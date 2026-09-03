"""
Phase 10: Demo Files Inspection Script.
Reads all 12 source/reference demo files and reports exact paths, dimensions, file sizes, and readability.
"""

import os
from pathlib import Path
from PIL import Image

DEMO_DIR = Path("data/demo")
PAIRS = ["pair_01", "pair_03", "pair_04", "pair_06", "pair_07", "pair_08"]

def main():
    print("================================================================================")
    print(" PHASE 10: DEMO DATASET FILE INTEGRITY & DIMENSIONS AUDIT ")
    print("================================================================================")
    
    results = {}
    for p in PAIRS:
        p_dir = DEMO_DIR / p
        src_path = p_dir / "source.png"
        ref_path = p_dir / "reference.png"
        gt_path = p_dir / "ground_truth.json"
        
        src_exists = src_path.exists()
        ref_exists = ref_path.exists()
        gt_exists = gt_path.exists()
        
        src_info = {}
        if src_exists:
            with Image.open(src_path) as img:
                src_info = {
                    "size_bytes": os.path.getsize(src_path),
                    "dimensions": img.size, # (width, height)
                    "mode": img.mode,
                    "format": img.format
                }
                
        ref_info = {}
        if ref_exists:
            with Image.open(ref_path) as img:
                ref_info = {
                    "size_bytes": os.path.getsize(ref_path),
                    "dimensions": img.size,
                    "mode": img.mode,
                    "format": img.format
                }
                
        results[p] = {
            "src": src_info,
            "ref": ref_info,
            "has_ground_truth": gt_exists
        }
        
        print(f"\n[{p}]")
        print(f"  Source:    {src_path} | Exists: {src_exists} | Size: {src_info.get('size_bytes')} bytes | Dims: {src_info.get('dimensions')} | Mode: {src_info.get('mode')}")
        print(f"  Reference: {ref_path} | Exists: {ref_exists} | Size: {ref_info.get('size_bytes')} bytes | Dims: {ref_info.get('dimensions')} | Mode: {ref_info.get('mode')}")
        print(f"  Ground Truth File: {gt_exists}")

if __name__ == "__main__":
    main()
