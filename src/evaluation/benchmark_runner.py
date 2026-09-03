"""
Reproducible Benchmark Runner for SIH26166 (Phase 2 Baseline Evaluation).
Executes SIFT and RIFT baselines across all benchmark suites in data/benchmark/.
Extracts exact measured metrics (RMSE, Inliers, Inlier Ratio, Sub-pixel Error, Gini G_k, Latency),
saves registered outputs, difference maps, match visualizations, and preserves failure diagnostics.
"""

import os
import sys
import glob
import json
import time
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import asdict

from src.registration.pipeline import LunarRegistrationPipeline, RegistrationOutput
from src.geometry.models import TransformationType
from src.evaluation.metrics import RegistrationMetrics


class BenchmarkRunner:
    """Automates execution and metric collection across standardized benchmark suites."""

    def __init__(
        self,
        benchmark_root: str = "data/benchmark",
        output_root: str = "results/baseline_evaluation"
    ):
        self.benchmark_root = benchmark_root
        self.output_root = output_root

    def discover_pairs(self) -> List[Dict[str, Any]]:
        """Scans benchmark directory for all test pair directories."""
        suite_dirs = sorted(glob.glob(os.path.join(self.benchmark_root, "suite_*")))
        pairs = []

        for sdir in suite_dirs:
            suite_name = os.path.basename(sdir)
            pair_dirs = sorted(glob.glob(os.path.join(sdir, "pair_*")))
            for pdir in pair_dirs:
                pair_name = os.path.basename(pdir)
                img1_path = os.path.join(pdir, "image_1.png")
                img2_path = os.path.join(pdir, "image_2.png")
                gt_path = os.path.join(pdir, "ground_truth.json")
                prov_path = os.path.join(pdir, "provenance.json")

                if os.path.exists(img1_path) and os.path.exists(img2_path):
                    pairs.append({
                        "suite_name": suite_name,
                        "pair_name": pair_name,
                        "pair_dir": pdir,
                        "img1_path": img1_path,
                        "img2_path": img2_path,
                        "gt_path": gt_path if os.path.exists(gt_path) else None,
                        "prov_path": prov_path if os.path.exists(prov_path) else None
                    })

        return pairs

    def run_pair(
        self,
        pair_info: Dict[str, Any],
        algorithm: str,
        transformation_model: TransformationType = TransformationType.HOMOGRAPHY
    ) -> Dict[str, Any]:
        """Runs registration pipeline on a single pair with the specified algorithm."""
        # 1. Load images
        img1 = cv2.imread(pair_info["img1_path"], cv2.IMREAD_UNCHANGED)
        img2 = cv2.imread(pair_info["img2_path"], cv2.IMREAD_UNCHANGED)

        # 2. Load ground truth metadata if present
        H_gt = None
        scale_ratio = 1.0
        delta_sun_azimuth = 0.0
        is_synthetic = True
        data_category = "SYNTHETIC_BENCHMARK"

        if pair_info["gt_path"]:
            with open(pair_info["gt_path"], "r", encoding="utf-8") as f:
                gt_data = json.load(f)
                if "ground_truth_homography" in gt_data:
                    H_gt = np.array(gt_data["ground_truth_homography"], dtype=np.float64)
                scale_ratio = float(gt_data.get("scale_ratio", 1.0))
                delta_sun_azimuth = float(gt_data.get("delta_sun_azimuth_deg", 0.0))
                is_synthetic = bool(gt_data.get("is_synthetic", True))
                data_category = gt_data.get("data_category", "SYNTHETIC_BENCHMARK")

        # 3. Instantiate and run pipeline
        pipeline = LunarRegistrationPipeline(
            algorithm=algorithm,
            transformation_model=transformation_model,
            ratio_threshold=0.80,
            ransac_threshold=3.0,
            enable_subpixel=True,
            enable_spatial_filter=True
        )

        output: RegistrationOutput = pipeline.register(
            source_image=img1,
            reference_image=img2,
            ground_truth_homography=H_gt,
            is_synthetic=is_synthetic,
            dataset_category=data_category
        )

        # 4. Save visual and data artifacts
        pair_out_dir = os.path.join(
            self.output_root,
            data_category.lower(),
            pair_info["suite_name"],
            pair_info["pair_name"],
            algorithm.lower()
        )
        os.makedirs(pair_out_dir, exist_ok=True)

        # Save images
        cv2.imwrite(os.path.join(pair_out_dir, "warped_source.png"), output.warped_source_image)
        cv2.imwrite(os.path.join(pair_out_dir, "match_visualization.png"), output.match_visualization)
        cv2.imwrite(os.path.join(pair_out_dir, "alpha_overlay.png"), output.alpha_overlay)
        cv2.imwrite(os.path.join(pair_out_dir, "checkerboard.png"), output.checkerboard)
        cv2.imwrite(os.path.join(pair_out_dir, "difference_map.png"), output.difference_map)

        # Save match points CSV
        pts_file = os.path.join(pair_out_dir, "inlier_match_points.csv")
        with open(pts_file, "w", encoding="utf-8") as f:
            f.write("source_x,source_y,ref_x,ref_y\n")
            for i in range(len(output.source_inlier_points)):
                sx, sy = output.source_inlier_points[i]
                rx, ry = output.reference_inlier_points[i]
                f.write(f"{sx:.4f},{sy:.4f},{rx:.4f},{ry:.4f}\n")

        # Compile full result record
        m = output.metrics
        record = {
            "pair_name": pair_info["pair_name"],
            "suite_name": pair_info["suite_name"],
            "algorithm": algorithm,
            "transformation_model": transformation_model.value,
            "status": output.status,
            "data_category": data_category,
            "is_synthetic": is_synthetic,
            "scale_ratio": scale_ratio,
            "delta_sun_azimuth_deg": delta_sun_azimuth,
            "metrics": {
                "inlier_match_count": m.inlier_match_count,
                "candidate_matches_count": output.candidate_matches_count,
                "inlier_ratio_percent": float(m.inlier_ratio_percent),
                "rmse_inliers_px": float(m.rmse_inliers) if m.rmse_inliers != float("inf") else None,
                "rmse_ground_truth_px": float(m.rmse_ground_truth) if m.rmse_ground_truth is not None else None,
                "mean_subpixel_residual_px": float(m.mean_subpixel_residual) if m.mean_subpixel_residual != float("inf") else None,
                "subpixel_accuracy_rate_05px": float(m.subpixel_accuracy_rate_05px),
                "spatial_gini_coefficient": float(m.spatial_gini_coefficient),
                "latency_ms": float(m.latency_ms)
            },
            "step_diagnostics": output.step_diagnostics,
            "artifacts_dir": pair_out_dir
        }

        # Save JSON result
        with open(os.path.join(pair_out_dir, "result.json"), "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

        return record

    def run_all_baselines(self) -> Dict[str, Any]:
        """Executes full benchmark evaluation across SIFT and RIFT baselines."""
        pairs = self.discover_pairs()
        print(f"Discovered {len(pairs)} benchmark test pairs across {self.benchmark_root}")

        algorithms = ["SIFT_Baseline", "RIFT_Baseline"]
        results = {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_pairs": len(pairs),
            "algorithms_evaluated": algorithms,
            "runs": []
        }

        for p_idx, pair in enumerate(pairs, start=1):
            print(f"\n[{p_idx}/{len(pairs)}] Evaluating: {pair['suite_name']} / {pair['pair_name']}")
            for algo in algorithms:
                t0 = time.time()
                res = self.run_pair(pair, algorithm=algo)
                elapsed = time.time() - t0
                m = res["metrics"]
                status_symbol = "SUCCESS" if res["status"] == "SUCCESS" else "FAILED"
                print(f"  -> {algo:<15} [{status_symbol}] Inliers: {m['inlier_match_count']:<4} Ratio: {m['inlier_ratio_percent']:>5.1f}% | RMSE: {m['rmse_inliers_px'] if m['rmse_inliers_px'] is not None else 'N/A':<6} | Gini: {m['spatial_gini_coefficient']:.2f} | Time: {elapsed:.2f}s")
                results["runs"].append(res)

        # Save aggregated summary
        os.makedirs(self.output_root, exist_ok=True)
        summary_path = os.path.join(self.output_root, "benchmark_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\nBenchmark execution complete. Aggregated summary saved to: {summary_path}")
        return results


def main():
    runner = BenchmarkRunner(
        benchmark_root="data/benchmark",
        output_root="results/baseline_evaluation"
    )
    runner.run_all_baselines()


if __name__ == "__main__":
    main()
