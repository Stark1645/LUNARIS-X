"""
Phase 4 Proposed Method & Ablation Experiment Runner.
Executes Proposed Pipeline and 5 Ablation Configurations across all benchmark suites.
Records exact measured metrics (Inliers, Inlier Ratio, Inlier RMSE, Ground-Truth RMSE, Sub-Pixel Error, Gini G_k, Latency).
"""

import os
import json
import time
import glob
import cv2
import numpy as np
from typing import Dict, Any, List

from src.proposed.proposed_pipeline import ProposedRegistrationPipeline
from src.features.sift.sift_detector import SIFTDetector
from src.features.rift.rift_detector import RIFTDetector
from src.registration.pipeline import LunarRegistrationPipeline


class ProposedMethodEvaluator:
    """Evaluates the Proposed Method and runs comprehensive ablation studies."""

    def __init__(
        self,
        benchmark_root: str = "data/benchmark",
        output_root: str = "results/proposed_method"
    ):
        self.benchmark_root = benchmark_root
        self.output_root = output_root

    def discover_pairs(self) -> List[Dict[str, Any]]:
        suite_dirs = sorted(glob.glob(os.path.join(self.benchmark_root, "suite_*")))
        pairs = []
        for sdir in suite_dirs:
            suite_name = os.path.basename(sdir)
            pair_dirs = sorted(glob.glob(os.path.join(sdir, "pair_*")))
            for pdir in pair_dirs:
                img1_path = os.path.join(pdir, "image_1.png")
                img2_path = os.path.join(pdir, "image_2.png")
                gt_path = os.path.join(pdir, "ground_truth.json")
                if os.path.exists(img1_path) and os.path.exists(img2_path):
                    pairs.append({
                        "suite_name": suite_name,
                        "pair_name": os.path.basename(pdir),
                        "pair_dir": pdir,
                        "img1_path": img1_path,
                        "img2_path": img2_path,
                        "gt_path": gt_path if os.path.exists(gt_path) else None
                    })
        return pairs

    def evaluate_all(self) -> Dict[str, Any]:
        pairs = self.discover_pairs()
        print(f"Loaded {len(pairs)} benchmark test pairs.")

        configurations = {
            "SIFT_Baseline": {"type": "BASELINE_SIFT"},
            "RIFT_Baseline": {"type": "BASELINE_RIFT"},
            "Proposed_Full": {
                "type": "PROPOSED",
                "enable_scale_pyramid": True,
                "enable_shadow_suppression": True,
                "enable_dynamic_model": True,
                "enable_subpixel": True
            },
            "Ablation_No_Scale_Pyramid": {
                "type": "PROPOSED",
                "enable_scale_pyramid": False,
                "enable_shadow_suppression": True,
                "enable_dynamic_model": True,
                "enable_subpixel": True
            },
            "Ablation_No_Shadow_Suppression": {
                "type": "PROPOSED",
                "enable_scale_pyramid": True,
                "enable_shadow_suppression": False,
                "enable_dynamic_model": True,
                "enable_subpixel": True
            },
            "Ablation_No_Dynamic_Model": {
                "type": "PROPOSED",
                "enable_scale_pyramid": True,
                "enable_shadow_suppression": True,
                "enable_dynamic_model": False,
                "enable_subpixel": True
            },
            "Ablation_No_Subpixel": {
                "type": "PROPOSED",
                "enable_scale_pyramid": True,
                "enable_shadow_suppression": True,
                "enable_dynamic_model": True,
                "enable_subpixel": False
            }
        }

        results = {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "total_pairs": len(pairs),
            "configurations": list(configurations.keys()),
            "records": []
        }

        for p_idx, pair in enumerate(pairs, start=1):
            print(f"\n=======================================================")
            print(f"[{p_idx}/{len(pairs)}] Testing Pair: {pair['suite_name']} / {pair['pair_name']}")
            print(f"=======================================================")

            img1 = cv2.imread(pair["img1_path"], cv2.IMREAD_UNCHANGED)
            img2 = cv2.imread(pair["img2_path"], cv2.IMREAD_UNCHANGED)

            H_gt = None
            scale_ratio = 1.0
            delta_sun = 0.0
            data_cat = "SYNTHETIC_BENCHMARK"
            is_syn = True

            if pair["gt_path"]:
                with open(pair["gt_path"], "r", encoding="utf-8") as f:
                    gt_data = json.load(f)
                    H_gt = np.array(gt_data["ground_truth_homography"], dtype=np.float64) if "ground_truth_homography" in gt_data else None
                    scale_ratio = float(gt_data.get("scale_ratio", 1.0))
                    delta_sun = float(gt_data.get("delta_sun_azimuth_deg", 0.0))

            for config_name, cfg in configurations.items():
                if cfg["type"] == "BASELINE_SIFT":
                    pipe = LunarRegistrationPipeline(algorithm="SIFT_Baseline")
                    out = pipe.register(img1, img2, ground_truth_homography=H_gt, is_synthetic=is_syn, dataset_category=data_cat)
                elif cfg["type"] == "BASELINE_RIFT":
                    pipe = LunarRegistrationPipeline(algorithm="RIFT_Baseline")
                    out = pipe.register(img1, img2, ground_truth_homography=H_gt, is_synthetic=is_syn, dataset_category=data_cat)
                else:
                    pipe = ProposedRegistrationPipeline(
                        algorithm_name=config_name,
                        enable_scale_pyramid=cfg["enable_scale_pyramid"],
                        enable_shadow_suppression=cfg["enable_shadow_suppression"],
                        enable_dynamic_model=cfg["enable_dynamic_model"],
                        enable_subpixel=cfg["enable_subpixel"]
                    )
                    out = pipe.register(img1, img2, ground_truth_homography=H_gt, is_synthetic=is_syn, dataset_category=data_cat)

                m = out.metrics
                rec = {
                    "suite_name": pair["suite_name"],
                    "pair_name": pair["pair_name"],
                    "config_name": config_name,
                    "status": out.status,
                    "transformation_model": out.transformation_model,
                    "scale_ratio": scale_ratio,
                    "delta_sun_azimuth_deg": delta_sun,
                    "metrics": {
                        "inlier_match_count": m.inlier_match_count,
                        "candidate_matches_count": out.candidate_matches_count,
                        "inlier_ratio_percent": float(m.inlier_ratio_percent),
                        "rmse_inliers_px": float(m.rmse_inliers) if m.rmse_inliers != float("inf") else None,
                        "rmse_ground_truth_px": float(m.rmse_ground_truth) if m.rmse_ground_truth is not None else None,
                        "mean_subpixel_residual_px": float(m.mean_subpixel_residual) if m.mean_subpixel_residual != float("inf") else None,
                        "spatial_gini": float(m.spatial_gini_coefficient),
                        "latency_ms": float(m.latency_ms)
                    }
                }
                results["records"].append(rec)

                # Save output artifacts for Proposed_Full
                if config_name == "Proposed_Full":
                    out_dir = os.path.join(self.output_root, pair["suite_name"], pair["pair_name"])
                    os.makedirs(out_dir, exist_ok=True)
                    cv2.imwrite(os.path.join(out_dir, "warped_source.png"), out.warped_source_image)
                    cv2.imwrite(os.path.join(out_dir, "match_visualization.png"), out.match_visualization)
                    cv2.imwrite(os.path.join(out_dir, "alpha_overlay.png"), out.alpha_overlay)
                    cv2.imwrite(os.path.join(out_dir, "checkerboard.png"), out.checkerboard)
                    cv2.imwrite(os.path.join(out_dir, "difference_map.png"), out.difference_map)

                gt_rmse_str = f"{m.rmse_ground_truth:.2f}" if m.rmse_ground_truth is not None else "N/A"
                print(f"  [{config_name:<30}] Inliers: {m.inlier_match_count:<4} Ratio: {m.inlier_ratio_percent:>5.1f}% | RMSE_Inlier: {m.rmse_inliers:<5.2f} | RMSE_GT: {gt_rmse_str:<6} | Model: {out.transformation_model:<10} | Gini: {m.spatial_gini_coefficient:.2f}")

        # Save summary JSON
        os.makedirs(self.output_root, exist_ok=True)
        sum_path = os.path.join(self.output_root, "phase4_evaluation_summary.json")
        with open(sum_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\nAll Phase 4 experiments and ablations completed. Summary saved to: {sum_path}")
        return results


def main():
    evaluator = ProposedMethodEvaluator()
    evaluator.evaluate_all()


if __name__ == "__main__":
    main()
