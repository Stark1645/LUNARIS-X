import json
from pathlib import Path

source_path = Path("results/proposed_method/phase4_evaluation_summary.json")
if not source_path.exists():
    print(f"Error: {source_path} does not exist")
    exit(1)

data = json.loads(source_path.read_text(encoding="utf-8"))
records = data["records"]
dto_list = []

for idx, r in enumerate(records):
    m = r.get("metrics", {})
    cfg = r.get("config_name", "")
    if "Proposed" in cfg:
        algo = "Proposed_AMSR"
    elif "SIFT" in cfg:
        algo = "SIFT_Baseline"
    elif "RIFT" in cfg:
        algo = "RIFT_Baseline"
    else:
        algo = "Ablation_Study"

    dto = {
        "id": idx + 1,
        "experimentId": f"EXP-{idx+1:03d}",
        "suiteName": r.get("suite_name"),
        "pairName": r.get("pair_name"),
        "algorithm": algo,
        "configurationName": cfg,
        "dataCategory": "SYNTHETIC_BENCHMARK",
        "scaleRatio": r.get("scale_ratio"),
        "deltaSunAzimuthDeg": r.get("delta_sun_azimuth_deg"),
        "inlierCount": m.get("inlier_match_count", 0),
        "inlierRatioPercent": m.get("inlier_ratio_percent", 0.0),
        "rmseInliersPx": m.get("rmse_inliers_px"),
        "rmseGroundTruthPx": m.get("rmse_ground_truth_px"),
        "spatialGini": m.get("spatial_gini"),
        "latencyMs": m.get("latency_ms", 0.0),
        "status": r.get("status", "SUCCESS"),
        "executedAt": data.get("timestamp_utc", "2026-09-02T14:13:16Z"),
    }
    dto_list.append(dto)

dest_dir = Path("frontend/src/data")
dest_dir.mkdir(parents=True, exist_ok=True)
dest_file = dest_dir / "curatedBenchmarks.ts"

content = (
    'import { ExperimentDTO } from "../types";\n\n'
    + "export const CURATED_BENCHMARKS: ExperimentDTO[] = "
    + json.dumps(dto_list, indent=2)
    + ";\n"
)
dest_file.write_text(content, encoding="utf-8")
print(f"Generated {len(dto_list)} benchmark records in {dest_file}")
