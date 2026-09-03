"""
Micro-benchmark Latency Profiler for SIH26166 AMSR Pipeline.
Measures stage-by-stage latency (in milliseconds) across representative challenge pairs.
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import json
import numpy as np

from src.preprocessing.normalizer import LunarPreprocessor
from src.proposed.condition_analyzer import ImagePairConditionAnalyzer
from src.matching.matcher import FeatureMatcher
from src.proposed.structural_detector import StructuralFeatureDetector
from src.proposed.spatial_ransac import SpatialCoverageAwareVerifier
from src.proposed.model_selector import DynamicModelSelector
from src.geometry.models import TransformationType
from src.refinement.subpixel import SubPixelRefiner

def profile_pair(src_path: Path, ref_path: Path, pair_name: str, src_gsd: float, ref_gsd: float):
    src_img = cv2.imread(str(src_path), cv2.IMREAD_GRAYSCALE)
    ref_img = cv2.imread(str(ref_path), cv2.IMREAD_GRAYSCALE)
    
    profiling = {}
    
    # 1. Preprocessing & Normalization
    t0 = time.time()
    src_norm, _ = LunarPreprocessor.normalize_radiometry(src_img)
    ref_norm, _ = LunarPreprocessor.normalize_radiometry(ref_img)
    src_mask = LunarPreprocessor.create_valid_mask(src_norm)
    ref_mask = LunarPreprocessor.create_valid_mask(ref_norm)
    profiling["1_preprocessing_ms"] = (time.time() - t0) * 1000
    
    # 2. Condition Analysis
    t0 = time.time()
    analyzer = ImagePairConditionAnalyzer()
    cond = analyzer.analyze(src_norm, ref_norm, src_gsd, ref_gsd)
    profiling["2_condition_analysis_ms"] = (time.time() - t0) * 1000
    
    # 3. Structural Feature Detection & Description
    t0 = time.time()
    detector = StructuralFeatureDetector(
        n_scales=4,
        n_orientations=6,
        suppress_shadow_edges=True
    )
    kps_src, desc_src = detector.detect_and_compute(src_norm, src_mask)
    kps_ref, desc_ref = detector.detect_and_compute(ref_norm, ref_mask)
    profiling["3_structural_detection_ms"] = (time.time() - t0) * 1000
    
    # 4. Feature Matching
    t0 = time.time()
    matcher = FeatureMatcher(ratio_threshold=0.80, cross_check=True)
    match_res = matcher.match(kps_src, desc_src, kps_ref, desc_ref)
    pts_src = match_res.source_points
    pts_ref = match_res.reference_points
    profiling["4_feature_matching_ms"] = (time.time() - t0) * 1000
    
    # 5. Spatial RANSAC
    t0 = time.time()
    verifier = SpatialCoverageAwareVerifier(
        ransac_threshold=3.0,
        max_iters=2000,
        max_allowed_gini=0.70
    )
    if len(pts_src) >= 4:
        v_res = verifier.verify(pts_src, pts_ref, src_norm.shape, preferred_model=TransformationType.HOMOGRAPHY)
        inliers_src = v_res.inlier_src_points
        inliers_ref = v_res.inlier_ref_points
    else:
        inliers_src, inliers_ref = np.empty((0, 2)), np.empty((0, 2))
    profiling["5_spatial_ransac_ms"] = (time.time() - t0) * 1000
    
    # 6. Dynamic Model Selection
    t0 = time.time()
    H_mat, model_type, info = DynamicModelSelector.select_and_estimate(inliers_src, inliers_ref, src_norm.shape)
    profiling["6_model_selection_ms"] = (time.time() - t0) * 1000
    
    # 7. Sub-Pixel Parabolic Hessian Refinement
    t0 = time.time()
    refiner = SubPixelRefiner(patch_radius=3)
    if len(inliers_src) > 0:
        refined_ref, displacements, stats = refiner.refine_points(src_norm, ref_norm, inliers_src, inliers_ref)
    profiling["7_subpixel_refinement_ms"] = (time.time() - t0) * 1000
    
    # 8. Backward Warping & Mosaic Compositing
    t0 = time.time()
    h, w = ref_norm.shape[:2]
    warped_img = cv2.warpPerspective(src_norm, H_mat, (w, h), flags=cv2.INTER_LINEAR)
    overlay = cv2.addWeighted(warped_img, 0.5, ref_norm, 0.5, 0)
    diff_map = cv2.absdiff(ref_norm, warped_img)
    profiling["8_warping_and_compositing_ms"] = (time.time() - t0) * 1000
    
    total_ms = sum(profiling.values())
    profiling["total_pipeline_ms"] = total_ms
    
    print(f"\n--- Profiling: {pair_name} ---")
    for k, v in profiling.items():
        print(f"  {k}: {v:.2f} ms")
    
    return profiling

def main():
    print("================================================================================")
    print(" AMSR STAGE-BY-STAGE LATENCY PROFILING ")
    print("================================================================================")
    
    p1_dir = Path("data/benchmark/suite_a_intra_sensor/pair_01_baseline_same_sun")
    profile_pair(p1_dir / "image_1.png", p1_dir / "image_2.png", "pair_01_baseline", 5.0, 5.0)
    
    p3_dir = Path("data/benchmark/suite_b_sun_angle/pair_03_sun_angle_180deg")
    profile_pair(p3_dir / "image_1.png", p3_dir / "image_2.png", "pair_03_sun_180deg", 5.0, 5.0)
    
    p4_dir = Path("data/benchmark/suite_c_scale_disparity/pair_04_scale_4x")
    profile_pair(p4_dir / "image_1.png", p4_dir / "image_2.png", "pair_04_scale_4x", 5.0, 1.25)

if __name__ == "__main__":
    main()
