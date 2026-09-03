"""
Command-Line Ingestion Pipeline for Raw Chandrayaan-2 Data.
Processes downloaded PDS4 XML labels and GeoTIFFs, validates geometry, computes provenance,
and registers images into the benchmark catalog.
"""

import os
import sys
import argparse
import json
import glob
from typing import List, Dict, Any
from src.dataset.pds4_parser import PDS4Parser, PDS3Parser
from src.dataset.provenance import ProvenanceTracker
from src.dataset.benchmark_builder import BenchmarkSuiteBuilder


def process_raw_directory(input_dir: str, output_catalog_path: str) -> List[Dict[str, Any]]:
    """Recursively scans input directory for PDS4 XML / PDS3 LBL labels and associated images."""
    if not os.path.exists(input_dir):
        print(f"Input directory does not exist: {input_dir}")
        return []

    xml_files = glob.glob(os.path.join(input_dir, "**", "*.xml"), recursive=True)
    lbl_files = glob.glob(os.path.join(input_dir, "**", "*.lbl"), recursive=True)
    all_labels = xml_files + lbl_files

    print(f"Found {len(all_labels)} metadata label files in {input_dir}")
    ingested_records = []

    for label_path in all_labels:
        try:
            if label_path.endswith(".xml"):
                meta = PDS4Parser.parse_xml_label(label_path)
            else:
                meta = PDS3Parser.parse_lbl_file(label_path)

            # Look for corresponding image file in same directory
            dir_name = os.path.dirname(label_path)
            candidate_img = os.path.join(dir_name, meta.image_filename)
            if not os.path.exists(candidate_img):
                # Check for common extensions
                base_no_ext = os.path.splitext(candidate_img)[0]
                for ext in [".tif", ".tiff", ".img", ".png", ".jpg", ".TIF", ".IMG"]:
                    if os.path.exists(base_no_ext + ext):
                        candidate_img = base_no_ext + ext
                        break

            # Generate provenance record
            prov = ProvenanceTracker.create_provenance_record(
                metadata=meta,
                image_path=candidate_img,
                source_url="https://pradan.issdc.gov.in/ch2/",
                notes="Automated PDS4 Ingestion"
            )

            # Save per-image manifest
            manifest_path = os.path.splitext(label_path)[0] + "_provenance.json"
            ProvenanceTracker.save_provenance_manifest(prov, manifest_path)
            ingested_records.append(prov)
            print(f"Ingested: {meta.product_id} [{meta.instrument_id}] - Solar Az: {meta.solar_geometry.sun_azimuth_deg}°")

        except Exception as e:
            print(f"Error processing {label_path}: {e}")

    # Save aggregated catalog
    os.makedirs(os.path.dirname(os.path.abspath(output_catalog_path)), exist_ok=True)
    with open(output_catalog_path, "w", encoding="utf-8") as f:
        json.dump(ingested_records, f, indent=2)

    print(f"Ingestion complete. Registered {len(ingested_records)} items to {output_catalog_path}")
    return ingested_records


def main():
    parser = argparse.ArgumentParser(description="Chandrayaan-2 Data Ingestion & Benchmark Builder")
    parser.add_argument("--input", type=str, default="data/raw", help="Path to raw PDS4 download folder")
    parser.add_argument("--catalog", type=str, default="data/raw_catalog.json", help="Path to output catalog JSON")
    parser.add_argument("--build-synthetic-bench", action="store_true", help="Generate synthetic Ch-2-MatchBench suites")
    parser.add_argument("--bench-dir", type=str, default="data/benchmark", help="Benchmark output directory")
    args = parser.parse_args()

    if args.build_synthetic_bench:
        print(f"Building synthetic Ch-2-MatchBench benchmark in {args.bench_dir}...")
        builder = BenchmarkSuiteBuilder(args.bench_dir)
        summary = builder.build_all_suites(force_rebuild=True)
        print("Successfully generated Suites A, B, C, D, E.")

    if os.path.exists(args.input):
        process_raw_directory(args.input, args.catalog)


if __name__ == "__main__":
    main()
