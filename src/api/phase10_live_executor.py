"""
Phase 10: Final Live UI & Multi-Tier Pipeline Validator.
Executes live end-to-end registration on all 6 demo pairs through the active Spring Boot API,
verifies all visual products (base64 decode and integrity), checks database persistence,
and runs negative API tests.
"""

import os
import sys
import json
import time
import base64
import mimetypes
import uuid
import urllib.request
import urllib.error
from io import BytesIO
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image

BACKEND_URL = "http://localhost:8080/api/v1"
DEMO_DIR = Path("data/demo")
OUTPUT_DIR = Path("results/phase10_live_validation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def http_post_multipart(url: str, file_path: Path, fields: dict) -> Tuple[int, Dict[str, Any]]:
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    body = bytearray()

    for k, v in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        body.extend(f"{v}\r\n".encode())

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
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}

def http_post_json(url: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}

def http_get_json(url: str) -> Tuple[int, Dict[str, Any]]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}

def validate_base64_image(b64_str: str, name: str) -> Dict[str, Any]:
    if not b64_str:
        return {"valid": False, "error": "Empty or null Base64 string"}
    
    # Strip data URL prefix if present
    raw_b64 = b64_str
    if "," in b64_str:
        raw_b64 = b64_str.split(",", 1)[1]
        
    try:
        data = base64.b64decode(raw_b64)
        img = Image.open(BytesIO(data))
        w, h = img.size
        is_blank = False
        # Verify non-zero dimensions
        if w == 0 or h == 0:
            return {"valid": False, "error": "Zero dimensions"}
        return {
            "valid": True,
            "format": img.format,
            "dimensions": (w, h),
            "size_bytes": len(data)
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}

def execute_demo_pair(pair_name: str, src_gsd: float, ref_gsd: float, requested_model: str = "HOMOGRAPHY") -> Dict[str, Any]:
    p_dir = DEMO_DIR / pair_name
    src_path = p_dir / "source.png"
    ref_path = p_dir / "reference.png"
    
    print(f"\n>>> Running Live End-to-End Test for [{pair_name}] <<<")
    
    # 1. Upload Source Image
    code_src, src_resp = http_post_multipart(f"{BACKEND_URL}/images/upload", src_path, {
        "sensor_name": "TMC-2",
        "mission_name": "CHANDRAYAAN-2",
        "gsd_meters": str(src_gsd),
        "data_category": "SYNTHETIC_BENCHMARK"
    })
    assert code_src in [200, 201], f"Source upload failed: {src_resp}"
    src_id = src_resp["id"]
    print(f"  Source Uploaded -> ID: {src_id} | SHA-256: {src_resp.get('sha256Checksum')[:16]}... | Dims: {src_resp.get('width')}x{src_resp.get('height')}")

    # 2. Upload Reference Image
    code_ref, ref_resp = http_post_multipart(f"{BACKEND_URL}/images/upload", ref_path, {
        "sensor_name": "OHRC" if "06" in pair_name else "TMC-2",
        "mission_name": "CHANDRAYAAN-2",
        "gsd_meters": str(ref_gsd),
        "data_category": "SYNTHETIC_BENCHMARK"
    })
    assert code_ref in [200, 201], f"Reference upload failed: {ref_resp}"
    ref_id = ref_resp["id"]
    print(f"  Reference Uploaded -> ID: {ref_id} | SHA-256: {ref_resp.get('sha256Checksum')[:16]}... | Dims: {ref_resp.get('width')}x{ref_resp.get('height')}")

    # 3. Submit Registration Job
    payload = {
        "sourceImageId": src_id,
        "referenceImageId": ref_id,
        "algorithm": "Proposed_Method",
        "transformationModel": requested_model,
        "ratioThreshold": 0.80,
        "ransacThreshold": 3.0,
        "enableSubpixel": True,
        "enableSpatialFilter": True
    }
    
    t0 = time.time()
    code_job, job_resp = http_post_json(f"{BACKEND_URL}/jobs/register", payload)
    total_http_ms = (time.time() - t0) * 1000
    assert code_job == 200, f"Registration failed with code {code_job}: {job_resp}"
    
    job_id = job_resp.get("jobId") or job_resp.get("id")
    status = job_resp.get("status")
    selected_model = job_resp.get("selectedTransformationModel")
    matrix_json = job_resp.get("transformationMatrixJson")
    metrics = job_resp.get("metrics", {})
    
    # 4. Validate Visual Products
    warped_val = validate_base64_image(job_resp.get("warpedImageBase64"), "warped")
    overlay_val = validate_base64_image(job_resp.get("alphaOverlayBase64"), "overlay")
    checkerboard_val = validate_base64_image(job_resp.get("checkerboardBase64"), "checkerboard")
    diff_val = validate_base64_image(job_resp.get("differenceMapBase64"), "diff")
    matches_val = validate_base64_image(job_resp.get("matchVisBase64"), "matches")
    
    # Save visual products to output dir
    p_out = OUTPUT_DIR / pair_name
    p_out.mkdir(parents=True, exist_ok=True)
    for name, b64_str in [
        ("warped_source.png", job_resp.get("warpedImageBase64")),
        ("alpha_overlay.png", job_resp.get("alphaOverlayBase64")),
        ("checkerboard.png", job_resp.get("checkerboardBase64")),
        ("difference_map.png", job_resp.get("differenceMapBase64")),
        ("matches.png", job_resp.get("matchVisBase64"))
    ]:
        if b64_str:
            raw = b64_str.split(",", 1)[1] if "," in b64_str else b64_str
            with open(p_out / name, "wb") as f:
                f.write(base64.b64decode(raw))

    # 5. Verify Database Retrieval
    code_get, db_job = http_get_json(f"{BACKEND_URL}/jobs/{job_id}")
    assert code_get == 200, f"Database job retrieval failed for job {job_id}"
    db_metrics = db_job.get("metrics", {})
    
    result_summary = {
        "pair_name": pair_name,
        "job_id": job_id,
        "status": status,
        "selected_model": selected_model,
        "candidate_matches": metrics.get("candidateMatchesCount"),
        "inlier_matches": metrics.get("inlierMatchesCount"),
        "inlier_ratio_percent": metrics.get("inlierRatioPercent"),
        "inlier_rmse_px": metrics.get("rmseInliersPx"),
        "gt_rmse_px": metrics.get("rmseGroundTruthPx"),
        "subpixel_residual_px": metrics.get("meanSubpixelResidualPx"),
        "spatial_gini": metrics.get("spatialGiniCoefficient"),
        "ml_latency_ms": metrics.get("latencyMs"),
        "total_roundtrip_ms": total_http_ms,
        "matrix_json": matrix_json,
        "visual_validation": {
            "warped": warped_val,
            "overlay": overlay_val,
            "checkerboard": checkerboard_val,
            "diff_map": diff_val,
            "match_visualization": matches_val
        },
        "db_verified": (db_job.get("status") == status and db_metrics.get("inlierMatchesCount") == metrics.get("inlierMatchesCount"))
    }
    
    print(f"  Job ID: {job_id} | Status: {status} | Model: {selected_model}")
    print(f"  Inliers: {result_summary['inlier_matches']} / {result_summary['candidate_matches']} ({result_summary['inlier_ratio_percent']}%) | RMSE: {result_summary['inlier_rmse_px']} px")
    print(f"  Subpixel: {result_summary['subpixel_residual_px']} px | Gini: {result_summary['spatial_gini']} | Latency: {result_summary['ml_latency_ms']} ms")
    print(f"  Visual Products Valid: Warped={warped_val['valid']}, Overlay={overlay_val['valid']}, Checkerboard={checkerboard_val['valid']}, Diff={diff_val['valid']}, Matches={matches_val['valid']}")
    print(f"  Database Row Verified via GET /jobs/{job_id}: {result_summary['db_verified']}")
    
    return result_summary

def run_negative_tests() -> Dict[str, Any]:
    print("\n>>> Running Negative API Tests <<<")
    neg_results = {}
    
    # 1. Unsupported extension (.exe)
    dummy_exe = OUTPUT_DIR / "dummy_malicious.exe"
    with open(dummy_exe, "wb") as f:
        f.write(b"MZ dummy executable payload")
    
    code_ext, resp_ext = http_post_multipart(f"{BACKEND_URL}/images/upload", dummy_exe, {
        "sensor_name": "TMC-2",
        "data_category": "SYNTHETIC_BENCHMARK"
    })
    neg_results["unsupported_extension"] = {
        "expected_code": 400,
        "actual_code": code_ext,
        "passed": (code_ext == 400),
        "response": resp_ext
    }
    print(f"  [Negative 1] Upload .exe -> HTTP {code_ext} (Expected 400) | Passed: {code_ext == 400}")
    
    # 2. Missing sourceImageId
    code_missing, resp_missing = http_post_json(f"{BACKEND_URL}/jobs/register", {
        "sourceImageId": None,
        "referenceImageId": 1,
        "algorithm": "Proposed_Method"
    })
    neg_results["missing_source_id"] = {
        "expected_code": 400,
        "actual_code": code_missing,
        "passed": (code_missing == 400),
        "response": resp_missing
    }
    print(f"  [Negative 2] Register with null sourceImageId -> HTTP {code_missing} (Expected 400) | Passed: {code_missing == 400}")

    # 3. Nonexistent Job ID
    code_404, resp_404 = http_get_json(f"{BACKEND_URL}/jobs/999999")
    neg_results["nonexistent_job_id"] = {
        "expected_code": 404,
        "actual_code": code_404,
        "passed": (code_404 == 404),
        "response": resp_404
    }
    print(f"  [Negative 3] Query nonexistent Job 999999 -> HTTP {code_404} (Expected 404) | Passed: {code_404 == 404}")

    return neg_results

def main():
    print("================================================================================")
    print(" PHASE 10: FULL-STACK LIVE UI VALIDATION & AUDIT RUNNER ")
    print("================================================================================")
    
    test_cases = [
        {"name": "pair_01", "src_gsd": 5.0, "ref_gsd": 5.0, "model": "HOMOGRAPHY"},
        {"name": "pair_03", "src_gsd": 5.0, "ref_gsd": 5.0, "model": "HOMOGRAPHY"},
        {"name": "pair_04", "src_gsd": 5.0, "ref_gsd": 1.25, "model": "HOMOGRAPHY"},
        {"name": "pair_06", "src_gsd": 5.0, "ref_gsd": 0.25, "model": "AFFINE"},
        {"name": "pair_07", "src_gsd": 5.0, "ref_gsd": 5.0, "model": "HOMOGRAPHY"},
        {"name": "pair_08", "src_gsd": 5.0, "ref_gsd": 5.0, "model": "HOMOGRAPHY"}
    ]
    
    pair_results = []
    for tc in test_cases:
        res = execute_demo_pair(tc["name"], tc["src_gsd"], tc["ref_gsd"], tc["model"])
        pair_results.append(res)
        
    neg_results = run_negative_tests()
    
    final_output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "live_demo_results": pair_results,
        "negative_test_results": neg_results
    }
    
    out_file = OUTPUT_DIR / "phase10_live_verification_report.json"
    with open(out_file, "w") as f:
        json.dump(final_output, f, indent=2)
    print(f"\n[DONE] Saved Phase 10 validation report to {out_file}")

if __name__ == "__main__":
    main()
