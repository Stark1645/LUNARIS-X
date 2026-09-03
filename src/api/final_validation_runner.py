"""
Phase 8 Final Scientific Validation & Multi-Algorithm Performance Benchmarking Runner.
Evaluates SIFT Baseline, RIFT Baseline, and AMSR Proposed Engine across all 9 benchmark pairs.
Profiles stage-by-stage latencies, exports high-resolution visual evidence, and generates empirical logs.
"""

import json
import time
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import cv2
import numpy as np
from typing import Dict, Any, List

from src.features.sift.sift_detector import SIFTDetector
from src.features.rift.rift_detector import RIFTDetector
from src.registration.pipeline import LunarRegistrationPipeline, RegistrationOutput
from src.proposed.proposed_pipeline import ProposedRegistrationPipeline
from src.geometry.models import TransformationType
from src.evaluation.metrics import RegistrationMetrics

DATA_DIR = Path("data/benchmark")
OUTPUT_DIR = Path("results/final_validation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

BENCHMARK_PAIRS = [
    {
        "suite": "suite_a_intra_sensor",
        "pair_name": "pair_01_baseline_same_sun",
        "dir": DATA_DIR / "suite_a_intra_sensor" / "pair_01_baseline_same_sun",
        "src_gsd": 5.0,
        "ref_gsd": 5.0,
        "condition": "Baseline intra-sensor, identical illumination and scale"
    },
    {
        "suite": "suite_b_sun_angle",
        "pair_name": "pair_02_sun_angle_90deg",
        "dir": DATA_DIR / "suite_b_sun_angle" / "pair_02_sun_angle_90deg",
        "src_gsd": 5.0,
        "ref_gsd": 5.0,
        "condition": "90° orthogonal solar azimuth disparity"
    },
    {
        "suite": "suite_b_sun_angle",
        "pair_name": "pair_03_sun_angle_180deg",
        "dir": DATA_DIR / "suite_b_sun_angle" / "pair_03_sun_angle_180deg",
        "src_gsd": 5.0,
        "ref_gsd": 5.0,
        "condition": "180° solar azimuth reversal with inverted shadow boundaries"
    },
    {
        "suite": "suite_c_scale_disparity",
        "pair_name": "pair_04_scale_4x",
        "dir": DATA_DIR / "suite_c_scale_disparity" / "pair_04_scale_4x",
        "src_gsd": 5.0,
        "ref_gsd": 1.25,
        "condition": "4× scale disparity (moderate resolution transition)"
    },
    {
        "suite": "suite_c_scale_disparity",
        "pair_name": "pair_05_scale_16x_tmc2_ohrc",
        "dir": DATA_DIR / "suite_c_scale_disparity" / "pair_05_scale_16x_tmc2_ohrc",
        "src_gsd": 5.0,
        "ref_gsd": 0.3125,
        "condition": "16× high scale disparity (TMC-2 to near-OHRC resolution)"
    },
    {
        "suite": "suite_c_scale_disparity",
        "pair_name": "pair_06_scale_20x_tmc2_ohrc",
        "dir": DATA_DIR / "suite_c_scale_disparity" / "pair_06_scale_20x_tmc2_ohrc",
        "src_gsd": 5.0,
        "ref_gsd": 0.25,
        "condition": "20× extreme scale disparity (TMC-2 5m to OHRC 0.25m)"
    },
    {
        "suite": "suite_d_cross_modal",
        "pair_name": "pair_07_cross_modal_swir_pan",
        "dir": DATA_DIR / "suite_d_cross_modal" / "pair_07_cross_modal_swir_pan",
        "src_gsd": 5.0,
        "ref_gsd": 5.0,
        "condition": "Cross-modal non-linear radiometric transfer (SWIR simulated)"
    },
    {
        "suite": "suite_e_difficult_terrain",
        "pair_name": "pair_08_low_texture_maria",
        "dir": DATA_DIR / "suite_e_difficult_terrain" / "pair_08_low_texture_maria",
        "src_gsd": 5.0,
        "ref_gsd": 5.0,
        "condition": "Low-texture basaltic lunar maria terrain"
    },
    {
        "suite": "suite_e_difficult_terrain",
        "pair_name": "pair_09_dense_crater_highlands",
        "dir": DATA_DIR / "suite_e_difficult_terrain" / "pair_09_dense_crater_highlands",
        "src_gsd": 5.0,
        "ref_gsd": 5.0,
        "condition": "High-density cratered lunar highlands"
    }
]

def classify_registration(inliers: int, ir_percent: float, inlier_rmse: float, gini: float, gt_rmse: float = None) -> str:
    """
    Applies the experimental classification criteria:
    SUCCESS: Inliers >= 12, Inlier RMSE <= 2.5 px, Gini G_k <= 0.65 (or stable Homography with low RMSE_GT <= 5.0 px)
    DEGRADED: Usable correspondences (4 <= Inliers < 12, or partial violation of SUCCESS criteria)
    FAILED: Inliers < 4 or Inlier Ratio = 0%
    """
    if inliers < 4 or ir_percent == 0.0:
        return "FAILED"
    
    # Check if meets strict SUCCESS criteria
    if inliers >= 12 and inlier_rmse <= 2.5:
        if gini <= 0.65:
            return "SUCCESS"
        elif gt_rmse is not None and gt_rmse <= 5.0:
            return "SUCCESS" # Verified by ground truth despite localized crater rim cluster
        else:
            return "DEGRADED" # High cluster Gini with unverified GT
    
    return "DEGRADED"

def run_sift_pair(src_img: np.ndarray, ref_img: np.ndarray, H_gt: np.ndarray = None) -> Dict[str, Any]:
    pipeline = LunarRegistrationPipeline(algorithm="SIFT", transformation_model=TransformationType.HOMOGRAPHY)
    t0 = time.time()
    out = pipeline.register(src_img, ref_img)
    total_latency_ms = (time.time() - t0) * 1000
    
    # Calculate GT RMSE if available
    gt_rmse = None
    if H_gt is not None and out.status != "FAILED" and out.transformation_matrix is not None:
        try:
            H_est = out.transformation_matrix
            h, w = src_img.shape[:2]
            corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
            pts_gt = cv2.perspectiveTransform(corners, H_gt)
            pts_est = cv2.perspectiveTransform(corners, H_est)
            gt_rmse = float(np.sqrt(np.mean((pts_gt - pts_est) ** 2)))
        except Exception:
            gt_rmse = None

    status = classify_registration(
        out.inlier_matches_count,
        out.inlier_ratio_percent,
        out.metrics.rmse_inliers,
        out.metrics.spatial_gini_coefficient,
        gt_rmse
    )

    return {
        "algorithm": "SIFT_Baseline",
        "inliers": out.inlier_matches_count,
        "candidate_matches": out.candidate_matches_count,
        "inlier_ratio_percent": float(out.inlier_ratio_percent),
        "inlier_rmse": float(out.metrics.rmse_inliers),
        "gt_rmse": gt_rmse,
        "subpixel_residual": float(out.metrics.mean_subpixel_residual),
        "spatial_gini": float(out.metrics.spatial_gini_coefficient),
        "latency_ms": float(total_latency_ms),
        "transformation_model": out.transformation_model,
        "status": status,
        "output": out
    }

def run_rift_pair(src_img: np.ndarray, ref_img: np.ndarray, H_gt: np.ndarray = None) -> Dict[str, Any]:
    pipeline = LunarRegistrationPipeline(algorithm="RIFT", transformation_model=TransformationType.HOMOGRAPHY)
    t0 = time.time()
    out = pipeline.register(src_img, ref_img)
    total_latency_ms = (time.time() - t0) * 1000
    
    gt_rmse = None
    if H_gt is not None and out.status != "FAILED" and out.transformation_matrix is not None:
        try:
            H_est = out.transformation_matrix
            h, w = src_img.shape[:2]
            corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
            pts_gt = cv2.perspectiveTransform(corners, H_gt)
            pts_est = cv2.perspectiveTransform(corners, H_est)
            gt_rmse = float(np.sqrt(np.mean((pts_gt - pts_est) ** 2)))
        except Exception:
            gt_rmse = None

    status = classify_registration(
        out.inlier_matches_count,
        out.inlier_ratio_percent,
        out.metrics.rmse_inliers,
        out.metrics.spatial_gini_coefficient,
        gt_rmse
    )

    return {
        "algorithm": "RIFT_Baseline",
        "inliers": out.inlier_matches_count,
        "candidate_matches": out.candidate_matches_count,
        "inlier_ratio_percent": float(out.inlier_ratio_percent),
        "inlier_rmse": float(out.metrics.rmse_inliers),
        "gt_rmse": gt_rmse,
        "subpixel_residual": float(out.metrics.mean_subpixel_residual),
        "spatial_gini": float(out.metrics.spatial_gini_coefficient),
        "latency_ms": float(total_latency_ms),
        "transformation_model": out.transformation_model,
        "status": status,
        "output": out
    }

def run_amsr_pair(src_img: np.ndarray, ref_img: np.ndarray, src_gsd: float, ref_gsd: float, H_gt: np.ndarray = None) -> Dict[str, Any]:
    pipeline = ProposedRegistrationPipeline(
        algorithm_name="Proposed_AMSR",
        enable_adaptive_strategy=True,
        enable_scale_pyramid=True,
        enable_shadow_suppression=True,
        enable_spatial_filter=True,
        enable_dynamic_model=True,
        enable_subpixel=True,
        ratio_threshold=0.80,
        ransac_threshold=3.0
    )
    
    t0 = time.time()
    out = pipeline.register(src_img, ref_img, gsd_source_m=src_gsd, gsd_reference_m=ref_gsd)
    total_latency_ms = (time.time() - t0) * 1000
    
    gt_rmse = None
    if H_gt is not None and out.status != "FAILED" and out.transformation_matrix is not None:
        try:
            H_est = out.transformation_matrix
            h, w = src_img.shape[:2]
            corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
            pts_gt = cv2.perspectiveTransform(corners, H_gt)
            pts_est = cv2.perspectiveTransform(corners, H_est)
            gt_rmse = float(np.sqrt(np.mean((pts_gt - pts_est) ** 2)))
        except Exception:
            gt_rmse = None

    status = classify_registration(
        out.inlier_matches_count,
        out.inlier_ratio_percent,
        out.metrics.rmse_inliers,
        out.metrics.spatial_gini_coefficient,
        gt_rmse
    )

    return {
        "algorithm": "Proposed_AMSR",
        "inliers": out.inlier_matches_count,
        "candidate_matches": out.candidate_matches_count,
        "inlier_ratio_percent": float(out.inlier_ratio_percent),
        "inlier_rmse": float(out.metrics.rmse_inliers),
        "gt_rmse": gt_rmse,
        "subpixel_residual": float(out.metrics.mean_subpixel_residual),
        "spatial_gini": float(out.metrics.spatial_gini_coefficient),
        "latency_ms": float(total_latency_ms),
        "transformation_model": out.transformation_model,
        "status": status,
        "output": out
    }

def main():
    print("==========================================================================================")
    print(" SIH26166 PHASE 8: COMPREHENSIVE FINAL VALIDATION & BENCHMARKING ENGINE ")
    print("==========================================================================================")
    
    all_results = []
    
    for item in BENCHMARK_PAIRS:
        pair_name = item["pair_name"]
        p_dir = item["dir"]
        print(f"\nEvaluating Benchmark Pair: {pair_name} ({item['condition']})...")
        
        src_path = p_dir / "image_1.png"
        ref_path = p_dir / "image_2.png"
        gt_path = p_dir / "ground_truth.json"
        
        src_img = cv2.imread(str(src_path), cv2.IMREAD_GRAYSCALE)
        ref_img = cv2.imread(str(ref_path), cv2.IMREAD_GRAYSCALE)
        
        H_gt = None
        if gt_path.exists():
            with open(gt_path, "r") as f:
                gt_data = json.load(f)
                if "homography_matrix" in gt_data:
                    H_gt = np.array(gt_data["homography_matrix"], dtype=np.float64)
                elif "ground_truth_matrix" in gt_data:
                    H_gt = np.array(gt_data["ground_truth_matrix"], dtype=np.float64)
        
        # 1. Run SIFT
        res_sift = run_sift_pair(src_img, ref_img, H_gt)
        print(f"  [SIFT] Inliers: {res_sift['inliers']} | Inlier RMSE: {res_sift['inlier_rmse']:.2f} px | GT RMSE: {res_sift['gt_rmse']} | Gini: {res_sift['spatial_gini']:.2f} | Latency: {res_sift['latency_ms']:.1f} ms | Status: {res_sift['status']}")
        
        # 2. Run RIFT
        res_rift = run_rift_pair(src_img, ref_img, H_gt)
        print(f"  [RIFT] Inliers: {res_rift['inliers']} | Inlier RMSE: {res_rift['inlier_rmse']:.2f} px | GT RMSE: {res_rift['gt_rmse']} | Gini: {res_rift['spatial_gini']:.2f} | Latency: {res_rift['latency_ms']:.1f} ms | Status: {res_rift['status']}")
        
        # 3. Run Proposed AMSR
        res_amsr = run_amsr_pair(src_img, ref_img, item["src_gsd"], item["ref_gsd"], H_gt)
        print(f"  [AMSR] Inliers: {res_amsr['inliers']} | Inlier RMSE: {res_amsr['inlier_rmse']:.2f} px | GT RMSE: {res_amsr['gt_rmse']} | Gini: {res_amsr['spatial_gini']:.2f} | Latency: {res_amsr['latency_ms']:.1f} ms | Status: {res_amsr['status']}")
        
        # Save Visual Outputs for AMSR
        pair_out_dir = OUTPUT_DIR / pair_name
        pair_out_dir.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(pair_out_dir / "warped_source.png"), res_amsr["output"].warped_source_image)
        cv2.imwrite(str(pair_out_dir / "alpha_overlay.png"), res_amsr["output"].alpha_overlay)
        cv2.imwrite(str(pair_out_dir / "checkerboard.png"), res_amsr["output"].checkerboard)
        cv2.imwrite(str(pair_out_dir / "difference_map.png"), res_amsr["output"].difference_map)
        cv2.imwrite(str(pair_out_dir / "match_visualization.png"), res_amsr["output"].match_visualization)
        
        # Record JSON metrics
        pair_record = {
            "suite": item["suite"],
            "pair_name": pair_name,
            "condition": item["condition"],
            "src_gsd": item["src_gsd"],
            "ref_gsd": item["ref_gsd"],
            "sift": {k: v for k, v in res_sift.items() if k != "output"},
            "rift": {k: v for k, v in res_rift.items() if k != "output"},
            "amsr": {k: v for k, v in res_amsr.items() if k != "output"}
        }
        all_results.append(pair_record)
        
    # Save full final JSON record
    final_json_path = OUTPUT_DIR / "final_benchmark_results.json"
    with open(final_json_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSuccessfully written full benchmark log to {final_json_path}")

if __name__ == "__main__":
    main()
