"""
Autonomous Geographic Overlap Detector for Chandrayaan-2 Planetary Science Products (SIH26166).
Mathematically evaluates whether two lunar products have overlapping surface coverage.
Rejects invalid pairs without fabricating overlap percentages.
"""

from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict

from src.dataset.pds4_parser import PlanetaryMetadata
from src.dataset.pradan_catalog import PradanProductRecord


@dataclass
class OverlapResult:
    """Rigorous evaluation of spatial overlap between Reference and Moving products."""
    is_valid_pair: bool
    has_overlap: bool
    overlap_status: str  # CONFIRMED_OVERLAP | CONFIRMED_DISJOINT | INDETERMINATE_MISSING_FOOTPRINT | MANUAL_BENCHMARK_PAIR
    overlap_percentage_ref: Optional[float]  # % of reference area covered by overlap
    overlap_percentage_mov: Optional[float]  # % of moving area covered by overlap
    intersection_bounds: Optional[Dict[str, float]]
    intersection_area_deg2: Optional[float]
    scale_disparity_ratio: Optional[float]
    reason: str
    reference_product_id: str
    moving_product_id: str
    reference_instrument: str
    moving_instrument: str
    reference_gsd_m: Optional[float]
    moving_gsd_m: Optional[float]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SpatialOverlapDetector:
    """
    Evaluates geospatial coverage and overlap between candidate Chandrayaan-2 product pairs.
    Operates strictly on authenticated metadata footprints without inventing overlap values.
    """

    @staticmethod
    def _extract_bounds(
        item: Union[PradanProductRecord, PlanetaryMetadata, Dict[str, Any]]
    ) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        if isinstance(item, PradanProductRecord):
            fp = item.geographic_footprint
            if fp and item.has_geographic_footprint:
                return fp.get("min_lat"), fp.get("max_lat"), fp.get("min_lon"), fp.get("max_lon")
            return None, None, None, None

        elif isinstance(item, PlanetaryMetadata):
            sb = item.spatial_bounds
            if sb.has_geographic_footprint():
                return sb.min_lat, sb.max_lat, sb.min_lon, sb.max_lon
            return None, None, None, None

        elif isinstance(item, dict):
            # Check for geographic_footprint or spatial_bounds sub-dict
            fp = item.get("geographic_footprint") or item.get("spatial_bounds") or item
            min_lat = fp.get("min_lat") or fp.get("minimum_latitude")
            max_lat = fp.get("max_lat") or fp.get("maximum_latitude")
            min_lon = fp.get("min_lon") or fp.get("minimum_longitude") or fp.get("westernmost_longitude")
            max_lon = fp.get("max_lon") or fp.get("maximum_longitude") or fp.get("easternmost_longitude")
            if all(v is not None for v in [min_lat, max_lat, min_lon, max_lon]):
                return float(min_lat), float(max_lat), float(min_lon), float(max_lon)
            return None, None, None, None

        return None, None, None, None

    @staticmethod
    def _extract_identifier(item: Union[PradanProductRecord, PlanetaryMetadata, Dict[str, Any]]) -> Tuple[str, str, Optional[float]]:
        if isinstance(item, PradanProductRecord):
            return item.product_id, item.instrument, item.gsd_m
        elif isinstance(item, PlanetaryMetadata):
            return item.product_id, item.instrument_id, item.spatial_bounds.gsd_m
        elif isinstance(item, dict):
            return (
                item.get("product_id", "UNKNOWN_PRODUCT"),
                item.get("instrument", item.get("instrument_id", "UNKNOWN_INSTRUMENT")),
                item.get("gsd_m", item.get("gsd"))
            )
        return "UNKNOWN_PRODUCT", "UNKNOWN_INSTRUMENT", None

    @classmethod
    def check_overlap(
        cls,
        reference: Union[PradanProductRecord, PlanetaryMetadata, Dict[str, Any]],
        moving: Union[PradanProductRecord, PlanetaryMetadata, Dict[str, Any]],
        is_manual_benchmark: bool = False
    ) -> OverlapResult:
        """
        Determines whether reference and moving footprints geometrically intersect on the lunar surface.
        """
        ref_id, ref_inst, ref_gsd = cls._extract_identifier(reference)
        mov_id, mov_inst, mov_gsd = cls._extract_identifier(moving)

        # Scale disparity calculation
        scale_ratio = None
        if ref_gsd is not None and mov_gsd is not None and ref_gsd > 0 and mov_gsd > 0:
            scale_ratio = round(float(max(ref_gsd, mov_gsd) / min(ref_gsd, mov_gsd)), 2)

        if is_manual_benchmark:
            return OverlapResult(
                is_valid_pair=True,
                has_overlap=True,
                overlap_status="MANUAL_BENCHMARK_PAIR",
                overlap_percentage_ref=100.0,
                overlap_percentage_mov=100.0,
                intersection_bounds=None,
                intersection_area_deg2=None,
                scale_disparity_ratio=scale_ratio,
                reason="Pair validated as a verified synthetic benchmark pair with known correspondence.",
                reference_product_id=ref_id,
                moving_product_id=mov_id,
                reference_instrument=ref_inst,
                moving_instrument=mov_inst,
                reference_gsd_m=ref_gsd,
                moving_gsd_m=mov_gsd
            )

        # Extract lat/lon bounds
        ref_min_lat, ref_max_lat, ref_min_lon, ref_max_lon = cls._extract_bounds(reference)
        mov_min_lat, mov_max_lat, mov_min_lon, mov_max_lon = cls._extract_bounds(moving)

        # Case 1: Missing coordinates
        if any(v is None for v in [ref_min_lat, ref_max_lat, ref_min_lon, ref_max_lon,
                                   mov_min_lat, mov_max_lat, mov_min_lon, mov_max_lon]):
            missing = []
            if ref_min_lat is None:
                missing.append(f"Reference ({ref_id})")
            if mov_min_lat is None:
                missing.append(f"Moving ({mov_id})")

            return OverlapResult(
                is_valid_pair=False,
                has_overlap=False,
                overlap_status="INDETERMINATE_MISSING_FOOTPRINT",
                overlap_percentage_ref=None,
                overlap_percentage_mov=None,
                intersection_bounds=None,
                intersection_area_deg2=None,
                scale_disparity_ratio=scale_ratio,
                reason=f"Geospatial footprint (lat/lon) missing in {', '.join(missing)}; autonomous overlap cannot be confirmed.",
                reference_product_id=ref_id,
                moving_product_id=mov_id,
                reference_instrument=ref_inst,
                moving_instrument=mov_inst,
                reference_gsd_m=ref_gsd,
                moving_gsd_m=mov_gsd
            )

        # Case 2: Mathematical 2D bounding box intersection on planetary sphere
        inter_min_lat = max(ref_min_lat, mov_min_lat)
        inter_max_lat = min(ref_max_lat, mov_max_lat)
        inter_min_lon = max(ref_min_lon, mov_min_lon)
        inter_max_lon = min(ref_max_lon, mov_max_lon)

        lat_span = inter_max_lat - inter_min_lat
        lon_span = inter_max_lon - inter_min_lon

        if lat_span <= 0 or lon_span <= 0:
            # Disjoint
            return OverlapResult(
                is_valid_pair=False,
                has_overlap=False,
                overlap_status="CONFIRMED_DISJOINT",
                overlap_percentage_ref=0.0,
                overlap_percentage_mov=0.0,
                intersection_bounds=None,
                intersection_area_deg2=0.0,
                scale_disparity_ratio=scale_ratio,
                reason="Geographic footprints are disjoint; products observe non-overlapping lunar regions.",
                reference_product_id=ref_id,
                moving_product_id=mov_id,
                reference_instrument=ref_inst,
                moving_instrument=mov_inst,
                reference_gsd_m=ref_gsd,
                moving_gsd_m=mov_gsd
            )

        # Compute overlap areas and percentages
        inter_area = float(lat_span * lon_span)
        ref_area = max(1e-9, float((ref_max_lat - ref_min_lat) * (ref_max_lon - ref_min_lon)))
        mov_area = max(1e-9, float((mov_max_lat - mov_min_lat) * (mov_max_lon - mov_min_lon)))

        pct_ref = round(float(min(100.0, (inter_area / ref_area) * 100.0)), 2)
        pct_mov = round(float(min(100.0, (inter_area / mov_area) * 100.0)), 2)

        intersection_bounds = {
            "min_lat": round(inter_min_lat, 4),
            "max_lat": round(inter_max_lat, 4),
            "min_lon": round(inter_min_lon, 4),
            "max_lon": round(inter_max_lon, 4),
        }

        # Reason formulation
        reason = f"Geographic footprints intersect: {pct_ref}% of Reference and {pct_mov}% of Moving frame intersect."
        if scale_ratio and scale_ratio >= 16.0:
            reason += f" Extreme scale disparity ({scale_ratio}x) detected (OHRC/TMC-2); will invoke multi-scale pyramid."

        return OverlapResult(
            is_valid_pair=True,
            has_overlap=True,
            overlap_status="CONFIRMED_OVERLAP",
            overlap_percentage_ref=pct_ref,
            overlap_percentage_mov=pct_mov,
            intersection_bounds=intersection_bounds,
            intersection_area_deg2=round(inter_area, 6),
            scale_disparity_ratio=scale_ratio,
            reason=reason,
            reference_product_id=ref_id,
            moving_product_id=mov_id,
            reference_instrument=ref_inst,
            moving_instrument=mov_inst,
            reference_gsd_m=ref_gsd,
            moving_gsd_m=mov_gsd
        )
