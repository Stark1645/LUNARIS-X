"""
Master Registration Pipeline Orchestrator for SIH26166.
Executes the approved end-to-end scientific registration workflow:
Source + Reference -> Validation -> Preprocessing -> Multi-Scale -> Feature Detection ->
Matching -> Filtering -> Geometric Verification -> Inlier/Outlier Separation ->
Uniform Distribution -> Transformation Model Selection -> Transformation Estimation ->
Sub-Pixel Refinement -> Backward Warping -> Outputs & Evaluation.
"""

import time
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass

from src.preprocessing.normalizer import LunarPreprocessor
from src.multiscale.scale_bridge import MultiScaleBridge
from src.features.base import BaseFeatureDetector
from src.features.sift.sift_detector import SIFTDetector
from src.features.rift.rift_detector import RIFTDetector
from src.matching.matcher import FeatureMatcher, MatchResult
from src.geometry.models import TransformationType, TransformationEstimator
from src.geometry.verifier import RobustGeometricVerifier, GeometricVerificationResult
from src.distribution.spatial_filter import SpatialDistributionFilter
from src.refinement.subpixel import SubPixelRefiner
from src.evaluation.metrics import RegistrationMetrics, RegistrationEvaluator
from src.visualization.renderer import RegistrationVisualizer


@dataclass
class RegistrationOutput:
    """Complete structured output of the SIH26166 registration pipeline."""
    status: str  # SUCCESS | FAILED
    algorithm: str
    transformation_model: str
    
    # Warped / Registered Product
    warped_source_image: np.ndarray  # Source image aligned to reference frame
    reference_image: np.ndarray
    raw_source_image: np.ndarray
    
    # Transformation Matrix
    transformation_matrix: np.ndarray  # 3x3 matrix mapping Source -> Reference
    
    # Match Points & Distribution
    candidate_matches_count: int
    inlier_matches_count: int
    inlier_ratio_percent: float
    source_inlier_points: np.ndarray  # (N, 2)
    reference_inlier_points: np.ndarray  # (N, 2)
    source_outlier_points: np.ndarray  # (M, 2)
    reference_outlier_points: np.ndarray  # (M, 2)
    
    # Sub-Pixel Refinements
    subpixel_refined_points: np.ndarray  # (N, 2)
    subpixel_displacement_mags: np.ndarray
    
    # Scientific Metrics
    metrics: RegistrationMetrics
    
    # Visual Diagnostics
    match_visualization: np.ndarray
    alpha_overlay: np.ndarray
    checkerboard: np.ndarray
    difference_map: np.ndarray
    
    # Processing Log / Step Diagnostics
    step_diagnostics: Dict[str, Any]


class LunarRegistrationPipeline:
    """Orchestrates modular end-to-end lunar image registration."""

    def __init__(
        self,
        algorithm: str = "SIFT_Baseline",  # SIFT_Baseline | RIFT_Baseline
        transformation_model: TransformationType = TransformationType.HOMOGRAPHY,
        ratio_threshold: float = 0.80,
        ransac_threshold: float = 3.0,
        enable_subpixel: bool = True,
        enable_spatial_filter: bool = True,
        grid_bins: int = 4
    ):
        self.algorithm_name = algorithm
        self.preferred_model = transformation_model
        self.ratio_threshold = ratio_threshold
        self.ransac_threshold = ransac_threshold
        self.enable_subpixel = enable_subpixel
        self.enable_spatial_filter = enable_spatial_filter
        self.grid_bins = grid_bins

        # Initialize detector based on algorithm
        if algorithm == "RIFT_Baseline":
            self.detector: BaseFeatureDetector = RIFTDetector()
        else:
            self.detector = SIFTDetector()

        self.matcher = FeatureMatcher(ratio_threshold=ratio_threshold, cross_check=True)
        self.verifier = RobustGeometricVerifier(ransac_threshold=ransac_threshold)
        self.spatial_filter = SpatialDistributionFilter(grid_size=grid_bins)
        self.subpixel_refiner = SubPixelRefiner()
        self.scale_bridge = MultiScaleBridge()

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
        Executes end-to-end registration of Source (Moving) Image to Reference (Fixed) Image.
        """
        start_time = time.time()
        step_diag: Dict[str, Any] = {}

        # -------------------------------------------------------------
        # 1. IMAGE VALIDATION
        # -------------------------------------------------------------
        if source_image is None or reference_image is None:
            raise ValueError("Source or Reference image is None.")
        if source_image.size == 0 or reference_image.size == 0:
            raise ValueError("Source or Reference image is empty.")

        h_src, w_src = source_image.shape[:2]
        h_ref, w_ref = reference_image.shape[:2]
        step_diag["validation"] = {
            "source_dimensions": (w_src, h_src),
            "reference_dimensions": (w_ref, h_ref),
            "source_gsd_m": gsd_source_m,
            "reference_gsd_m": gsd_reference_m
        }

        # -------------------------------------------------------------
        # 2. PREPROCESSING
        # -------------------------------------------------------------
        src_norm, src_stats = LunarPreprocessor.normalize_radiometry(source_image)
        ref_norm, ref_stats = LunarPreprocessor.normalize_radiometry(reference_image)
        src_mask = LunarPreprocessor.create_valid_mask(src_norm)
        ref_mask = LunarPreprocessor.create_valid_mask(ref_norm)
        step_diag["preprocessing"] = {"source": src_stats, "reference": ref_stats}

        # -------------------------------------------------------------
        # 3. MULTI-SCALE REPRESENTATION
        # -------------------------------------------------------------
        scale_ratio = self.scale_bridge.estimate_scale_ratio(gsd_source_m, gsd_reference_m)
        step_diag["multiscale"] = {"estimated_scale_ratio": scale_ratio}

        # -------------------------------------------------------------
        # 4. FEATURE / CORRESPONDENCE DETECTION
        # -------------------------------------------------------------
        t_feat = time.time()
        kps_src, desc_src = self.detector.detect_and_compute(src_norm, src_mask)
        kps_ref, desc_ref = self.detector.detect_and_compute(ref_norm, ref_mask)
        step_diag["features"] = {
            "source_keypoints_count": len(kps_src),
            "reference_keypoints_count": len(kps_ref),
            "detection_time_ms": (time.time() - t_feat) * 1000.0
        }

        # -------------------------------------------------------------
        # 5. FEATURE MATCHING & 6. MATCH FILTERING
        # -------------------------------------------------------------
        match_res = self.matcher.match(kps_src, desc_src, kps_ref, desc_ref)
        step_diag["matching"] = {
            "raw_matches": match_res.raw_matches_count,
            "filtered_matches": match_res.filtered_matches_count
        }

        # -------------------------------------------------------------
        # 7. GEOMETRIC VERIFICATION & 8. INLIER / OUTLIER SEPARATION
        # -------------------------------------------------------------
        geom_res = self.verifier.verify(
            match_res.source_points,
            match_res.reference_points,
            preferred_model=self.preferred_model
        )
        step_diag["geometric_verification"] = {
            "is_valid": geom_res.is_valid,
            "inlier_count": geom_res.inlier_count,
            "outlier_count": geom_res.outlier_count,
            "inlier_ratio_percent": geom_res.inlier_ratio * 100.0,
            "mean_rmse_px": geom_res.mean_rmse
        }

        if not geom_res.is_valid or geom_res.inlier_count < 4:
            # Handle failure case gracefully
            latency = (time.time() - start_time) * 1000.0
            failed_metrics = RegistrationEvaluator.evaluate(
                src_inliers=np.empty((0, 2), dtype=np.float32),
                ref_inliers=np.empty((0, 2), dtype=np.float32),
                H_estimated=None,
                candidate_count=match_res.filtered_matches_count,
                algorithm_name=self.algorithm_name,
                transformation_model=self.preferred_model.value,
                image_shape=(h_ref, w_ref),
                H_ground_truth=ground_truth_homography,
                latency_ms=latency,
                is_synthetic=is_synthetic,
                dataset_category=dataset_category
            )

            empty_vis = np.zeros((h_ref, w_src + w_ref, 3), dtype=np.uint8)
            return RegistrationOutput(
                status="FAILED",
                algorithm=self.algorithm_name,
                transformation_model=self.preferred_model.value,
                warped_source_image=np.zeros_like(ref_norm),
                reference_image=ref_norm,
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
                alpha_overlay=ref_norm,
                checkerboard=ref_norm,
                difference_map=np.zeros_like(ref_norm),
                step_diagnostics=step_diag
            )

        # -------------------------------------------------------------
        # 9. UNIFORM DISTRIBUTION OF RELIABLE INLIERS
        # -------------------------------------------------------------
        inliers_src = geom_res.inlier_src_points
        inliers_ref = geom_res.inlier_ref_points

        if self.enable_spatial_filter and len(inliers_src) > 16:
            inliers_src, inliers_ref, dist_stats = self.spatial_filter.filter_inliers(
                inliers_src, inliers_ref, image_shape=(h_src, w_src)
            )
            step_diag["spatial_distribution"] = dist_stats
        else:
            step_diag["spatial_distribution"] = {"filter_applied": False}

        # -------------------------------------------------------------
        # 10. TRANSFORMATION MODEL SELECTION & 11. ESTIMATION
        # -------------------------------------------------------------
        H_final, model_stats = TransformationEstimator.estimate_model(
            inliers_src, inliers_ref, model_type=self.preferred_model
        )
        if H_final is None:
            H_final = geom_res.transformation_matrix
        step_diag["transformation"] = model_stats

        # -------------------------------------------------------------
        # 12. SUB-PIXEL REFINEMENT
        # -------------------------------------------------------------
        refined_ref_pts = inliers_ref
        disp_mags = np.zeros((len(inliers_ref),), dtype=np.float32)

        if self.enable_subpixel and len(inliers_src) > 0:
            refined_ref_pts, displacements, sub_stats = self.subpixel_refiner.refine_points(
                src_norm, ref_norm, inliers_src, inliers_ref
            )
            disp_mags = np.sqrt(np.sum(displacements ** 2, axis=1))
            step_diag["subpixel_refinement"] = sub_stats

            # Re-estimate transformation with sub-pixel refined coordinates
            H_sub, _ = TransformationEstimator.estimate_model(
                inliers_src, refined_ref_pts, model_type=self.preferred_model
            )
            if H_sub is not None:
                H_final = H_sub

        # -------------------------------------------------------------
        # 13. REGISTER SOURCE IMAGE TO REFERENCE FRAME (WARPING)
        # -------------------------------------------------------------
        warped_src = TransformationEstimator.warp_source_to_reference(
            src_norm,
            H_final,
            reference_shape=(h_ref, w_ref)
        )

        # -------------------------------------------------------------
        # 14. EVALUATION & METRICS CALCULATION
        # -------------------------------------------------------------
        latency = (time.time() - start_time) * 1000.0
        metrics = RegistrationEvaluator.evaluate(
            src_inliers=inliers_src,
            ref_inliers=refined_ref_pts,
            H_estimated=H_final,
            candidate_count=match_res.filtered_matches_count,
            algorithm_name=self.algorithm_name,
            transformation_model=self.preferred_model.value,
            image_shape=(h_ref, w_ref),
            H_ground_truth=ground_truth_homography,
            latency_ms=latency,
            is_synthetic=is_synthetic,
            dataset_category=dataset_category
        )

        # -------------------------------------------------------------
        # 15. VISUALIZATION & DIAGNOSTICS RENDERING
        # -------------------------------------------------------------
        match_vis = RegistrationVisualizer.draw_matches(
            src_norm, ref_norm,
            match_res.source_points,
            match_res.reference_points,
            inlier_mask=geom_res.inlier_mask
        )
        alpha_overlay = RegistrationVisualizer.draw_alpha_overlay(ref_norm, warped_src, alpha=0.5)
        checkerboard = RegistrationVisualizer.draw_checkerboard(ref_norm, warped_src, grid_tiles=8)
        diff_map = RegistrationVisualizer.draw_difference_map(ref_norm, warped_src)

        return RegistrationOutput(
            status="SUCCESS",
            algorithm=self.algorithm_name,
            transformation_model=self.preferred_model.value,
            warped_source_image=warped_src,
            reference_image=ref_norm,
            raw_source_image=src_norm,
            transformation_matrix=H_final,
            candidate_matches_count=match_res.filtered_matches_count,
            inlier_matches_count=len(inliers_src),
            inlier_ratio_percent=metrics.inlier_ratio_percent,
            source_inlier_points=inliers_src,
            reference_inlier_points=refined_ref_pts,
            source_outlier_points=geom_res.outlier_src_points,
            reference_outlier_points=geom_res.outlier_ref_points,
            subpixel_refined_points=refined_ref_pts,
            subpixel_displacement_mags=disp_mags,
            metrics=metrics,
            match_visualization=match_vis,
            alpha_overlay=alpha_overlay,
            checkerboard=checkerboard,
            difference_map=diff_map,
            step_diagnostics=step_diag
        )
