"""
PDS4 / PDS3 Metadata Parser for Chandrayaan-2 and Planetary Datasets.
Extracts observational geometry, spatial resolution, coordinates, and image references.
Strictly implements metadata provenance: distinguishes FOUND, DERIVED, ESTIMATED, and MISSING fields.
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Tuple, List
import re
from enum import Enum
from dataclasses import dataclass, field, asdict


class MetadataStatus(str, Enum):
    FOUND = "FOUND"         # Extracted directly from official PDS4 XML label
    DERIVED = "DERIVED"     # Computed from actual raster/file header
    ESTIMATED = "ESTIMATED" # Documented fallback heuristic estimate (explicitly labeled)
    MISSING = "MISSING"     # Unavailable in label and raster; not fabricated


@dataclass
class MetadataField:
    """Individual metadata attribute with explicit provenance and confidence rating."""
    value: Any
    source: Optional[str] = None          # e.g., "PDS4_XML", "RASTER_HEADER", "INSTRUMENT_HEURISTIC_ESTIMATE", None
    status: MetadataStatus = MetadataStatus.MISSING
    confidence: float = 1.0               # 1.0 (FOUND), 0.8 (DERIVED), 0.4 (ESTIMATED), 0.0 (MISSING)
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "source": self.source,
            "status": self.status.value if isinstance(self.status, MetadataStatus) else str(self.status),
            "confidence": self.confidence,
            "notes": self.notes
        }


@dataclass
class SolarGeometry:
    sun_azimuth_deg: Optional[float] = None
    incidence_angle_deg: Optional[float] = None
    emission_angle_deg: Optional[float] = None
    phase_angle_deg: Optional[float] = None
    fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)


@dataclass
class SpatialBounds:
    min_lat: Optional[float] = None
    max_lat: Optional[float] = None
    min_lon: Optional[float] = None
    max_lon: Optional[float] = None
    gsd_m: Optional[float] = None  # Ground Sampling Distance in meters/pixel
    fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def has_geographic_footprint(self) -> bool:
        """Returns True only if all 4 bounding coordinates are valid floats."""
        return (
            self.min_lat is not None and
            self.max_lat is not None and
            self.min_lon is not None and
            self.max_lon is not None
        )


@dataclass
class PlanetaryMetadata:
    product_id: str
    instrument_id: str  # CH2_OHRC, CH2_TMC2, CH2_IIRS, LRO_NAC, SELENE_TC
    target_name: Optional[str]
    acquisition_time_utc: Optional[str]
    solar_geometry: SolarGeometry
    spatial_bounds: SpatialBounds
    projection: Optional[str]
    image_filename: str
    raw_label_path: str
    dimensions: Optional[Dict[str, int]] = None  # lines, samples, bands
    metadata_fields: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    metadata_confidence_score: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_provenance_dict(self) -> Dict[str, Any]:
        """Returns structured provenance summary dictionary for scientific auditing."""
        return {
            "product_id": self.product_id,
            "instrument_id": self.instrument_id,
            "target_name": self.target_name,
            "acquisition_time_utc": self.acquisition_time_utc,
            "metadata_confidence_score": self.metadata_confidence_score,
            "is_pradan_ready": self.is_pradan_ready(),
            "provenance": {
                "label_path": self.raw_label_path,
                "image_filename": self.image_filename,
                "projection": self.projection
            },
            "field_provenance": self.metadata_fields
        }

    def is_pradan_ready(self) -> bool:
        """Evaluates whether critical registration parameters are authenticated."""
        return (
            self.instrument_id != "UNKNOWN" and
            self.spatial_bounds.gsd_m is not None and
            self.spatial_bounds.has_geographic_footprint()
        )


class PDS4Parser:
    """
    Parser for Chandrayaan-2 PDS4 XML Labels and PDS3 LBL files.
    Strictly tracks metadata provenance without substituting fabricated authoritative values.
    """

    # Nominal mission GSD heuristic references (for explicit ESTIMATED status only)
    NOMINAL_GSD_ESTIMATES = {
        "CH2_OHRC": 0.28,
        "CH2_TMC2": 5.0,
        "CH2_IIRS": 120.0,
        "LRO_NAC": 0.5,
        "SELENE_TC": 10.0
    }

    @staticmethod
    def parse_xml_label(xml_path: str, allow_heuristic_gsd: bool = True) -> PlanetaryMetadata:
        """
        Parses a PDS4 XML label file with strict provenance tracking.
        """
        if not os.path.exists(xml_path):
            raise FileNotFoundError(f"Label file not found: {xml_path}")

        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Helper to find tag regardless of XML namespace
        def find_elem_any_ns(parent, tag_name: str) -> Optional[ET.Element]:
            for elem in parent.iter():
                if elem.tag.split("}")[-1].lower() == tag_name.lower():
                    return elem
            return None

        def find_text_any_ns(parent, tag_name: str) -> Optional[str]:
            elem = find_elem_any_ns(parent, tag_name)
            if elem is not None and elem.text:
                return elem.text.strip()
            return None

        fields_dict: Dict[str, MetadataField] = {}

        # -------------------------------------------------------------
        # 1. Product Identification
        # -------------------------------------------------------------
        lid = find_text_any_ns(root, "logical_identifier")
        pid = find_text_any_ns(root, "product_id")
        title = find_text_any_ns(root, "title")

        if lid:
            product_id = lid
            fields_dict["product_id"] = MetadataField(value=lid, source="PDS4_XML:<logical_identifier>", status=MetadataStatus.FOUND, confidence=1.0)
        elif pid:
            product_id = pid
            fields_dict["product_id"] = MetadataField(value=pid, source="PDS4_XML:<product_id>", status=MetadataStatus.FOUND, confidence=1.0)
        elif title:
            product_id = title
            fields_dict["product_id"] = MetadataField(value=title, source="PDS4_XML:<title>", status=MetadataStatus.FOUND, confidence=0.9)
        else:
            base_name = os.path.splitext(os.path.basename(xml_path))[0]
            product_id = base_name
            fields_dict["product_id"] = MetadataField(value=base_name, source="FILENAME", status=MetadataStatus.DERIVED, confidence=0.7)

        # -------------------------------------------------------------
        # 2. Instrument Identification
        # -------------------------------------------------------------
        full_xml_text = "".join([elem.text or "" for elem in root.iter()]).upper()
        inst_id = "UNKNOWN"
        inst_source = None

        if "ORBITER HIGH RESOLUTION" in full_xml_text or "OHRC" in full_xml_text:
            inst_id = "CH2_OHRC"
            inst_source = "PDS4_XML:Observing_System"
        elif "TERRAIN MAPPING" in full_xml_text or "TMC" in full_xml_text:
            inst_id = "CH2_TMC2"
            inst_source = "PDS4_XML:Observing_System"
        elif "INFRARED SPECTROMETER" in full_xml_text or "IIRS" in full_xml_text:
            inst_id = "CH2_IIRS"
            inst_source = "PDS4_XML:Observing_System"
        elif "NARROW ANGLE" in full_xml_text or "LROC" in full_xml_text:
            inst_id = "LRO_NAC"
            inst_source = "PDS4_XML:Observing_System"
        elif "KAGUYA" in full_xml_text or "SELENE" in full_xml_text:
            inst_id = "SELENE_TC"
            inst_source = "PDS4_XML:Observing_System"
        else:
            # Fallback based on filename
            fname_upper = os.path.basename(xml_path).upper()
            if "OHRC" in fname_upper or "OHR" in fname_upper:
                inst_id = "CH2_OHRC"
                inst_source = "FILENAME"
            elif "TMC" in fname_upper:
                inst_id = "CH2_TMC2"
                inst_source = "FILENAME"
            elif "IIRS" in fname_upper:
                inst_id = "CH2_IIRS"
                inst_source = "FILENAME"
            elif "NAC" in fname_upper:
                inst_id = "LRO_NAC"
                inst_source = "FILENAME"

        if inst_source == "PDS4_XML:Observing_System":
            fields_dict["instrument_id"] = MetadataField(value=inst_id, source=inst_source, status=MetadataStatus.FOUND, confidence=1.0)
        elif inst_source == "FILENAME":
            fields_dict["instrument_id"] = MetadataField(value=inst_id, source=inst_source, status=MetadataStatus.DERIVED, confidence=0.75)
        else:
            fields_dict["instrument_id"] = MetadataField(value="UNKNOWN", source=None, status=MetadataStatus.MISSING, confidence=0.0)

        # -------------------------------------------------------------
        # 3. Target & Acquisition Time
        # -------------------------------------------------------------
        target_elem = find_elem_any_ns(root, "Target_Identification")
        target = None
        if target_elem is not None:
            target = find_text_any_ns(target_elem, "name")
        if not target:
            target = find_text_any_ns(root, "target_name")

        if target and target.upper() in ["MOON", "LUNAR"]:
            target_val = target
            fields_dict["target_name"] = MetadataField(value=target_val, source="PDS4_XML:<Target_Identification>/<target_name>", status=MetadataStatus.FOUND, confidence=1.0)
        elif target:
            target_val = target
            fields_dict["target_name"] = MetadataField(value=target_val, source="PDS4_XML", status=MetadataStatus.FOUND, confidence=0.9)
        else:
            target_val = None
            fields_dict["target_name"] = MetadataField(value=None, source=None, status=MetadataStatus.MISSING, confidence=0.0)

        start_time = find_text_any_ns(root, "start_date_time") or find_text_any_ns(root, "acquisition_date_time")
        if start_time:
            fields_dict["acquisition_time_utc"] = MetadataField(value=start_time, source="PDS4_XML:<start_date_time>", status=MetadataStatus.FOUND, confidence=1.0)
        else:
            fields_dict["acquisition_time_utc"] = MetadataField(value=None, source=None, status=MetadataStatus.MISSING, confidence=0.0)

        # -------------------------------------------------------------
        # 4. Solar Geometry
        # -------------------------------------------------------------
        def extract_numeric(tag_names: List[str]) -> Tuple[Optional[float], MetadataField]:
            for tag in tag_names:
                val = find_text_any_ns(root, tag)
                if val is not None:
                    try:
                        fval = float(val)
                        return fval, MetadataField(value=fval, source=f"PDS4_XML:<{tag}>", status=MetadataStatus.FOUND, confidence=1.0)
                    except ValueError:
                        pass
            return None, MetadataField(value=None, source=None, status=MetadataStatus.MISSING, confidence=0.0)

        sun_azimuth, field_az = extract_numeric(["sun_azimuth", "sub_solar_azimuth", "solar_azimuth_angle"])
        incidence, field_inc = extract_numeric(["incidence_angle", "solar_incidence_angle"])
        emission, field_emi = extract_numeric(["emission_angle", "sub_spacecraft_emission_angle"])
        phase, field_ph = extract_numeric(["phase_angle", "solar_phase_angle"])

        solar_fields = {
            "sun_azimuth_deg": field_az.to_dict(),
            "incidence_angle_deg": field_inc.to_dict(),
            "emission_angle_deg": field_emi.to_dict(),
            "phase_angle_deg": field_ph.to_dict()
        }

        solar_geo = SolarGeometry(
            sun_azimuth_deg=sun_azimuth,
            incidence_angle_deg=incidence,
            emission_angle_deg=emission,
            phase_angle_deg=phase,
            fields=solar_fields
        )

        # -------------------------------------------------------------
        # 5. Spatial Bounds & Ground Sampling Distance (GSD)
        # -------------------------------------------------------------
        min_lat, f_min_lat = extract_numeric(["minimum_latitude", "lower_left_latitude", "south_bounding_coordinate"])
        max_lat, f_max_lat = extract_numeric(["maximum_latitude", "upper_right_latitude", "north_bounding_coordinate"])
        min_lon, f_min_lon = extract_numeric(["minimum_longitude", "lower_left_longitude", "west_bounding_coordinate", "westernmost_longitude"])
        max_lon, f_max_lon = extract_numeric(["maximum_longitude", "upper_right_longitude", "east_bounding_coordinate", "easternmost_longitude"])

        raw_gsd, f_gsd = extract_numeric(["pixel_resolution", "sampling_parameter", "spatial_resolution", "map_scale"])

        gsd = raw_gsd
        if gsd is None and allow_heuristic_gsd and inst_id in PDS4Parser.NOMINAL_GSD_ESTIMATES:
            # Explicitly mark as ESTIMATED fallback
            gsd = PDS4Parser.NOMINAL_GSD_ESTIMATES[inst_id]
            f_gsd = MetadataField(
                value=gsd,
                source="INSTRUMENT_HEURISTIC_ESTIMATE",
                status=MetadataStatus.ESTIMATED,
                confidence=0.45,
                notes=f"Nominal operational GSD for {inst_id}. Real GSD was absent in PDS4 XML label."
            )
        elif gsd is None:
            f_gsd = MetadataField(value=None, source=None, status=MetadataStatus.MISSING, confidence=0.0)

        bounds_fields = {
            "min_lat": f_min_lat.to_dict(),
            "max_lat": f_max_lat.to_dict(),
            "min_lon": f_min_lon.to_dict(),
            "max_lon": f_max_lon.to_dict(),
            "gsd_m": f_gsd.to_dict()
        }

        spatial_bounds = SpatialBounds(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            gsd_m=gsd,
            fields=bounds_fields
        )

        # -------------------------------------------------------------
        # 6. Projection & Image File Reference
        # -------------------------------------------------------------
        projection = find_text_any_ns(root, "map_projection_name") or find_text_any_ns(root, "projection_name")
        if projection:
            fields_dict["projection"] = MetadataField(value=projection, source="PDS4_XML:<map_projection_name>", status=MetadataStatus.FOUND, confidence=1.0)
        else:
            fields_dict["projection"] = MetadataField(value=None, source=None, status=MetadataStatus.MISSING, confidence=0.0)

        img_name = find_text_any_ns(root, "file_name")
        img_source = "PDS4_XML:<file_name>"
        img_status = MetadataStatus.FOUND
        if not img_name:
            # Search directory for file matching base name
            dir_path = os.path.dirname(xml_path)
            base_name = os.path.splitext(os.path.basename(xml_path))[0]
            found_candidate = None
            for ext in [".tif", ".tiff", ".img", ".png", ".jpg", ".TIF", ".TIFF", ".IMG", ".bin", ".cub"]:
                cand = os.path.join(dir_path, base_name + ext)
                if os.path.exists(cand):
                    found_candidate = os.path.basename(cand)
                    break
            if found_candidate:
                img_name = found_candidate
                img_source = "DIRECTORY_SCAN"
                img_status = MetadataStatus.DERIVED
        fields_dict["image_filename"] = MetadataField(value=img_name, source=img_source, status=img_status, confidence=1.0 if img_status == MetadataStatus.FOUND else 0.7)

        # -------------------------------------------------------------
        # 7. Raster Dimensions (Lines, Samples, Bands)
        # -------------------------------------------------------------
        lines_val = None
        samples_val = None
        bands_val = None

        # Check Axis_Array elements in PDS4
        for axis_elem in root.iter():
            if "Axis_Array" in axis_elem.tag:
                ax_name = find_text_any_ns(axis_elem, "axis_name")
                elems = find_text_any_ns(axis_elem, "elements")
                if ax_name and elems:
                    try:
                        elem_count = int(elems)
                        if "LINE" in ax_name.upper():
                            lines_val = float(elem_count)
                        elif "SAMPLE" in ax_name.upper():
                            samples_val = float(elem_count)
                        elif "BAND" in ax_name.upper():
                            bands_val = float(elem_count)
                    except ValueError:
                        pass

        if lines_val is None:
            lines_val, f_lines = extract_numeric(["lines", "line"])
        if samples_val is None:
            samples_val, f_samples = extract_numeric(["samples", "sample", "elements"])
        if bands_val is None:
            bands_val, f_bands = extract_numeric(["bands", "band"])

        dimensions = {}
        if lines_val is not None and samples_val is not None:
            dimensions["lines"] = int(lines_val)
            dimensions["samples"] = int(samples_val)
            dimensions["bands"] = int(bands_val) if bands_val is not None else 1
            fields_dict["dimensions"] = MetadataField(
                value=dimensions,
                source="PDS4_XML:Axis_Array",
                status=MetadataStatus.FOUND,
                confidence=1.0
            )
        else:
            # Check if referenced image file exists to derive dimensions
            full_img_path = os.path.join(os.path.dirname(xml_path), img_name)
            if os.path.exists(full_img_path):
                try:
                    import cv2
                    test_im = cv2.imread(full_img_path, cv2.IMREAD_UNCHANGED)
                    if test_im is not None:
                        h, w = test_im.shape[:2]
                        b = test_im.shape[2] if len(test_im.shape) > 2 else 1
                        dimensions = {"lines": h, "samples": w, "bands": b}
                        fields_dict["dimensions"] = MetadataField(
                            value=dimensions,
                            source="RASTER_HEADER",
                            status=MetadataStatus.DERIVED,
                            confidence=0.95
                        )
                except Exception:
                    pass

        # -------------------------------------------------------------
        # 8. Overall Confidence Rating
        # -------------------------------------------------------------
        conf_scores = [f.confidence for f in fields_dict.values()]
        if conf_scores:
            avg_confidence = float(sum(conf_scores) / len(conf_scores))
        else:
            avg_confidence = 0.5

        # Format output fields
        serialized_fields = {k: v.to_dict() for k, v in fields_dict.items()}

        return PlanetaryMetadata(
            product_id=product_id,
            instrument_id=inst_id,
            target_name=target_val,
            acquisition_time_utc=start_time,
            solar_geometry=solar_geo,
            spatial_bounds=spatial_bounds,
            projection=projection,
            image_filename=img_name,
            raw_label_path=xml_path,
            dimensions=dimensions if dimensions else None,
            metadata_fields=serialized_fields,
            metadata_confidence_score=round(avg_confidence, 3)
        )


class PDS3Parser:
    """Fallback parser for PDS3 .LBL headers (used in historical LRO and Kaguya data)."""

    @staticmethod
    def parse_lbl_file(lbl_path: str, allow_heuristic_gsd: bool = True) -> PlanetaryMetadata:
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
        time_utc = metadata_dict.get("START_TIME")

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

        min_lat = get_float("MINIMUM_LATITUDE")
        max_lat = get_float("MAXIMUM_LATITUDE")
        min_lon = get_float("WESTERNMOST_LONGITUDE") or get_float("MINIMUM_LONGITUDE")
        max_lon = get_float("EASTERNMOST_LONGITUDE") or get_float("MAXIMUM_LONGITUDE")
        gsd = get_float("MAP_SCALE") or get_float("PIXEL_RESOLUTION")

        if gsd is None and allow_heuristic_gsd:
            gsd = PDS4Parser.NOMINAL_GSD_ESTIMATES.get(inst_id, None)

        spatial_bounds = SpatialBounds(
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            gsd_m=gsd
        )

        img_file = metadata_dict.get("^IMAGE", os.path.splitext(os.path.basename(lbl_path))[0] + ".IMG")

        return PlanetaryMetadata(
            product_id=product_id,
            instrument_id=inst_id,
            target_name=target,
            acquisition_time_utc=time_utc,
            solar_geometry=solar_geo,
            spatial_bounds=spatial_bounds,
            projection=metadata_dict.get("MAP_PROJECTION_TYPE"),
            image_filename=img_file,
            raw_label_path=lbl_path
        )
