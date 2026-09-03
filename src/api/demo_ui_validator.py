"""
Live Demonstration Dataset Validator for SIH 2026 (SIH26166).
Validates upload, processing, database persistence, and visual rendering
across all 6 demo pairs in data/demo/ through the live Spring Boot + Python ML API.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Tuple

BACKEND_URL = "http://localhost:8080/api/v1"
DEMO_DIR = Path("data/demo")

import mimetypes
import uuid

def http_post_multipart(url: str, file_path: Path, fields: dict):
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = bytearray()

    # Form fields
    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        body.extend(f"{v}\r\n".encode())

    # File field
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(f'Content-Disposition: form-data; name="file"; filename="{file_path.name}"\r\n'.encode())
    body.extend(f"Content-Type: {mime_type}\r\n\r\n".encode())
    with open(file_path, "rb") as f:
        body.extend(f.read())
    body.extend(b"\r\n")

    body.extend(f"--{boundary}--\r\n".encode())

    req = urllib.request.Request(
        url,
        data=bytes(body),
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Accept": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}

def http_post_json(url: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            res_data = json.loads(response.read().decode("utf-8"))
            return status_code, res_data
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}

def run_demo_pair(pair_name: str, src_gsd: float, ref_gsd: float, model: str = "HOMOGRAPHY") -> Dict[str, Any]:
    p_dir = DEMO_DIR / pair_name
    src_file = p_dir / "source.png"
    ref_file = p_dir / "reference.png"
    
    # 1. Upload Source Image
    code1, src_res = http_post_multipart(f"{BACKEND_URL}/images/upload", src_file, {
        "sensor_name": "TMC-2",
        "mission_name": "Chandrayaan-2",
        "gsd_meters": str(src_gsd),
        "data_category": "SYNTHETIC_BENCHMARK"
    })
    if code1 not in [200, 201]:
        raise RuntimeError(f"Failed to upload source image for {pair_name} (code {code1}): {src_res}")
    src_id = src_res["id"]
    
    # 2. Upload Reference Image
    code2, ref_res = http_post_multipart(f"{BACKEND_URL}/images/upload", ref_file, {
        "sensor_name": "TMC-2",
        "mission_name": "Chandrayaan-2",
        "gsd_meters": str(ref_gsd),
        "data_category": "SYNTHETIC_BENCHMARK"
    })
    if code2 not in [200, 201]:
        raise RuntimeError(f"Failed to upload reference image for {pair_name} (code {code2}): {ref_res}")
    ref_id = ref_res["id"]
    
    # 3. Execute Registration Job
    payload = {
        "sourceImageId": src_id,
        "referenceImageId": ref_id,
        "algorithm": "Proposed_Method",
        "transformationModel": model,
        "ratioThreshold": 0.80,
        "ransacThreshold": 3.0,
        "enableSubpixel": True,
        "enableSpatialFilter": True
    }
    
    t0 = time.time()
    code3, job_res = http_post_json(f"{BACKEND_URL}/jobs/register", payload)
    roundtrip_ms = (time.time() - t0) * 1000
    
    if code3 not in [200, 201]:
        raise RuntimeError(f"Failed to register {pair_name}: {job_res}")
        
    metrics = job_res.get("metrics", {})
    return {
        "pair_name": pair_name,
        "source_id": src_id,
        "reference_id": ref_id,
        "job_id": job_res.get("jobId") or job_res.get("id"),
        "status": job_res.get("status"),
        "selected_model": job_res.get("selectedTransformationModel"),
        "inliers": metrics.get("inlierMatchesCount"),
        "candidates": metrics.get("candidateMatchesCount"),
        "inlier_ratio_percent": metrics.get("inlierRatioPercent"),
        "inlier_rmse": metrics.get("rmseInliersPx"),
        "subpixel_residual": metrics.get("meanSubpixelResidualPx"),
        "spatial_gini": metrics.get("spatialGiniCoefficient"),
        "ml_latency_ms": metrics.get("latencyMs"),
        "roundtrip_ms": roundtrip_ms,
        "has_warped": bool(job_res.get("warpedImageBase64")),
        "has_overlay": bool(job_res.get("alphaOverlayBase64")),
        "has_checkerboard": bool(job_res.get("checkerboardBase64")),
        "has_diff": bool(job_res.get("differenceMapBase64")),
        "has_match_vis": bool(job_res.get("matchVisBase64"))
    }

def main():
    print("================================================================================")
    print(" SIH 2026 (SIH26166) DEMONSTRATION DATASET & REAL PIPELINE VALIDATION ")
    print("================================================================================")
    
    demo_cases = [
        {"name": "pair_01", "src_gsd": 5.0, "ref_gsd": 5.0, "model": "HOMOGRAPHY", "desc": "Baseline Intra-Sensor"},
        {"name": "pair_03", "src_gsd": 5.0, "ref_gsd": 5.0, "model": "HOMOGRAPHY", "desc": "180 deg Shadow Reversal"},
        {"name": "pair_04", "src_gsd": 5.0, "ref_gsd": 1.25, "model": "HOMOGRAPHY", "desc": "4x Scale Disparity"},
        {"name": "pair_06", "src_gsd": 5.0, "ref_gsd": 0.25, "model": "AFFINE", "desc": "20x Extreme Scale Gap"},
        {"name": "pair_07", "src_gsd": 5.0, "ref_gsd": 5.0, "model": "HOMOGRAPHY", "desc": "Cross-Modal SWIR to Pan"},
        {"name": "pair_08", "src_gsd": 5.0, "ref_gsd": 5.0, "model": "HOMOGRAPHY", "desc": "Low-Texture Maria"}
    ]
    
    results = []
    for c in demo_cases:
        p_name = c["name"]
        print(f"\nTesting Demo Pair: {p_name} ({c['desc']})...")
        try:
            res = run_demo_pair(p_name, c["src_gsd"], c["ref_gsd"], c["model"])
            print(f"  Job ID: {res['job_id']} | Status: {res['status']} | Model: {res['selected_model']}")
            print(f"  Inliers: {res['inliers']} / {res['candidates']} ({res['inlier_ratio_percent']:.1f}%) | Inlier RMSE: {res['inlier_rmse']:.2f} px")
            print(f"  Sub-Pixel Residual: {res['subpixel_residual']:.3f} px | Gini: {res['spatial_gini']:.2f} | Latency: {res['ml_latency_ms']:.1f} ms")
            print(f"  Visual Products -> Warped: {res['has_warped']}, Overlay: {res['has_overlay']}, Checkerboard: {res['has_checkerboard']}, Diff: {res['has_diff']}, Matches: {res['has_match_vis']}")
            results.append(res)
        except Exception as e:
            import traceback
            print(f"  [ERROR] {e}")
            traceback.print_exc()
            
    # Save live validation log
    out_file = Path("results/phase9_live_demo_validation.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[DONE] Saved Phase 9 live demo validation log to {out_file}")

if __name__ == "__main__":
    main()
