"""
Unit Tests for SIH26166 Dataset Pipeline, PDS4 Parser, Provenance Tracker, and Benchmark Builder.
"""

import os
import shutil
import tempfile
import pytest
import numpy as np
from src.dataset.pds4_parser import PDS4Parser, PlanetaryMetadata, SolarGeometry, SpatialBounds
from src.dataset.provenance import ProvenanceTracker
from src.dataset.synthetic_generator import LunarSurfaceGenerator, SyntheticBenchmarkPairGenerator
from src.dataset.benchmark_builder import BenchmarkSuiteBuilder


def test_pds4_parser_mock_xml():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <Product_Observational xmlns="http://pds.nasa.gov/pds4/pds/v1">
        <Identification_Area>
            <logical_identifier>urn:isro:isda:ch2_ohrc:data:ch2_ohr_ncp_20200901t120000_cal</logical_identifier>
            <product_class>Product_Observational</product_class>
        </Identification_Area>
        <Observation_Area>
            <start_date_time>2020-09-01T12:00:00.000Z</start_date_time>
            <Target_Identification>
                <target_name>Moon</target_name>
            </Target_Identification>
            <Investigation_Area>
                <name>Chandrayaan-2</name>
            </Investigation_Area>
            <Observing_System>
                <name>Orbiter High Resolution Camera</name>
            </Observing_System>
            <Discipline_Area>
                <Geometry>
                    <sun_azimuth unit="deg">135.5</sun_azimuth>
                    <incidence_angle unit="deg">62.3</incidence_angle>
                    <emission_angle unit="deg">2.1</emission_angle>
                    <phase_angle unit="deg">64.0</phase_angle>
                    <minimum_latitude unit="deg">-82.5</minimum_latitude>
                    <maximum_latitude unit="deg">-81.8</maximum_latitude>
                    <minimum_longitude unit="deg">15.0</minimum_longitude>
                    <maximum_longitude unit="deg">16.2</maximum_longitude>
                    <pixel_resolution unit="m">0.28</pixel_resolution>
                </Geometry>
            </Discipline_Area>
        </Observation_Area>
        <File_Area_Observational>
            <File>
                <file_name>ch2_ohr_ncp_20200901t120000_cal.tif</file_name>
            </File>
        </File_Area_Observational>
    </Product_Observational>
    """
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
        f.write(xml_content)
        temp_xml = f.name

    try:
        meta = PDS4Parser.parse_xml_label(temp_xml)
        assert meta.instrument_id == "CH2_OHRC"
        assert meta.target_name == "Moon"
        assert meta.solar_geometry.sun_azimuth_deg == 135.5
        assert meta.solar_geometry.incidence_angle_deg == 62.3
        assert meta.spatial_bounds.gsd_m == 0.28
        assert meta.spatial_bounds.min_lat == -82.5
        assert meta.image_filename == "ch2_ohr_ncp_20200901t120000_cal.tif"
    finally:
        if os.path.exists(temp_xml):
            os.remove(temp_xml)


def test_provenance_tracker_sha256():
    with tempfile.NamedTemporaryFile("wb", suffix=".bin", delete=False) as f:
        f.write(b"ISRO Chandrayaan-2 Planetary Science Data Provenance Test")
        temp_bin = f.name

    try:
        hash1 = ProvenanceTracker.compute_sha256(temp_bin)
        assert len(hash1) == 64
        # Re-compute to confirm deterministic output
        hash2 = ProvenanceTracker.compute_sha256(temp_bin)
        assert hash1 == hash2
    finally:
        if os.path.exists(temp_bin):
            os.remove(temp_bin)


def test_lunar_surface_and_pair_generation():
    dem = LunarSurfaceGenerator.generate_lunar_elevation_map(width=256, height=256, num_craters=10, seed=42)
    assert dem.shape == (256, 256)
    assert not np.isnan(dem).any()
    assert not np.isinf(dem).any()
    assert dem.std() > 0.1  # Terrain has elevation variance

    img1, img2, H_gt, meta = SyntheticBenchmarkPairGenerator.generate_pair(
        dem, sun_azimuth_1=45.0, sun_azimuth_2=135.0, incidence_1=50.0, incidence_2=50.0,
        scale_ratio=2.0, rotation_deg=5.0
    )
    assert img1.shape == (128, 128)
    assert img2.shape == (256, 256)
    assert H_gt.shape == (3, 3)
    assert meta["delta_sun_azimuth_deg"] == 90.0
    assert meta["scale_ratio"] == 2.0
