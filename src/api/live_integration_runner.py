"""
Live Integration & Scientific Verification Runner for SIH26166.
Uses Python standard library (urllib.request / json) for 100% zero-dependency execution.
Tests: Client -> Spring Boot (:8080) -> Python ML (:8000) -> MySQL (:3306) -> Persistence.
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path
import mimetypes
import uuid

BACKEND_URL = "http://localhost:8080/api/v1"
DATA_DIR = Path("data/benchmark")

def http_get(url: str):
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

def http_post_json(url: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
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
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {"error": body}


def test_health():
    print("\n--- 1. Testing Distributed Health Endpoint ---")
    status, data = http_get(f"{BACKEND_URL}/health")
    assert status == 200, f"Health check failed: {status}"
    print("Health Status Response:", json.dumps(data, indent=2))
    assert data["status"] == "UP"
    assert data["pythonServiceStatus"] == "UP"
    assert data["databaseStatus"] == "UP"
    print("[PASS] Health Check Passed.")
    return data


def upload_image(file_path: Path, sensor_name: str, gsd: float, category: str = "SYNTHETIC_BENCHMARK"):
    fields = {
        "sensor_name": sensor_name,
        "mission_name": "CHANDRAYAAN-2",
        "gsd_meters": str(gsd),
        "data_category": category
    }
    status, img_data = http_post_multipart(f"{BACKEND_URL}/images/upload", file_path, fields)
    assert status == 201, f"Image upload failed ({status}): {img_data}"
    print(f"  Uploaded {file_path.name} -> Image ID: {img_data['id']}, SHA-256: {img_data['sha256Checksum'][:16]}...")
    return img_data


def register_pair(src_path: Path, ref_path: Path, pair_name: str, src_gsd: float, ref_gsd: float, algo: str = "Proposed_Method"):
    print(f"\n--- Running End-to-End Registration: {pair_name} ({algo}) ---")

    # 1. Upload Source (Moving Image)
    src_meta = upload_image(src_path, "TMC-2", src_gsd)

    # 2. Upload Reference (Fixed Image)
    ref_meta = upload_image(ref_path, "OHRC", ref_gsd)

    # 3. Create and Execute Registration Job
    payload = {
        "sourceImageId": src_meta["id"],
        "referenceImageId": ref_meta["id"],
        "algorithm": algo,
        "transformationModel": "HOMOGRAPHY",
        "ratioThreshold": 0.80,
        "ransacThreshold": 3.0,
        "enableSubpixel": True,
        "enableSpatialFilter": True
    }

    t0 = time.time()
    status, job_data = http_post_json(f"{BACKEND_URL}/jobs/register", payload)
    elapsed_total = (time.time() - t0) * 1000

    assert status == 200, f"Registration failed ({status}): {job_data}"

    print(f"  Job ID: {job_data['jobId']}")
    print(f"  Status: {job_data['status']}")
    print(f"  Algorithm: {job_data['algorithm']}")
    print(f"  Selected Model: {job_data['selectedTransformationModel']}")

    m = job_data["metrics"]
    print(f"  Inlier Matches: {m['inlierMatchesCount']} / {m['candidateMatchesCount']} (Ratio: {m['inlierRatioPercent']:.1f}%)")
    print(f"  Inlier RMSE: {m['rmseInliersPx']:.2f} px")
    print(f"  GT RMSE: {m['rmseGroundTruthPx']} px" if m['rmseGroundTruthPx'] is not None else "  GT RMSE: N/A")
    print(f"  Sub-Pixel Residual: {m['meanSubpixelResidualPx']:.3f} px")
    print(f"  Spatial Gini (G_k): {m['spatialGiniCoefficient']:.2f}")
    print(f"  ML Latency: {m['latencyMs']:.1f} ms (Total HTTP Roundtrip: {elapsed_total:.1f} ms)")

    # Verify Visual Products
    has_warped = bool(job_data.get("warpedImageBase64"))
    has_overlay = bool(job_data.get("alphaOverlayBase64"))
    has_checker = bool(job_data.get("checkerboardBase64"))
    has_diff = bool(job_data.get("differenceMapBase64"))
    has_matches = bool(job_data.get("matchVisBase64"))
    print(f"  Visual Products -> Warped: {has_warped}, Overlay: {has_overlay}, Checkerboard: {has_checker}, Diff: {has_diff}, Matches: {has_matches}")

    # 4. Verify Database Persistence by re-querying GET /api/v1/jobs/{id}
    get_status, persisted_job = http_get(f"{BACKEND_URL}/jobs/{job_data['jobId']}")
    assert get_status == 200, f"Failed to retrieve persisted job: {get_status}"
    assert persisted_job["status"] == job_data["status"]
    assert persisted_job["metrics"]["inlierMatchesCount"] == m["inlierMatchesCount"]
    print("  [PASS] Database Persistence Verified via GET /jobs/{id}.")

    return job_data


def test_error_paths():
    print("\n--- Testing Error-Path Handling ---")

    # Test 1: Missing sourceImageId (Bean validation)
    bad_req = {"referenceImageId": 1, "algorithm": "Proposed_Method"}
    status, res = http_post_json(f"{BACKEND_URL}/jobs/register", bad_req)
    print(f"  Register with missing sourceImageId -> HTTP {status} ({res.get('error', res)})")
    assert status == 400

    # Test 2: Non-existent job ID
    status, res = http_get(f"{BACKEND_URL}/jobs/999999")
    print(f"  Get non-existent job ID (999999) -> HTTP {status} ({res.get('error', res)})")
    assert status == 404

    print("[PASS] All Error Paths Handled Safely.")


def main():
    print("================================================================================")
    print(" SIH 2026 (SIH26166) FULL-STACK LIVE INTEGRATION & SCIENTIFIC VERIFICATION ")
    print("================================================================================")

    test_health()

    results = {}

    # Case A: pair_03 (180 deg illumination / shadow inversion)
    p3_dir = DATA_DIR / "suite_b_sun_angle" / "pair_03_sun_angle_180deg"
    results["pair_03"] = register_pair(
        src_path=p3_dir / "image_1.png",
        ref_path=p3_dir / "image_2.png",
        pair_name="pair_03 (180 deg Shadow Reversal)",
        src_gsd=5.0,
        ref_gsd=5.0,
        algo="Proposed_Method"
    )

    # Case B: pair_04 (4x scale disparity)
    p4_dir = DATA_DIR / "suite_c_scale_disparity" / "pair_04_scale_4x"
    results["pair_04"] = register_pair(
        src_path=p4_dir / "image_1.png",
        ref_path=p4_dir / "image_2.png",
        pair_name="pair_04 (4x Scale Disparity)",
        src_gsd=5.0,
        ref_gsd=1.25,
        algo="Proposed_Method"
    )

    # Case C: pair_06 (20x scale disparity)
    p6_dir = DATA_DIR / "suite_c_scale_disparity" / "pair_06_scale_20x_tmc2_ohrc"
    results["pair_06"] = register_pair(
        src_path=p6_dir / "image_1.png",
        ref_path=p6_dir / "image_2.png",
        pair_name="pair_06 (20x Scale Disparity TMC-2 to OHRC)",
        src_gsd=5.0,
        ref_gsd=0.25,
        algo="Proposed_Method"
    )

    test_error_paths()

    print("\n================================================================================")
    print(" LIVE INTEGRATION RUN SUMMARY ")
    print("================================================================================")
    for pair_id, res in results.items():
        m = res["metrics"]
        print(f"[{pair_id.upper()}] Status: {res['status']} | Inliers: {m['inlierMatchesCount']} (IR: {m['inlierRatioPercent']:.1f}%) | Inlier RMSE: {m['rmseInliersPx']:.2f} px | GT RMSE: {m['rmseGroundTruthPx']} px | Gini: {m['spatialGiniCoefficient']:.2f} | Latency: {m['latencyMs']:.0f} ms")

    # Save live verification log
    out_file = Path("results/phase7_live_verification_results.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved live verification results to {out_file}")


if __name__ == "__main__":
    main()
