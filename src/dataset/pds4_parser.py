"""
PDS4 / PDS3 Metadata Parser for Chandrayaan-2 and Planetary Datasets.
Extracts observational geometry, spatial resolution, coordinates, and image references.
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
import re
from dataclasses import dataclass, asdict


@dataclass
class SolarGeometry:
    sun_azimuth_deg: Optional[float] = None
    incidence_angle_deg: Optional[float] = None
    emission_angle_deg: Optional[float] = None
    phase_angle_deg: Optional[float] = None


@dataclass
class SpatialBounds:
    min_lat: Optional[float] = None
    max_lat: Optional[float] = None
    min_lon: Optional[float] = None
    max_lon: Optional[float] = None
    gsd_m: Optional[float] = None  # Ground Sampling Distance in meters/pixel


@dataclass
class PlanetaryMetadata:
    product_id: str
    instrument_id: str  # CH2_OHRC, CH2_TMC2, CH2_IIRS, LRO_NAC, SELENE_TC
    target_name: str
    acquisition_time_utc: str
    solar_geometry: SolarGeometry
    spatial_bounds: SpatialBounds
    projection: str
    image_filename: str
    raw_label_path: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PDS4Parser:
    """Parser for Chandrayaan-2 PDS4 XML Labels and PDS3 LBL files."""

    @staticmethod
    def parse_xml_label(xml_path: str) -> PlanetaryMetadata:
        """Parses a PDS4 XML label file."""
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Label file not found: {xml_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Helper to strip namespaces
        def find_text_any_ns(parent, tag_name: str) -> Optional[str]:
            for elem in parent.iter():
                if elem.tag.split("}")[-1].lower() == tag_name.lower():
                    if elem.text:
                        return elem.text.strip()
            return None

        # 1. Product Identification
        product_id = find_text_any_ns(root, "logical_identifier") or find_text_any_ns(root, "product_id") or os.path.splitext(os.path.basename(xml_path))[0]
        
        # 2. Instrument Identification
        # Check all text in Observing_System, instrument_name, logical_identifier, and title
        full_xml_text = "".join([elem.text or "" for elem in root.iter()]).upper()
        inst_id = "UNKNOWN"
        if "OHRC" in full_xml_text or "ORBITER HIGH RESOLUTION" in full_xml_text:
            inst_id = "CH2_OHRC"
        elif "TMC" in full_xml_text or "TERRAIN MAPPING" in full_xml_text:
            inst_id = "CH2_TMC2"
        elif "IIRS" in full_xml_text or "INFRARED SPECTROMETER" in full_xml_text:
            inst_id = "CH2_IIRS"
        elif "LROC" in full_xml_text or "NARROW ANGLE" in full_xml_text:
            inst_id = "LRO_NAC"
        elif "KAGUYA" in full_xml_text or "SELENE" in full_xml_text:
            inst_id = "SELENE_TC"
        else:
            # Fallback based on filename / path
            fname_upper = os.path.basename(xml_path).upper()
            if "OHRC" in fname_upper or "OHR" in fname_upper:
                inst_id = "CH2_OHRC"
            elif "TMC" in fname_upper:
                inst_id = "CH2_TMC2"
            elif "IIRS" in fname_upper:
                inst_id = "CH2_IIRS"
            elif "NAC" in fname_upper:
                inst_id = "LRO_NAC"

        # 3. Target & Acquisition Time
        target = find_text_any_ns(root, "target_name") or "Moon"
        start_time = find_text_any_ns(root, "start_date_time") or find_text_any_ns(root, "acquisition_date_time") or "2020-01-01T00:00:00Z"

        # 4. Solar Geometry
        def extract_float(tag: str) -> Optional[float]:
            val = find_text_any_ns(root, tag)
            if val is not None:
                try:
                    return float(val)
                except ValueError:
                    return None
            return None

        sun_azimuth = extract_float("sun_azimuth") or extract_float("sub_solar_azimuth") or extract_float("solar_azimuth_angle")
        incidence = extract_float("incidence_angle") or extract_float("solar_incidence_angle")
        emission = extract_float("emission_angle") or extract_float("sub_spacecraft_emission_angle")
        phase = extract_float("phase_angle") or extract_float("solar_phase_angle")

        solar_geo = SolarGeometry(
            sun_azimuth_deg=sun_azimuth,
            incidence_angle_deg=incidence,
            emission_angle_deg=emission,
            phase_angle_deg=phase
        )

        # 5. Spatial Bounds & Resolution (GSD)
        min_lat = extract_float("minimum_latitude") or extract_float("lower_left_latitude")
        max_lat = extract_float("maximum_latitude") or extract_float("upper_right_latitude")
        min_lon = extract_float("minimum_longitude") or extract_float("lower_left_longitude")
        max_lon = extract_float("maximum_longitude") or extract_float("upper_right_longitude")
        gsd = extract_float("pixel_resolution") or extract_float("sampling_parameter") or extract_float("spatial_resolution")

        if gsd is None:
            # Instrument default estimates
            if inst_id == "CH2_OHRC":
                gsd = 0.28
            elif inst_id == "CH2_TMC2":
                gsd = 5.0
            elif inst_id == "CH2_IIRS":
                gsd = 120.0
            elif inst_id == "LRO_NAC":
                gsd = 0.5
            elif inst_id == "SELENE_TC":
                gsd = 10.0

        spatial_bounds = SpatialBounds(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            gsd_m=gsd
        )

        # 6. Projection & Image File Reference
        projection = find_text_any_ns(root, "map_projection_name") or "Simple Cylindrical / Moon 2000 IAU"
        img_name = find_text_any_ns(root, "file_name") or os.path.splitext(os.path.basename(xml_path))[0] + ".tif"

        return PlanetaryMetadata(
            product_id=product_id,
            instrument_id=inst_id,
            target_name=target,
            acquisition_time_utc=start_time,
            solar_geometry=solar_geo,
            spatial_bounds=spatial_bounds,
            projection=projection,
            image_filename=img_name,
            raw_label_path=xml_path
        )


class PDS3Parser:
    """Fallback parser for PDS3 .LBL headers (used in historical LRO and Kaguya data)."""

    @staticmethod
    def parse_lbl_file(lbl_path: str) -> PlanetaryMetadata:
        if not os.path.exists(lbl_path):
            raise FileNotFoundError(f"LBL file not found: {lbl_path}")

        metadata_dict = {}
        with open(lbl_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "=" in line:
                    k, v = line.split("=", 1)
                    metadata_dict[k.strip().upper()] = v.strip().strip('"').strip("'")

        product_id = metadata_dict.get("PRODUCT_ID", os.path.splitext(os.path.basename(lbl_path))[0])
        inst_id = metadata_dict.get("INSTRUMENT_ID", "UNKNOWN")
        target = metadata_dict.get("TARGET_NAME", "MOON")
        time_utc = metadata_dict.get("START_TIME", "2020-01-01T00:00:00Z")

        def get_float(key: str) -> Optional[float]:
            val = metadata_dict.get(key)
            if val:
                match = re.search(r"[-+]?\d*\.\d+|\d+", val)
                if match:
                    return float(match.group(0))
            return None

        solar_geo = SolarGeometry(
            sun_azimuth_deg=get_float("SUB_SOLAR_AZIMUTH") or get_float("SOLAR_AZIMUTH"),
            incidence_angle_deg=get_float("INCIDENCE_ANGLE"),
            emission_angle_deg=get_float("EMISSION_ANGLE"),
            phase_angle_deg=get_float("PHASE_ANGLE")
        )

        spatial_bounds = SpatialBounds(
            min_lat=get_float("MINIMUM_LATITUDE"),
            max_lat=get_float("MAXIMUM_LATITUDE"),
            min_lon=get_float("WESTERNMOST_LONGITUDE") or get_float("MINIMUM_LONGITUDE"),
            max_lon=get_float("EASTERNMOST_LONGITUDE") or get_float("MAXIMUM_LONGITUDE"),
            gsd_m=get_float("MAP_SCALE") or get_float("PIXEL_RESOLUTION") or 1.0
        )

        img_file = metadata_dict.get("^IMAGE", os.path.splitext(os.path.basename(lbl_path))[0] + ".IMG")

        return PlanetaryMetadata(
            product_id=product_id,
            instrument_id=inst_id,
            target_name=target,
            acquisition_time_utc=time_utc,
            solar_geometry=solar_geo,
            spatial_bounds=spatial_bounds,
            projection=metadata_dict.get("MAP_PROJECTION_TYPE", "Moon 2000 IAU"),
            image_filename=img_file,
            raw_label_path=lbl_path
        )
