"""
Proposed Registration Pipeline (Adaptive Multi-Scale Structural Registration - AMSR).
Implements the scientifically validated proposed method addressing:
1. Illumination Invariance via Multi-Scale Phase Congruency & Shadow-Edge Suppression.
2. Scale Invariance via Hierarchical Scale-Pyramid Bridge (bridging 4x - 20x+ gaps).
3. Robust Spatial Coverage & Model Selection to prevent 4-point minimal sample traps.
4. Continuous 2D Parabolic Hessian Sub-Pixel Refinement.
"""

import time
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple

from src.preprocessing.normalizer import LunarPreprocessor
from src.features.sift.sift_detector import SIFTDetector
from src.proposed.condition_analyzer import ImagePairConditionAnalyzer, ImagePairCharacteristics
from src.proposed.structural_detector import StructuralFeatureDetector
from src.proposed.scale_pyramid_matcher import HierarchicalScalePyramidMatcher
from src.proposed.spatial_ransac import SpatialCoverageAwareVerifier
from src.proposed.model_selector import DynamicModelSelector
from src.distribution.spatial_filter import SpatialDistributionFilter
from src.refinement.subpixel import SubPixelRefiner
from src.geometry.models import TransformationType, TransformationEstimator
from src.evaluation.metrics import RegistrationMetrics, RegistrationEvaluator
from src.visualization.renderer import RegistrationVisualizer
from src.registration.pipeline import RegistrationOutput


class ProposedRegistrationPipeline:
    """Adaptive Multi-Scale Structural Registration Pipeline for SIH26166."""

    def __init__(
        self,
        algorithm_name: str = "Proposed_Method",
        enable_adaptive_strategy: bool = True,
        enable_scale_pyramid: bool = True,
        enable_shadow_suppression: bool = True,
        enable_spatial_filter: bool = True,
        enable_dynamic_model: bool = True,
        enable_subpixel: bool = True,
        ratio_threshold: float = 0.80,
        ransac_threshold: float = 3.0
    ):
        self.algorithm_name = algorithm_name
        self.enable_adaptive_strategy = enable_adaptive_strategy
        self.enable_scale_pyramid = enable_scale_pyramid
        self.enable_shadow_suppression = enable_shadow_suppression
        self.enable_spatial_filter = enable_spatial_filter
        self.enable_dynamic_model = enable_dynamic_model
        self.enable_subpixel = enable_subpixel
        self.ratio_threshold = ratio_threshold
        self.ransac_threshold = ransac_threshold

        # Core Detectors
        self.structural_detector = StructuralFeatureDetector(
            nfeatures=2500,
            suppress_shadow_edges=enable_shadow_suppression
        )
        self.sift_detector = SIFTDetector(nfeatures=2000)

        # Scale Bridge
        self.scale_matcher = HierarchicalScalePyramidMatcher(
            detector=self.structural_detector,
            ratio_threshold=ratio_threshold
        )
        self.scale_matcher_sift = HierarchicalScalePyramidMatcher(
            detector=self.sift_detector,
            ratio_threshold=ratio_threshold
        )

        # Verifier, Spatial Filter, and Subpixel Refiner
        self.verifier = SpatialCoverageAwareVerifier(ransac_threshold=ransac_threshold)
        self.spatial_filter = SpatialDistributionFilter(grid_size=4)
        self.subpixel_refiner = SubPixelRefiner()

    def register(
        self,
        source_image: np.ndarray,
        reference_image: np.ndarray,
        gsd_source_m: Optional[float] = None,
        gsd_reference_m: Optional[float] = None,
        ground_truth_homography: Optional[np.ndarray] = None,
        is_synthetic: bool = True,
        dataset_category: str = "SYNTHETIC_BENCHMARK"
    ) -> RegistrationOutput:
        """
        Executes end-to-end adaptive registration.
        """
        start_time = time.time()
        step_diag: Dict[str, Any] = {}

        # 1. Validation & Preprocessing
        src_norm, src_stats = LunarPreprocessor.normalize_radiometry(source_image)
        ref_norm, ref_stats = LunarPreprocessor.normalize_radiometry(reference_image)
        h_s, w_s = src_norm.shape[:2]
        h_r, w_r = ref_norm.shape[:2]

        # Multi-scale limit for ultra-large satellite strips (> 2048 px)
        max_dim = 2048
        raw_scale_s = min(1.0, float(max_dim) / float(max(h_s, w_s))) if max(h_s, w_s) > max_dim else 1.0
        raw_scale_r = min(1.0, float(max_dim) / float(max(h_r, w_r))) if max(h_r, w_r) > max_dim else 1.0

        # Physical GSD consistency check:
        # If both images have the same or similar GSD (e.g. crop vs strip of same instrument):
        # We must use isometric scaling (common scale) to preserve 1:1 pixel physical scale
        gsd_ratio = 1.0
        if gsd_source_m and gsd_reference_m and gsd_source_m > 0 and gsd_reference_m > 0:
            gsd_ratio = max(gsd_source_m / gsd_reference_m, gsd_reference_m / gsd_source_m)
        elif abs(w_s - w_r) / max(1.0, float(max(w_s, w_r))) < 0.25:
            gsd_ratio = 1.0

        if gsd_ratio < 1.5:
            common_scale = min(raw_scale_s, raw_scale_r)
            min_dim = min(h_s, w_s, h_r, w_r)
            if min_dim * common_scale < 128:
                common_scale = min(1.0, max(common_scale, 128.0 / min_dim))
            scale_s = common_scale
            scale_r = common_scale
        else:
            scale_s = raw_scale_s
            scale_r = raw_scale_r

        if scale_s < 1.0:
            src_proc = cv2.resize(src_norm, (int(round(w_s * scale_s)), int(round(h_s * scale_s))), interpolation=cv2.INTER_AREA)
        else:
            src_proc = src_norm

        if scale_r < 1.0:
            ref_proc = cv2.resize(ref_norm, (int(round(w_r * scale_r)), int(round(h_r * scale_r))), interpolation=cv2.INTER_AREA)
        else:
            ref_proc = ref_norm

        h_proc_s, w_proc_s = src_proc.shape[:2]
        h_proc_r, w_proc_r = ref_proc.shape[:2]

        step_diag["preprocessing"] = {"source": src_stats, "reference": ref_stats, "working_scale": {"scale_src": scale_s, "scale_ref": scale_r}}

        # 2. Condition Analysis (Innovation A)
        chars: ImagePairCharacteristics = ImagePairConditionAnalyzer.analyze(
            src_proc, ref_proc, gsd_source_m, gsd_reference_m
        )
        step_diag["condition_analysis"] = {
            "scale_ratio": chars.scale_ratio,
            "gradient_correlation": chars.gradient_correlation,
            "intensity_correlation": chars.intensity_correlation,
            "is_scale_disparate": chars.is_scale_disparate,
            "is_illumination_inverted": chars.is_illumination_inverted,
            "recommended_strategy": chars.recommended_feature_backend
        }

        # 3. Adaptive Feature Extraction & Scale-Pyramid Matching (Innovation A & B & C)
        t_match_start = time.time()
        
        # Decide matcher backend based on condition analysis
        if self.enable_adaptive_strategy and chars.is_scale_disparate and self.enable_scale_pyramid:
            # Scale disparate -> use multi-scale pyramid bridge with SIFT/Structural features
            match_res = self.scale_matcher_sift.match_scale_disparate_pair(
                src_proc, ref_proc, estimated_scale_ratio=chars.scale_ratio
            )
            # If SIFT pyramid matches are few, augment with structural scale matcher
            if match_res.filtered_matches_count < 10:
                match_res_struct = self.scale_matcher.match_scale_disparate_pair(
                    src_proc, ref_proc, estimated_scale_ratio=chars.scale_ratio
                )
                if match_res_struct.filtered_matches_count > match_res.filtered_matches_count:
                    match_res = match_res_struct

        elif self.enable_adaptive_strategy and chars.is_illumination_inverted:
            # Illumination inverted -> use Structural Phase Congruency
            if self.enable_scale_pyramid and chars.scale_ratio > 1.5:
                match_res = self.scale_matcher.match_scale_disparate_pair(
                    src_proc, ref_proc, estimated_scale_ratio=chars.scale_ratio
                )
            else:
                kps_src, desc_src = self.structural_detector.detect_and_compute(src_proc)
                kps_ref, desc_ref = self.structural_detector.detect_and_compute(ref_proc)
                match_res = self.scale_matcher.matcher.match(kps_src, desc_src, kps_ref, desc_ref)

        else:
            # Standard / Hybrid strategy
            if self.enable_scale_pyramid and chars.scale_ratio > 1.5:
                match_res = self.scale_matcher.match_scale_disparate_pair(
                    src_proc, ref_proc, estimated_scale_ratio=chars.scale_ratio
                )
            else:
                kps_src, desc_src = self.structural_detector.detect_and_compute(src_proc)
                kps_ref, desc_ref = self.structural_detector.detect_and_compute(ref_proc)
                match_res = self.scale_matcher.matcher.match(kps_src, desc_src, kps_ref, desc_ref)

        step_diag["matching"] = {
            "candidate_matches_count": match_res.filtered_matches_count,
            "matching_time_ms": (time.time() - t_match_start) * 1000.0
        }

        # 4. Spatial Coverage-Aware Verification (Innovation D)
        geom_res = self.verifier.verify(
            match_res.source_points,
            match_res.reference_points,
            image_shape=(h_proc_r, w_proc_r),
            preferred_model=TransformationType.HOMOGRAPHY
        )

        step_diag["geometric_verification"] = {
            "is_valid": geom_res.is_valid,
            "inlier_count": geom_res.inlier_count,
            "outlier_count": geom_res.outlier_count,
            "inlier_ratio_percent": geom_res.inlier_ratio * 100.0,
            "mean_rmse_px": geom_res.mean_rmse
        }

        # Multi-orientation recovery: check 90/180/270 deg rotation if initial verification failed
        if not geom_res.is_valid or geom_res.inlier_count < 4:
            for rot_angle in [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]:
                src_rot = cv2.rotate(src_proc, rot_angle)
                kps_rot, desc_rot = self.structural_detector.detect_and_compute(src_rot)
                kps_r, desc_r = self.structural_detector.detect_and_compute(ref_proc)
                m_rot = self.scale_matcher.matcher.match(kps_rot, desc_rot, kps_r, desc_r)
                if m_rot.filtered_matches_count >= 6:
                    g_rot = self.verifier.verify(
                        m_rot.source_points,
                        m_rot.reference_points,
                        image_shape=(h_proc_r, w_proc_r),
                        preferred_model=TransformationType.HOMOGRAPHY
                    )
                    if g_rot.is_valid and g_rot.inlier_count >= 4:
                        geom_res = g_rot
                        match_res = m_rot
                        src_proc = src_rot
                        h_proc_s, w_proc_s = src_proc.shape[:2]
                        break

        if not geom_res.is_valid or geom_res.inlier_count < 4:
            # Handle failure gracefully
            latency = (time.time() - start_time) * 1000.0
            failed_metrics = RegistrationEvaluator.evaluate(
                src_inliers=np.empty((0, 2), dtype=np.float32),
                ref_inliers=np.empty((0, 2), dtype=np.float32),
                H_estimated=None,
                candidate_count=match_res.filtered_matches_count,
                algorithm_name=self.algorithm_name,
                transformation_model="NONE",
                image_shape=(h_proc_r, w_proc_r),
                H_ground_truth=ground_truth_homography,
                latency_ms=latency,
                is_synthetic=is_synthetic,
                dataset_category=dataset_category
            )

            empty_vis = RegistrationVisualizer.draw_matches(
                src_proc, ref_proc,
                match_res.source_points,
                match_res.reference_points,
                inlier_mask=geom_res.inlier_mask
            )

            return RegistrationOutput(
                status="FAILED",
                algorithm=self.algorithm_name,
                transformation_model="NONE",
                warped_source_image=src_proc,
                reference_image=ref_proc,
                raw_source_image=src_norm,
                transformation_matrix=np.eye(3, dtype=np.float64),
                candidate_matches_count=match_res.filtered_matches_count,
                inlier_matches_count=0,
                inlier_ratio_percent=0.0,
                source_inlier_points=np.empty((0, 2), dtype=np.float32),
                reference_inlier_points=np.empty((0, 2), dtype=np.float32),
                source_outlier_points=match_res.source_points,
                reference_outlier_points=match_res.reference_points,
                subpixel_refined_points=np.empty((0, 2), dtype=np.float32),
                subpixel_displacement_mags=np.empty((0,), dtype=np.float32),
                metrics=failed_metrics,
                match_visualization=empty_vis,
                alpha_overlay=ref_proc,
                checkerboard=ref_proc,
                difference_map=np.zeros_like(ref_proc),
                panoramic_mosaic=RegistrationVisualizer.draw_panoramic_mosaic(ref_proc, src_proc, None),
                step_diagnostics=step_diag
            )

        # 5. Spatial Coverage Filter (Innovation D)
        inliers_src = geom_res.inlier_src_points
        inliers_ref = geom_res.inlier_ref_points

        if self.enable_spatial_filter and len(inliers_src) > 16:
            inliers_src, inliers_ref, dist_stats = self.spatial_filter.filter_inliers(
                inliers_src, inliers_ref, image_shape=(h_proc_s, w_proc_s)
            )
            step_diag["spatial_distribution"] = dist_stats
        else:
            step_diag["spatial_distribution"] = {"filter_applied": False}

        # 6. Dynamic Transformation Model Selection (Innovation E)
        if self.enable_dynamic_model:
            H_final, model_type, model_stats = DynamicModelSelector.select_and_estimate(
                inliers_src, inliers_ref, image_shape=(h_proc_s, w_proc_s)
            )
        else:
            H_final, model_stats = TransformationEstimator.estimate_model(
                inliers_src, inliers_ref, TransformationType.HOMOGRAPHY
            )
            model_type = TransformationType.HOMOGRAPHY

        step_diag["transformation_model_selection"] = {
            "selected_model": model_type.value,
            "stats": model_stats
        }

        # 7. Sub-Pixel Refinement (Innovation F)
        refined_ref = inliers_ref
        disp_mags = np.zeros((len(inliers_ref),), dtype=np.float32)

        if self.enable_subpixel and len(inliers_src) > 0:
            refined_ref, displacements, sub_stats = self.subpixel_refiner.refine_points(
                src_proc, ref_proc, inliers_src, inliers_ref
            )
            disp_mags = np.sqrt(np.sum(displacements ** 2, axis=1))
            step_diag["subpixel_refinement"] = sub_stats

            # Re-estimate with refined points
            H_refined, _, _ = DynamicModelSelector.select_and_estimate(
                inliers_src, refined_ref, image_shape=(h_proc_s, w_proc_s), force_model=model_type
            )
            if H_refined is not None:
                H_final = H_refined

        # 8. Backward Image Warping at working scale
        warped_src = TransformationEstimator.warp_source_to_reference(
            src_proc, H_final, reference_shape=(h_proc_r, w_proc_r)
        )

        # 9. Metric Calculation
        spatial_quality = dist_stats.get("spatial_quality_status", "ACCEPTABLE") if self.enable_spatial_filter and len(geom_res.inlier_src_points) > 16 else "ACCEPTABLE"
        latency = (time.time() - start_time) * 1000.0
        metrics = RegistrationEvaluator.evaluate(
            src_inliers=inliers_src,
            ref_inliers=refined_ref,
            H_estimated=H_final,
            candidate_count=match_res.filtered_matches_count,
            algorithm_name=self.algorithm_name,
            transformation_model=model_type.value,
            image_shape=(h_proc_r, w_proc_r),
            H_ground_truth=ground_truth_homography,
            latency_ms=latency,
            is_synthetic=is_synthetic,
            dataset_category=dataset_category,
            spatial_quality_status=spatial_quality
        )

        # 10. Visualization Rendering
        match_vis = RegistrationVisualizer.draw_matches(
            src_proc, ref_proc,
            match_res.source_points,
            match_res.reference_points,
            inlier_mask=geom_res.inlier_mask
        )
        alpha_overlay = RegistrationVisualizer.draw_alpha_overlay(ref_proc, warped_src, alpha=0.5)
        checkerboard = RegistrationVisualizer.draw_checkerboard(ref_proc, warped_src, grid_tiles=8)
        diff_map = RegistrationVisualizer.draw_difference_map(ref_proc, warped_src)
        panoramic_mosaic = RegistrationVisualizer.draw_panoramic_mosaic(ref_proc, src_proc, H_final)

        # 11. Re-project transformation matrix and inliers to native coordinate frame
        if scale_s < 1.0 or scale_r < 1.0:
            S_s = np.diag([scale_s, scale_s, 1.0])
            inv_S_r = np.diag([1.0 / scale_r, 1.0 / scale_r, 1.0])
            H_native = inv_S_r @ H_final @ S_s

            inliers_src_native = (inliers_src / scale_s).astype(np.float32)
            refined_ref_native = (refined_ref / scale_r).astype(np.float32)
            outliers_src_native = (geom_res.outlier_src_points / scale_s).astype(np.float32) if len(geom_res.outlier_src_points) > 0 else geom_res.outlier_src_points
            outliers_ref_native = (geom_res.outlier_ref_points / scale_r).astype(np.float32) if len(geom_res.outlier_ref_points) > 0 else geom_res.outlier_ref_points
        else:
            H_native = H_final
            inliers_src_native = inliers_src
            refined_ref_native = refined_ref
            outliers_src_native = geom_res.outlier_src_points
            outliers_ref_native = geom_res.outlier_ref_points

        return RegistrationOutput(
            status="SUCCESS",
            algorithm=self.algorithm_name,
            transformation_model=model_type.value,
            warped_source_image=warped_src,
            reference_image=ref_proc,
            raw_source_image=src_norm,
            transformation_matrix=H_native,
            candidate_matches_count=match_res.filtered_matches_count,
            inlier_matches_count=len(inliers_src),
            inlier_ratio_percent=metrics.inlier_ratio_percent,
            source_inlier_points=inliers_src_native,
            reference_inlier_points=refined_ref_native,
            source_outlier_points=outliers_src_native,
            reference_outlier_points=outliers_ref_native,
            subpixel_refined_points=refined_ref_native,
            subpixel_displacement_mags=disp_mags,
            metrics=metrics,
            match_visualization=match_vis,
            alpha_overlay=alpha_overlay,
            checkerboard=checkerboard,
            difference_map=diff_map,
            panoramic_mosaic=panoramic_mosaic,
            step_diagnostics=step_diag
        )
