"""
Comprehensive Automated Test Suite for PRADAN Ingestion, Cataloging, Overlap Detection,
and Reference/Moving Selection (SIH26166).
"""

import os
import tempfile
import numpy as np
import pytest

from src.dataset.pds4_parser import PDS4Parser, PlanetaryMetadata, MetadataStatus
from src.dataset.pradan_catalog import PradanProductCatalog, PradanProductRecord
from src.dataset.overlap_detector import SpatialOverlapDetector, OverlapResult
from src.proposed.reference_selector import ReferenceMovingSelector, SelectionDecision
from src.preprocessing.normalizer import LunarPreprocessor


# =====================================================================
# 1. PDS4 PARSING & PROVENANCE TESTS
# =====================================================================

def test_pds4_metadata_status_and_provenance():
    """Verifies that PDS4 parsing populates MetadataStatus with explicit provenance."""
    sample_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <Product_Observational xmlns="http://pds.nasa.gov/pds4/pds/v1">
        <Identification_Area>
            <logical_identifier>urn:isro:issdc:ch2:ohrc:ch2_ohr_ncp_20200815t041012_d_img</logical_identifier>
            <product_class>Product_Observational</product_class>
            <title>Chandrayaan-2 OHRC Calibrated Observation</title>
        </Identification_Area>
        <Observation_Area>
            <Time_Coordinates>
                <start_date_time>2020-08-15T04:10:12.124Z</start_date_time>
                <stop_date_time>2020-08-15T04:10:45.312Z</stop_date_time>
            </Time_Coordinates>
            <Investigation_Area>
                <name>Chandrayaan-2</name>
                <type>Mission</type>
            </Investigation_Area>
            <Observing_System>
                <Observing_System_Component>
                    <name>Orbiter High Resolution Camera</name>
                    <type>Instrument</type>
                </Observing_System_Component>
            </Observing_System>
            <Target_Identification>
                <name>Moon</name>
                <type>Satellite</type>
            </Target_Identification>
        </Observation_Area>
        <File_Area_Observational>
            <File>
                <file_name>ch2_ohr_ncp_20200815t041012_d_img.tif</file_name>
            </File>
            <Array_2D_Image>
                <axes>2</axes>
                <axis_index_order>Last_Index_Fastest</axis_index_order>
                <Element_Array>
                    <data_type>UnsignedMSB2</data_type>
                </Element_Array>
                <Axis_Array>
                    <axis_name>Line</axis_name>
                    <elements>2048</elements>
                    <sequence_number>1</sequence_number>
                </Axis_Array>
                <Axis_Array>
                    <axis_name>Sample</axis_name>
                    <elements>2048</elements>
                    <sequence_number>2</sequence_number>
                </Axis_Array>
            </Array_2D_Image>
        </File_Area_Observational>
    </Product_Observational>
    """

    with tempfile.NamedTemporaryFile(suffix=".xml", mode="w", delete=False, encoding="utf-8") as f:
        f.write(sample_xml)
        temp_path = f.name

    try:
        meta = PDS4Parser.parse_xml_label(temp_path, allow_heuristic_gsd=True)

        assert meta.product_id == "urn:isro:issdc:ch2:ohrc:ch2_ohr_ncp_20200815t041012_d_img"
        assert meta.instrument_id == "CH2_OHRC"
        assert meta.target_name == "Moon"
        assert meta.acquisition_time_utc == "2020-08-15T04:10:12.124Z"
        assert meta.dimensions == {"lines": 2048, "samples": 2048, "bands": 1}

        # GSD is estimated via OHRC nominal heuristic since not present in XML
        assert meta.spatial_bounds.gsd_m == 0.28
        gsd_field = meta.spatial_bounds.fields["gsd_m"]
        assert gsd_field["status"] == MetadataStatus.ESTIMATED.value
        assert gsd_field["confidence"] < 0.6  # Explicitly lower confidence for heuristic

        # Target name is FOUND with full confidence
        target_field = meta.metadata_fields["target_name"]
        assert target_field["status"] == MetadataStatus.FOUND.value
        assert target_field["confidence"] == 1.0

        # Provenance summary dictionary is structured
        prov_dict = meta.to_provenance_dict()
        assert "provenance" in prov_dict
        assert "field_provenance" in prov_dict
        assert prov_dict["metadata_confidence_score"] > 0.0
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================================
# 2. PRADAN PRODUCT CATALOG TESTS
# =====================================================================

def test_pradan_catalog_queries_and_filtering():
    """Verifies that the catalog registers products and enables independent instrument querying."""
    catalog = PradanProductCatalog()

    ohrc_rec = PradanProductRecord(
        product_id="CH2_OHRC_001",
        instrument="CH2_OHRC",
        acquisition_time="2020-08-15T04:10:12Z",
        image_path="data/pradan/ohrc_001.tif",
        metadata_path="data/pradan/ohrc_001.xml",
        gsd_m=0.25,
        gsd_status="ESTIMATED",
        dimensions={"lines": 2048, "samples": 2048, "bands": 1},
        geographic_footprint={"min_lat": -70.5, "max_lat": -70.0, "min_lon": 22.0, "max_lon": 22.5},
        has_geographic_footprint=True,
        projection="Equirectangular",
        modality="PANCHROMATIC_HIGH_RES",
        solar_azimuth_deg=45.0,
        incidence_angle_deg=30.0,
        metadata_confidence=0.85,
        data_category="AUTHENTIC_CH2_PRADAN",
        is_synthetic=False
    )

    tmc2_rec = PradanProductRecord(
        product_id="CH2_TMC2_001",
        instrument="CH2_TMC2",
        acquisition_time="2020-08-15T04:10:15Z",
        image_path="data/pradan/tmc2_001.tif",
        metadata_path="data/pradan/tmc2_001.xml",
        gsd_m=5.0,
        gsd_status="FOUND",
        dimensions={"lines": 4096, "samples": 4096, "bands": 1},
        geographic_footprint={"min_lat": -71.0, "max_lat": -69.5, "min_lon": 21.5, "max_lon": 23.0},
        has_geographic_footprint=True,
        projection="Equirectangular",
        modality="STEREO_PAN",
        solar_azimuth_deg=45.5,
        incidence_angle_deg=30.2,
        metadata_confidence=0.95,
        data_category="AUTHENTIC_CH2_PRADAN",
        is_synthetic=False
    )

    iirs_rec = PradanProductRecord(
        product_id="CH2_IIRS_001",
        instrument="CH2_IIRS",
        acquisition_time="2020-08-15T04:10:20Z",
        image_path="data/pradan/iirs_001.img",
        metadata_path="data/pradan/iirs_001.xml",
        gsd_m=80.0,
        gsd_status="FOUND",
        dimensions={"lines": 512, "samples": 512, "bands": 256},
        geographic_footprint={"min_lat": -71.5, "max_lat": -69.0, "min_lon": 20.0, "max_lon": 24.0},
        has_geographic_footprint=True,
        projection="Equirectangular",
        modality="HYPERSPECTRAL_SWIR",
        solar_azimuth_deg=46.0,
        incidence_angle_deg=31.0,
        metadata_confidence=0.92,
        data_category="AUTHENTIC_CH2_PRADAN",
        is_synthetic=False
    )

    catalog.add_product(ohrc_rec)
    catalog.add_product(tmc2_rec)
    catalog.add_product(iirs_rec)

    # Independent queries
    assert len(catalog.get_ohrc_products()) == 1
    assert catalog.get_ohrc_products()[0].product_id == "CH2_OHRC_001"

    assert len(catalog.get_tmc2_products()) == 1
    assert catalog.get_tmc2_products()[0].product_id == "CH2_TMC2_001"

    assert len(catalog.get_iirs_products()) == 1
    assert catalog.get_iirs_products()[0].product_id == "CH2_IIRS_001"

    assert catalog.get_product("CH2_TMC2_001") is not None
    assert catalog.get_product("NONEXISTENT") is None

    summary = catalog.get_catalog_summary()
    assert summary["total_products"] == 3
    assert summary["with_geographic_footprint"] == 3
    assert summary["authentic_pradan_count"] == 3


# =====================================================================
# 3. SPATIAL OVERLAP DETECTION TESTS
# =====================================================================

def test_overlap_detector_confirmed_overlap():
    """Verifies that intersecting footprints return CONFIRMED_OVERLAP and exact percentages."""
    ref_prod = {
        "product_id": "TMC2_BASEMAP",
        "instrument": "CH2_TMC2",
        "gsd_m": 5.0,
        "geographic_footprint": {
            "min_lat": -71.0,
            "max_lat": -69.0,
            "min_lon": 20.0,
            "max_lon": 24.0
        }
    }

    mov_prod = {
        "product_id": "OHRC_CHIP",
        "instrument": "CH2_OHRC",
        "gsd_m": 0.25,
        "geographic_footprint": {
            "min_lat": -70.5,
            "max_lat": -70.0,
            "min_lon": 21.0,
            "max_lon": 22.0
        }
    }

    res: OverlapResult = SpatialOverlapDetector.check_overlap(ref_prod, mov_prod)

    assert res.is_valid_pair is True
    assert res.has_overlap is True
    assert res.overlap_status == "CONFIRMED_OVERLAP"
    # OHRC is completely inside TMC-2 basemap (100% of moving is covered)
    assert res.overlap_percentage_mov == 100.0
    # TMC-2 total area = 2 * 4 = 8 deg2. Intersection = 0.5 * 1.0 = 0.5 deg2 -> 6.25%
    assert res.overlap_percentage_ref == 6.25
    assert res.scale_disparity_ratio == 20.0  # 5.0 / 0.25 = 20x disparity
    assert "Extreme scale disparity" in res.reason


def test_overlap_detector_disjoint_rejection():
    """Verifies that non-overlapping footprints return CONFIRMED_DISJOINT and 0.0% overlap."""
    ref_prod = {
        "product_id": "OHRC_CRATER_A",
        "instrument": "CH2_OHRC",
        "gsd_m": 0.25,
        "geographic_footprint": {"min_lat": 10.0, "max_lat": 10.5, "min_lon": 30.0, "max_lon": 30.5}
    }

    mov_prod = {
        "product_id": "TMC2_CRATER_B",
        "instrument": "CH2_TMC2",
        "gsd_m": 5.0,
        "geographic_footprint": {"min_lat": 25.0, "max_lat": 26.0, "min_lon": 45.0, "max_lon": 46.0}
    }

    res: OverlapResult = SpatialOverlapDetector.check_overlap(ref_prod, mov_prod)

    assert res.is_valid_pair is False
    assert res.has_overlap is False
    assert res.overlap_status == "CONFIRMED_DISJOINT"
    assert res.overlap_percentage_ref == 0.0
    assert res.overlap_percentage_mov == 0.0


def test_overlap_detector_missing_footprint_indeterminate():
    """Verifies that missing coordinates return INDETERMINATE_MISSING_FOOTPRINT."""
    ref_prod = {
        "product_id": "OHRC_NO_BOUNDS",
        "instrument": "CH2_OHRC",
        "gsd_m": 0.25,
        "geographic_footprint": None
    }

    mov_prod = {
        "product_id": "TMC2_WITH_BOUNDS",
        "instrument": "CH2_TMC2",
        "gsd_m": 5.0,
        "geographic_footprint": {"min_lat": 10.0, "max_lat": 12.0, "min_lon": 30.0, "max_lon": 32.0}
    }

    res: OverlapResult = SpatialOverlapDetector.check_overlap(ref_prod, mov_prod)

    assert res.is_valid_pair is False
    assert res.has_overlap is False
    assert res.overlap_status == "INDETERMINATE_MISSING_FOOTPRINT"
    assert res.overlap_percentage_ref is None
    assert "missing" in res.reason.lower()


# =====================================================================
# 4. REFERENCE / MOVING SELECTION TESTS (4 TIERS)
# =====================================================================

def test_reference_selector_tier_1_mission_designation():
    """Verifies Tier 1: mission-provided designation takes absolute precedence."""
    prod_a = {"product_id": "OHRC_P1", "instrument": "CH2_OHRC", "gsd_m": 0.25}
    prod_b = {"product_id": "TMC2_P2", "instrument": "CH2_TMC2", "gsd_m": 5.0}

    decision = ReferenceMovingSelector.select_roles(
        product_a=prod_a,
        product_b=prod_b,
        mission_designation={"reference": "OHRC_P1", "moving": "TMC2_P2"}
    )

    assert decision.reference_product_id == "OHRC_P1"
    assert decision.moving_product_id == "TMC2_P2"
    assert decision.decision_tier == "TIER_1_MISSION_DESIGNATION"


def test_reference_selector_tier_2_user_choice():
    """Verifies Tier 2: user-selected target coordinate system is honored."""
    prod_a = {"product_id": "OHRC_P1", "instrument": "CH2_OHRC", "gsd_m": 0.25}
    prod_b = {"product_id": "TMC2_P2", "instrument": "CH2_TMC2", "gsd_m": 5.0}

    decision = ReferenceMovingSelector.select_roles(
        product_a=prod_a,
        product_b=prod_b,
        user_reference_choice="OHRC_P1"
    )

    assert decision.reference_product_id == "OHRC_P1"
    assert decision.moving_product_id == "TMC2_P2"
    assert decision.decision_tier == "TIER_2_USER_SELECTION"


def test_reference_selector_tier_3_objective_basemap():
    """Verifies Tier 3: REGIONAL_BASEMAP objective selects the wider/coarser frame as Reference."""
    prod_a = {"product_id": "OHRC_FINE", "instrument": "CH2_OHRC", "gsd_m": 0.25, "area": 0.2}
    prod_b = {"product_id": "TMC2_COARSE", "instrument": "CH2_TMC2", "gsd_m": 5.0, "area": 4.0}

    decision = ReferenceMovingSelector.select_roles(
        product_a=prod_a,
        product_b=prod_b,
        registration_objective="REGIONAL_BASEMAP_ALIGNMENT"
    )

    assert decision.reference_product_id == "TMC2_COARSE"
    assert decision.moving_product_id == "OHRC_FINE"
    assert decision.decision_tier == "TIER_3_REGISTRATION_OBJECTIVE"


def test_reference_selector_tier_4_heuristic_stability():
    """Verifies Tier 4: Scientific multi-factor heuristic prefers calibrated stereo TMC-2 basemap."""
    prod_a = {"product_id": "OHRC_CHIP", "instrument": "CH2_OHRC", "gsd_m": 0.25, "area": 0.1, "confidence": 0.8}
    prod_b = {"product_id": "TMC2_BASE", "instrument": "CH2_TMC2", "gsd_m": 5.0, "area": 2.0, "confidence": 0.9}

    decision = ReferenceMovingSelector.select_roles(
        product_a=prod_a,
        product_b=prod_b
    )

    assert decision.reference_product_id == "TMC2_BASE"
    assert decision.moving_product_id == "OHRC_CHIP"
    assert decision.decision_tier == "TIER_4_SCIENTIFIC_HEURISTIC"
    assert "heuristic score" in decision.rationale.lower()


# =====================================================================
# 5. MULTI-MODAL PREPROCESSING ENHANCEMENT TESTS
# =====================================================================

def test_preprocessing_nan_and_inf_sanitization():
    """Verifies that invalid pixels (NaN, +Inf, -Inf) are sanitized non-destructively."""
    raw = np.array([
        [10.0, np.nan, 30.0],
        [np.inf, 50.0, -np.inf],
        [70.0, 80.0, 90.0]
    ], dtype=np.float32)

    sanitized, diag = LunarPreprocessor.sanitize_raster(raw)

    assert diag["nan_pixels_fixed"] == 1
    assert diag["inf_pixels_fixed"] == 2
    assert not np.any(np.isnan(sanitized))
    assert not np.any(np.isinf(sanitized))
    # Original array was not mutated in-place
    assert np.isnan(raw[0, 1])


def test_preprocessing_modality_aware():
    """Verifies instrument-specific conditioning for OHRC, TMC-2, and IIRS."""
    synth_img = (np.random.rand(64, 64) * 200).astype(np.uint8)

    ohrc_out, ohrc_diag = LunarPreprocessor.modality_aware_preprocess(synth_img, instrument="CH2_OHRC")
    assert ohrc_out.shape == (64, 64)
    assert "Bilateral" in ohrc_diag["conditioning"]

    tmc2_out, tmc2_diag = LunarPreprocessor.modality_aware_preprocess(synth_img, instrument="CH2_TMC2")
    assert tmc2_out.shape == (64, 64)
    assert "CLAHE" in tmc2_diag["conditioning"]

    iirs_out, iirs_diag = LunarPreprocessor.modality_aware_preprocess(synth_img, instrument="CH2_IIRS")
    assert iirs_out.shape == (64, 64)
    assert "median" in iirs_diag["conditioning"].lower()
