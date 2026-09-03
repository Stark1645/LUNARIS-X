"""
Scientific Reference / Moving Selection Module for LUNARIS-X (SIH26166).
Implements a 4-tier decision priority to determine which image serves as Reference (Fixed)
and which serves as Moving (Source), strictly avoiding hardcoded assumptions.
"""

from typing import Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict

from src.dataset.pds4_parser import PlanetaryMetadata
from src.dataset.pradan_catalog import PradanProductRecord


@dataclass
class SelectionDecision:
    """Documented scientific decision for Reference (Fixed) and Moving (Source) designation."""
    reference_product_id: str
    moving_product_id: str
    decision_tier: str       # TIER_1_MISSION_DESIGNATION | TIER_2_USER_SELECTION | TIER_3_REGISTRATION_OBJECTIVE | TIER_4_SCIENTIFIC_HEURISTIC
    rationale: str
    reference_instrument: str
    moving_instrument: str
    reference_gsd_m: Optional[float]
    moving_gsd_m: Optional[float]
    criteria_summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ReferenceMovingSelector:
    """
    Selects Reference (Fixed) and Moving (Source) products following the SIH26166 priority:
    1. Dataset/mission-provided designation.
    2. User-selected target coordinate system.
    3. Registration objective.
    4. Multi-factor scientific selection heuristic.
    """

    @classmethod
    def select_roles(
        cls,
        product_a: Union[PradanProductRecord, PlanetaryMetadata, Dict[str, Any]],
        product_b: Union[PradanProductRecord, PlanetaryMetadata, Dict[str, Any]],
        user_reference_choice: Optional[str] = None,
        registration_objective: Optional[str] = None,
        mission_designation: Optional[Dict[str, str]] = None
    ) -> SelectionDecision:
        """
        Determines Reference vs Moving roles according to the 4-tier priority.
        """
        id_a, inst_a, gsd_a, conf_a, area_a = cls._extract_metadata(product_a)
        id_b, inst_b, gsd_b, conf_b, area_b = cls._extract_metadata(product_b)

        # -------------------------------------------------------------
        # TIER 1: Dataset / Mission-provided designation
        # -------------------------------------------------------------
        if mission_designation:
            ref_id = mission_designation.get("reference")
            mov_id = mission_designation.get("moving")
            if ref_id in [id_a, id_b] and mov_id in [id_a, id_b]:
                ref_inst, ref_gsd = (inst_a, gsd_a) if ref_id == id_a else (inst_b, gsd_b)
                mov_inst, mov_gsd = (inst_b, gsd_b) if ref_id == id_a else (inst_a, gsd_a)
                return SelectionDecision(
                    reference_product_id=ref_id,
                    moving_product_id=mov_id,
                    decision_tier="TIER_1_MISSION_DESIGNATION",
                    rationale="Roles assigned by authoritative mission metadata / benchmark catalog designation.",
                    reference_instrument=ref_inst,
                    moving_instrument=mov_inst,
                    reference_gsd_m=ref_gsd,
                    moving_gsd_m=mov_gsd,
                    criteria_summary={"assigned_reference": ref_id, "assigned_moving": mov_id}
                )

        # -------------------------------------------------------------
        # TIER 2: User-selected target coordinate system
        # -------------------------------------------------------------
        if user_reference_choice:
            choice_clean = user_reference_choice.strip().lower()
            if choice_clean in [id_a.lower(), "a", "product_a"]:
                return SelectionDecision(
                    reference_product_id=id_a,
                    moving_product_id=id_b,
                    decision_tier="TIER_2_USER_SELECTION",
                    rationale=f"User explicitly designated {id_a} as the fixed reference coordinate frame.",
                    reference_instrument=inst_a,
                    moving_instrument=inst_b,
                    reference_gsd_m=gsd_a,
                    moving_gsd_m=gsd_b,
                    criteria_summary={"user_choice": id_a}
                )
            elif choice_clean in [id_b.lower(), "b", "product_b"]:
                return SelectionDecision(
                    reference_product_id=id_b,
                    moving_product_id=id_a,
                    decision_tier="TIER_2_USER_SELECTION",
                    rationale=f"User explicitly designated {id_b} as the fixed reference coordinate frame.",
                    reference_instrument=inst_b,
                    moving_instrument=inst_a,
                    reference_gsd_m=gsd_b,
                    moving_gsd_m=gsd_a,
                    criteria_summary={"user_choice": id_b}
                )

        # -------------------------------------------------------------
        # TIER 3: Registration Objective
        # -------------------------------------------------------------
        if registration_objective:
            obj_upper = registration_objective.upper()

            # Objective A: Regional Basemap Alignment / Orthorectification
            # (Coarser, regional wide-coverage frame is reference)
            if any(k in obj_upper for k in ["BASEMAP", "REGIONAL", "ORTHO", "MOSAIC"]):
                if area_a >= area_b or (gsd_a and gsd_b and gsd_a >= gsd_b):
                    ref_id, mov_id = id_a, id_b
                    ref_inst, mov_inst = inst_a, inst_b
                    ref_gsd, mov_gsd = gsd_a, gsd_b
                else:
                    ref_id, mov_id = id_b, id_a
                    ref_inst, mov_inst = inst_b, inst_a
                    ref_gsd, mov_gsd = gsd_b, gsd_a

                return SelectionDecision(
                    reference_product_id=ref_id,
                    moving_product_id=mov_id,
                    decision_tier="TIER_3_REGISTRATION_OBJECTIVE",
                    rationale=f"Objective '{registration_objective}' aligns high-res frame onto wider regional basemap ({ref_id}).",
                    reference_instrument=ref_inst,
                    moving_instrument=mov_inst,
                    reference_gsd_m=ref_gsd,
                    moving_gsd_m=mov_gsd,
                    criteria_summary={"objective": registration_objective, "chosen_reference": ref_id}
                )

            # Objective B: Target Feature Analysis / Detail Inspection
            # (Fine-resolution target frame is reference coordinate system)
            elif any(k in obj_upper for k in ["TARGET", "DETAIL", "INSPECTION", "HIGH_RES"]):
                if gsd_a and gsd_b and gsd_a <= gsd_b:
                    ref_id, mov_id = id_a, id_b
                    ref_inst, mov_inst = inst_a, inst_b
                    ref_gsd, mov_gsd = gsd_a, gsd_b
                else:
                    ref_id, mov_id = id_b, id_a
                    ref_inst, mov_inst = inst_b, inst_a
                    ref_gsd, mov_gsd = gsd_b, gsd_a

                return SelectionDecision(
                    reference_product_id=ref_id,
                    moving_product_id=mov_id,
                    decision_tier="TIER_3_REGISTRATION_OBJECTIVE",
                    rationale=f"Objective '{registration_objective}' maps contextual data into high-resolution target frame ({ref_id}).",
                    reference_instrument=ref_inst,
                    moving_instrument=mov_inst,
                    reference_gsd_m=ref_gsd,
                    moving_gsd_m=mov_gsd,
                    criteria_summary={"objective": registration_objective, "chosen_reference": ref_id}
                )

        # -------------------------------------------------------------
        # TIER 4: Scientific Selection Heuristic
        # Multi-factor score evaluating:
        # 1. Geometric stability (Stereo / calibrated DEM basemap gets bonus)
        # 2. Coverage area (Larger surface footprint provides broader anchor)
        # 3. Metadata confidence (Higher authenticity score preferred)
        # 4. GSD compatibility
        # -------------------------------------------------------------
        score_a = 0.0
        score_b = 0.0

        # Factor 1: Geometric basemap role (TMC-2 has calibrated stereo DEMs)
        if "TMC" in inst_a:
            score_a += 2.0
        if "TMC" in inst_b:
            score_b += 2.0

        # Factor 2: Geographic coverage (larger area = better reference frame)
        if area_a > area_b:
            score_a += 1.5
        elif area_b > area_a:
            score_b += 1.5

        # Factor 3: Metadata authenticity / completeness confidence
        score_a += conf_a * 1.5
        score_b += conf_b * 1.5

        # Factor 4: GSD tie-breaker (coarser GSD typically serves as regional reference)
        if gsd_a and gsd_b:
            if gsd_a > gsd_b:
                score_a += 1.0
            elif gsd_b > gsd_a:
                score_b += 1.0

        if score_a >= score_b:
            ref_id, mov_id = id_a, id_b
            ref_inst, mov_inst = inst_a, inst_b
            ref_gsd, mov_gsd = gsd_a, gsd_b
            reason = f"Heuristic score: {id_a} ({score_a:.2f}) > {id_b} ({score_b:.2f}) due to coverage area and geometric basemap stability."
        else:
            ref_id, mov_id = id_b, id_a
            ref_inst, mov_inst = inst_b, inst_a
            ref_gsd, mov_gsd = gsd_b, gsd_a
            reason = f"Heuristic score: {id_b} ({score_b:.2f}) > {id_a} ({score_a:.2f}) due to coverage area and geometric basemap stability."

        return SelectionDecision(
            reference_product_id=ref_id,
            moving_product_id=mov_id,
            decision_tier="TIER_4_SCIENTIFIC_HEURISTIC",
            rationale=reason,
            reference_instrument=ref_inst,
            moving_instrument=mov_inst,
            reference_gsd_m=ref_gsd,
            moving_gsd_m=mov_gsd,
            criteria_summary={
                "score_product_a": round(score_a, 2),
                "score_product_b": round(score_b, 2),
                "evaluated_factors": ["geometric_stability", "coverage_area", "metadata_confidence", "gsd_compatibility"]
            }
        )

    @staticmethod
    def _extract_metadata(
        item: Union[PradanProductRecord, PlanetaryMetadata, Dict[str, Any]]
    ) -> Tuple[str, str, Optional[float], float, float]:
        """Returns (product_id, instrument, gsd_m, confidence, coverage_area_deg2)."""
        if isinstance(item, PradanProductRecord):
            pid = item.product_id
            inst = item.instrument
            gsd = item.gsd_m
            conf = item.metadata_confidence
            area = 0.0
            if item.has_geographic_footprint and item.geographic_footprint:
                fp = item.geographic_footprint
                lat_span = abs((fp.get("max_lat") or 0.0) - (fp.get("min_lat") or 0.0))
                lon_span = abs((fp.get("max_lon") or 0.0) - (fp.get("min_lon") or 0.0))
                area = float(lat_span * lon_span)
            return pid, inst, gsd, conf, area

        elif isinstance(item, PlanetaryMetadata):
            pid = item.product_id
            inst = item.instrument_id
            gsd = item.spatial_bounds.gsd_m
            conf = item.metadata_confidence_score
            area = 0.0
            sb = item.spatial_bounds
            if sb.has_geographic_footprint():
                area = float(abs(sb.max_lat - sb.min_lat) * abs(sb.max_lon - sb.min_lon))
            return pid, inst, gsd, conf, area

        elif isinstance(item, dict):
            pid = item.get("product_id", "PRODUCT_UNKNOWN")
            inst = item.get("instrument", item.get("instrument_id", "UNKNOWN"))
            gsd = item.get("gsd_m", item.get("gsd"))
            conf = float(item.get("metadata_confidence", item.get("confidence", 0.5)))
            area = float(item.get("coverage_area", item.get("area", 0.0)))
            return pid, inst, gsd, conf, area

        return "UNKNOWN", "UNKNOWN", None, 0.0, 0.0
