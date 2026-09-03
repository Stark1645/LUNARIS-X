"""
Benchmark Suite Builder for SIH26166 (Ch-2-MatchBench-Synthetic).
Populates Suites A, B, C, D, and E with standardized synthetic test pairs, ground truth, and provenance.
"""

import os
import cv2
import json
import numpy as np
from typing import Dict, Any, List
from src.dataset.synthetic_generator import LunarSurfaceGenerator, SyntheticBenchmarkPairGenerator
from src.dataset.provenance import ProvenanceTracker
from src.dataset.pds4_parser import PlanetaryMetadata, SolarGeometry, SpatialBounds


class BenchmarkSuiteBuilder:
    """Orchestrates creation of standardized benchmark suites."""

    def __init__(self, benchmark_root: str = "data/benchmark"):
        self.benchmark_root = benchmark_root

    def build_all_suites(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Builds all 5 benchmark suites."""
        os.makedirs(self.benchmark_root, exist_ok=True)
        summary = {
            "benchmark_name": "Ch-2-MatchBench-Synthetic",
            "version": "1.1",
            "is_synthetic": True,
            "description": "Controlled synthetic lunar correspondence benchmark with analytical ground truth for SIH26166.",
            "suites": {}
        }

        # 1. Suite A: Intra-Sensor Baseline (Same Illumination)
        summary["suites"]["suite_a"] = self._build_suite_a(force_rebuild)

        # 2. Suite B: Sun-Angle Disparity (90° & 180° Shadow Reversals)
        summary["suites"]["suite_b"] = self._build_suite_b(force_rebuild)

        # 3. Suite C: Extreme Scale Disparity (1:4, 1:16, 1:20)
        summary["suites"]["suite_c"] = self._build_suite_c(force_rebuild)

        # 4. Suite D: Cross-Modal (IIRS SWIR vs Panchromatic)
        summary["suites"]["suite_d"] = self._build_suite_d(force_rebuild)

        # 5. Suite E: Difficult Terrain (Low-Texture Maria vs Dense Highlands)
        summary["suites"]["suite_e"] = self._build_suite_e(force_rebuild)

        # Save overall benchmark catalog
        catalog_path = os.path.join(self.benchmark_root, "benchmark_catalog.json")
        with open(catalog_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary

    def _save_pair(
        self,
        pair_dir: str,
        img1: np.ndarray,
        img2: np.ndarray,
        H_gt: np.ndarray,
        metadata: Dict[str, Any],
        pair_id: str,
        sim_sensor1: str,
        sim_sensor2: str,
        gsd1: float,
        gsd2: float,
        challenge_desc: str
    ) -> Dict[str, Any]:
        os.makedirs(pair_dir, exist_ok=True)
        img1_path = os.path.join(pair_dir, "image_1.png").replace("\\", "/")
        img2_path = os.path.join(pair_dir, "image_2.png").replace("\\", "/")
        gt_path = os.path.join(pair_dir, "ground_truth.json").replace("\\", "/")
        prov_path = os.path.join(pair_dir, "provenance.json").replace("\\", "/")

        cv2.imwrite(img1_path, img1)
        cv2.imwrite(img2_path, img2)

        # Ground truth file
        with open(gt_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        # Metadata records for provenance
        meta1 = PlanetaryMetadata(
            product_id=f"{pair_id}_SYNTH_IMG1",
            instrument_id=sim_sensor1,
            target_name="Moon (Synthetic Simulation)",
            acquisition_time_utc="2026-09-01T00:00:00Z",
            solar_geometry=SolarGeometry(
                sun_azimuth_deg=metadata["sun_azimuth_1_deg"],
                incidence_angle_deg=metadata["incidence_1_deg"]
            ),
            spatial_bounds=SpatialBounds(gsd_m=gsd1),
            projection="Simple Cylindrical (Simulation Frame)",
            image_filename="image_1.png",
            raw_label_path=gt_path
        )

        prov_record = {
            "pair_id": pair_id,
            "data_category": "SYNTHETIC_BENCHMARK",
            "is_synthetic": True,
            "challenge_description": challenge_desc,
            "image_1": ProvenanceTracker.create_provenance_record(
                meta1, img1_path,
                source_url="internal://synthetic_generator/lunar_surface_dem",
                data_category="SYNTHETIC_BENCHMARK",
                is_synthetic=True,
                notes=f"Synthetic Simulation of {sim_sensor1}"
            ),
            "image_2_simulated_sensor": sim_sensor2,
            "image_2_gsd_m": gsd2,
            "delta_sun_azimuth_deg": metadata["delta_sun_azimuth_deg"],
            "scale_ratio": metadata["scale_ratio"],
            "cross_modal": metadata["cross_modal"],
            "ground_truth_homography": metadata["ground_truth_homography"]
        }

        with open(prov_path, "w", encoding="utf-8") as f:
            json.dump(prov_record, f, indent=2)

        return prov_record

    def _build_suite_a(self, force: bool) -> List[Dict[str, Any]]:
        """Suite A: Intra-Sensor Baseline (Same Illumination, 1:1 Scale)."""
        suite_dir = os.path.join(self.benchmark_root, "suite_a_intra_sensor")
        dem = LunarSurfaceGenerator.generate_lunar_elevation_map(1024, 1024, num_craters=40, seed=101)

        # Pair 1: Small rotation, same sun angle
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem, sun_azimuth_1=45.0, sun_azimuth_2=48.0, incidence_1=40.0, incidence_2=40.0,
            rotation_deg=5.0, translation_px=(15.0, -10.0)
        )
        p1 = self._save_pair(os.path.join(suite_dir, "pair_01_baseline_same_sun"),
                             img1, img2, H_gt, meta, "SUITE_A_PAIR_01", "CH2_TMC2", "CH2_TMC2", 5.0, 5.0,
                             "Baseline verification under nearly identical illumination")

        return [p1]

    def _build_suite_b(self, force: bool) -> List[Dict[str, Any]]:
        """Suite B: Sun-Angle Invariance (90° & 180° Illumination Shifts)."""
        suite_dir = os.path.join(self.benchmark_root, "suite_b_sun_angle")
        dem = LunarSurfaceGenerator.generate_lunar_elevation_map(1024, 1024, num_craters=45, seed=202)

        # Pair 2: 90° azimuth shift
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem, sun_azimuth_1=45.0, sun_azimuth_2=135.0, incidence_1=60.0, incidence_2=60.0,
            rotation_deg=8.0, translation_px=(20.0, 10.0)
        )
        p2 = self._save_pair(os.path.join(suite_dir, "pair_02_sun_angle_90deg"),
                             img1, img2, H_gt, meta, "SUITE_B_PAIR_02", "CH2_OHRC", "CH2_OHRC", 0.3, 0.3,
                             "Orthogonal solar illumination (90° azimuth shift)")

        # Pair 3: 180° full shadow reversal (East vs West illumination)
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem, sun_azimuth_1=30.0, sun_azimuth_2=210.0, incidence_1=65.0, incidence_2=65.0,
            rotation_deg=-4.0, translation_px=(-15.0, 25.0)
        )
        p3 = self._save_pair(os.path.join(suite_dir, "pair_03_sun_angle_180deg"),
                             img1, img2, H_gt, meta, "SUITE_B_PAIR_03", "CH2_OHRC", "CH2_OHRC", 0.3, 0.3,
                             "Complete shadow reversal under 180° opposing solar azimuths")

        return [p2, p3]

    def _build_suite_c(self, force: bool) -> List[Dict[str, Any]]:
        """Suite C: Cross-Scale Disparity (1:4, 1:16, 1:20)."""
        suite_dir = os.path.join(self.benchmark_root, "suite_c_scale_disparity")
        dem = LunarSurfaceGenerator.generate_lunar_elevation_map(1024, 1024, num_craters=50, seed=303)

        # Pair 4: 1:4 scale
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem, sun_azimuth_1=60.0, sun_azimuth_2=65.0, incidence_1=45.0, incidence_2=45.0,
            scale_ratio=4.0, rotation_deg=0.0
        )
        p4 = self._save_pair(os.path.join(suite_dir, "pair_04_scale_4x"),
                             img1, img2, H_gt, meta, "SUITE_C_PAIR_04", "CH2_TMC2", "CH2_OHRC", 1.2, 0.3,
                             "Moderate 4x scale gap")

        # Pair 5: 1:16 scale (TMC-2 5.0m vs OHRC 0.31m)
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem, sun_azimuth_1=60.0, sun_azimuth_2=75.0, incidence_1=50.0, incidence_2=50.0,
            scale_ratio=16.0, rotation_deg=2.0
        )
        p5 = self._save_pair(os.path.join(suite_dir, "pair_05_scale_16x_tmc2_ohrc"),
                             img1, img2, H_gt, meta, "SUITE_C_PAIR_05", "CH2_TMC2", "CH2_OHRC", 5.0, 0.31,
                             "Severe 16x cross-scale disparity (TMC-2 to OHRC)")

        # Pair 6: 1:20 scale (TMC-2 5.0m vs OHRC 0.25m)
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem, sun_azimuth_1=45.0, sun_azimuth_2=65.0, incidence_1=55.0, incidence_2=55.0,
            scale_ratio=20.0, rotation_deg=-3.0
        )
        p6 = self._save_pair(os.path.join(suite_dir, "pair_06_scale_20x_tmc2_ohrc"),
                             img1, img2, H_gt, meta, "SUITE_C_PAIR_06", "CH2_TMC2", "CH2_OHRC", 5.0, 0.25,
                             "Extreme 20x cross-scale disparity (TMC-2 5m to OHRC 0.25m)")

        return [p4, p5, p6]

    def _build_suite_d(self, force: bool) -> List[Dict[str, Any]]:
        """Suite D: Cross-Modal (IIRS SWIR vs Panchromatic)."""
        suite_dir = os.path.join(self.benchmark_root, "suite_d_cross_modal")
        dem = LunarSurfaceGenerator.generate_lunar_elevation_map(1024, 1024, num_craters=35, seed=404)

        # Pair 7: Cross-modal IIRS SWIR absorption simulation
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem, sun_azimuth_1=50.0, sun_azimuth_2=55.0, incidence_1=45.0, incidence_2=45.0,
            rotation_deg=4.0, translation_px=(10.0, -10.0), cross_modal=True
        )
        p7 = self._save_pair(os.path.join(suite_dir, "pair_07_cross_modal_swir_pan"),
                             img1, img2, H_gt, meta, "SUITE_D_PAIR_07", "CH2_IIRS", "CH2_TMC2", 80.0, 5.0,
                             "Cross-modal non-linear spectral absorption (IIRS SWIR vs Panchromatic)")

        return [p7]

    def _build_suite_e(self, force: bool) -> List[Dict[str, Any]]:
        """Suite E: Difficult Terrain (Low-Texture Maria vs Dense Highlands)."""
        suite_dir = os.path.join(self.benchmark_root, "suite_e_difficult_terrain")

        # Pair 8: Low-texture maria (only 5 tiny craters)
        dem_maria = LunarSurfaceGenerator.generate_lunar_elevation_map(1024, 1024, num_craters=5, seed=505)
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem_maria, sun_azimuth_1=45.0, sun_azimuth_2=75.0, incidence_1=30.0, incidence_2=35.0,
            rotation_deg=-2.0, translation_px=(5.0, 5.0)
        )
        p8 = self._save_pair(os.path.join(suite_dir, "pair_08_low_texture_maria"),
                             img1, img2, H_gt, meta, "SUITE_E_PAIR_08", "CH2_TMC2", "CH2_TMC2", 5.0, 5.0,
                             "Low-texture feature-sparse lunar maria plain")

        # Pair 9: Dense crater highlands (80 overlapping craters)
        dem_highlands = LunarSurfaceGenerator.generate_lunar_elevation_map(1024, 1024, num_craters=80, seed=606)
        img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
            dem_highlands, sun_azimuth_1=30.0, sun_azimuth_2=90.0, incidence_1=65.0, incidence_2=65.0,
            rotation_deg=7.0, translation_px=(-20.0, 15.0)
        )
        p9 = self._save_pair(os.path.join(suite_dir, "pair_09_dense_crater_highlands"),
                             img1, img2, H_gt, meta, "SUITE_E_PAIR_09", "CH2_OHRC", "CH2_OHRC", 0.3, 0.3,
                             "Dense overlapping crater cluster in lunar highland terrain")

        return [p8, p9]


if __name__ == "__main__":
    builder = BenchmarkSuiteBuilder("data/benchmark")
    cat = builder.build_all_suites(force_rebuild=True)
    print("Clean benchmark suites regenerated successfully.")
