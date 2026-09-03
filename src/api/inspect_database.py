"""
Database rows and consistency inspector for SIH26166.
Checks MySQL tables: images, registration_jobs, registration_metrics, and match_points.
"""

import urllib.request
import json

BACKEND_URL = "http://localhost:8080/api/v1"

def main():
    print("================================================================================")
    print(" DATABASE ENTITY & ROW INTEGRITY AUDIT ")
    print("================================================================================")
    
    # 1. Images
    try:
        req = urllib.request.Request(f"{BACKEND_URL}/images")
        with urllib.request.urlopen(req) as resp:
            images = json.loads(resp.read().decode())
            print(f"Images Table: {len(images)} total images persisted.")
            for img in images[-5:]:
                print(f"  ID: {img['id']} | File: {img['filename']} | Sensor: {img['sensorName']} | SHA-256: {img['sha256Checksum'][:16]}... | Path: {img['storagePath']}")
    except Exception as e:
        print(f"Error reading images: {e}")

    # 2. Registration Jobs & Metrics
    for j_id in [28, 29, 30, 31, 32, 33]:
        try:
            req = urllib.request.Request(f"{BACKEND_URL}/jobs/{j_id}")
            with urllib.request.urlopen(req) as resp:
                job = json.loads(resp.read().decode())
                m = job.get("metrics", {})
                pts = job.get("matchPoints", [])
                print(f"\nJob ID {j_id} ({job.get('algorithm')}) Status: {job.get('status')} | Model: {job.get('selectedTransformationModel')}")
                print(f"  Source ID: {job.get('sourceImageId')} | Ref ID: {job.get('referenceImageId')}")
                print(f"  Metrics -> Inliers: {m.get('inlierMatchesCount')}, RMSE: {m.get('rmseInliersPx')} px, Gini: {m.get('spatialGiniCoefficient')}, Latency: {m.get('latencyMs')} ms")
                print(f"  Match Points Count: {len(pts)} (Inliers: {sum(1 for p in pts if p.get('inlier'))})")
        except Exception as e:
            print(f"Error reading job {j_id}: {e}")

if __name__ == "__main__":
    main()
