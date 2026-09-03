"""
PRADAN Product Catalog for Chandrayaan-2 Planetary Science Products (SIH26166).
Indexes, validates, and manages OHRC, TMC-2, and IIRS products with full provenance.
Enables independent querying, filtering, and footprint inspection without fabricated metadata.
"""

import os
import glob
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from src.dataset.pds4_parser import PDS4Parser, PDS3Parser, PlanetaryMetadata, MetadataStatus
from src.dataset.provenance import ProvenanceTracker


@dataclass
class PradanProductRecord:
    """Catalog record for an authenticated or benchmark Chandrayaan-2 product."""
    product_id: str
    instrument: str              # CH2_OHRC | CH2_TMC2 | CH2_IIRS
    acquisition_time: Optional[str]
    image_path: str
    metadata_path: str
    gsd_m: Optional[float]
    gsd_status: str              # FOUND | DERIVED | ESTIMATED | MISSING
    dimensions: Optional[Dict[str, int]]  # {"lines": H, "samples": W, "bands": B}
    geographic_footprint: Optional[Dict[str, Optional[float]]]
    has_geographic_footprint: bool
    projection: Optional[str]
    modality: str                # PANCHROMATIC | STEREO_TRIPLET | HYPERSPECTRAL_SWIR | UNKNOWN
    solar_azimuth_deg: Optional[float]
    incidence_angle_deg: Optional[float]
    metadata_confidence: float
    data_category: str           # AUTHENTIC_CH2_PRADAN | SYNTHETIC_BENCHMARK | DEMO
    is_synthetic: bool
    provenance_manifest_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PradanProductCatalog:
    """
    Catalog registry for real Chandrayaan-2 PRADAN products and benchmark datasets.
    Supports querying OHRC, TMC-2, and IIRS independently.
    """

    def __init__(self, catalog_path: Optional[str] = None):
        self.catalog_path = catalog_path
        self._records: Dict[str, PradanProductRecord] = {}

        if catalog_path and os.path.exists(catalog_path):
            self.load_catalog(catalog_path)

    @staticmethod
    def determine_modality(instrument: str) -> str:
        """Determines optical sensing modality from instrument identifier."""
        inst_upper = instrument.upper()
        if "OHRC" in inst_upper:
            return "PANCHROMATIC_HIGH_RES"
        elif "TMC" in inst_upper:
            return "STEREO_PAN"
        elif "IIRS" in inst_upper:
            return "HYPERSPECTRAL_SWIR"
        return "OPTICAL_GENERIC"

    def add_product(self, record: PradanProductRecord) -> None:
        """Adds or updates a product record in the catalog."""
        self._records[record.product_id] = record

    def get_product(self, product_id: str) -> Optional[PradanProductRecord]:
        """Retrieves a product record by its product_id or logical identifier."""
        if product_id in self._records:
            return self._records[product_id]
        # Check partial match on product ID
        for pid, rec in self._records.items():
            if product_id.lower() in pid.lower() or os.path.basename(product_id).lower() in pid.lower():
                return rec
        return None

    def get_all_products(self) -> List[PradanProductRecord]:
        """Returns all registered products."""
        return list(self._records.values())

    def query_by_instrument(self, instrument_name: str) -> List[PradanProductRecord]:
        """Queries products by instrument identifier (case-insensitive substring)."""
        target = instrument_name.upper().replace("-", "").replace("_", "")
        matches = []
        for rec in self._records.values():
            rec_inst = rec.instrument.upper().replace("-", "").replace("_", "")
            if target in rec_inst or rec_inst in target:
                matches.append(rec)
        return matches

    def get_ohrc_products(self) -> List[PradanProductRecord]:
        """Queries all OHRC (Orbiter High Resolution Camera) products."""
        return self.query_by_instrument("OHRC")

    def get_tmc2_products(self) -> List[PradanProductRecord]:
        """Queries all TMC-2 (Terrain Mapping Camera-2) products."""
        return self.query_by_instrument("TMC")

    def get_iirs_products(self) -> List[PradanProductRecord]:
        """Queries all IIRS (Imaging Infra-Red Spectrometer) products."""
        return self.query_by_instrument("IIRS")

    def scan_directory(
        self,
        directory_path: str,
        data_category: str = "AUTHENTIC_CH2_PRADAN",
        is_synthetic: bool = False
    ) -> List[PradanProductRecord]:
        """
        Recursively scans a directory for PDS4 XML and PDS3 LBL metadata files and their
        associated raster images, registering them into the catalog.
        """
        if not os.path.exists(directory_path):
            return []

        xml_files = glob.glob(os.path.join(directory_path, "**", "*.xml"), recursive=True)
        lbl_files = glob.glob(os.path.join(directory_path, "**", "*.lbl"), recursive=True)
        all_labels = xml_files + lbl_files

        scanned = []
        for label_path in all_labels:
            try:
                # 1. Parse PDS metadata
                if label_path.endswith(".xml"):
                    meta: PlanetaryMetadata = PDS4Parser.parse_xml_label(label_path, allow_heuristic_gsd=True)
                else:
                    meta = PDS3Parser.parse_lbl_file(label_path, allow_heuristic_gsd=True)

                # 2. Resolve image path
                dir_name = os.path.dirname(label_path)
                image_path = os.path.join(dir_name, meta.image_filename)

                if not os.path.exists(image_path):
                    # Check common extensions and subfolders (data/, browse/)
                    base_no_ext = os.path.splitext(image_path)[0]
                    found = False
                    for ext in [".tif", ".tiff", ".img", ".png", ".jpg", ".TIF", ".TIFF", ".IMG", ".bin"]:
                        cand = base_no_ext + ext
                        if os.path.exists(cand):
                            image_path = cand
                            found = True
                            break

                    if not found:
                        # Search in data/ subfolder if label is in root
                        data_dir = os.path.join(dir_name, "data")
                        if os.path.exists(data_dir):
                            for ext in [".tif", ".tiff", ".img", ".png", ".TIF", ".IMG"]:
                                cand = os.path.join(data_dir, os.path.basename(base_no_ext) + ext)
                                if os.path.exists(cand):
                                    image_path = cand
                                    found = True
                                    break

                # 3. Create provenance manifest
                prov_path = os.path.splitext(label_path)[0] + "_provenance.json"
                prov_record = ProvenanceTracker.create_provenance_record(
                    metadata=meta,
                    image_path=image_path,
                    source_url="https://pradan.issdc.gov.in/ch2/",
                    data_category=data_category,
                    is_synthetic=is_synthetic,
                    notes="Ingested by LUNARIS-X PRADAN Product Catalog"
                )
                ProvenanceTracker.save_provenance_manifest(prov_record, prov_path)

                # 4. Extract GSD status from metadata fields
                gsd_field = meta.spatial_bounds.fields.get("gsd_m", {})
                gsd_status = gsd_field.get("status", "FOUND" if meta.spatial_bounds.gsd_m is not None else "MISSING")

                # 5. Extract geographic footprint
                has_fp = meta.spatial_bounds.has_geographic_footprint()
                fp = {
                    "min_lat": meta.spatial_bounds.min_lat,
                    "max_lat": meta.spatial_bounds.max_lat,
                    "min_lon": meta.spatial_bounds.min_lon,
                    "max_lon": meta.spatial_bounds.max_lon,
                } if has_fp else None

                record = PradanProductRecord(
                    product_id=meta.product_id,
                    instrument=meta.instrument_id,
                    acquisition_time=meta.acquisition_time_utc,
                    image_path=image_path.replace("\\", "/"),
                    metadata_path=label_path.replace("\\", "/"),
                    gsd_m=meta.spatial_bounds.gsd_m,
                    gsd_status=gsd_status,
                    dimensions=meta.dimensions,
                    geographic_footprint=fp,
                    has_geographic_footprint=has_fp,
                    projection=meta.projection,
                    modality=self.determine_modality(meta.instrument_id),
                    solar_azimuth_deg=meta.solar_geometry.sun_azimuth_deg,
                    incidence_angle_deg=meta.solar_geometry.incidence_angle_deg,
                    metadata_confidence=meta.metadata_confidence_score,
                    data_category=data_category,
                    is_synthetic=is_synthetic,
                    provenance_manifest_path=prov_path.replace("\\", "/")
                )

                self.add_product(record)
                scanned.append(record)

            except Exception as e:
                print(f"[PRADAN Catalog] Error processing {label_path}: {e}")

        if self.catalog_path:
            self.save_catalog()

        return scanned

    def save_catalog(self, file_path: Optional[str] = None) -> None:
        """Saves current catalog to JSON."""
        target_path = file_path or self.catalog_path
        if not target_path:
            raise ValueError("Target catalog path not specified.")

        os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
        data = {
            "catalog_name": "LUNARIS_X_PRADAN_Product_Catalog",
            "version": "1.0",
            "total_products": len(self._records),
            "instruments_summary": {
                "OHRC_count": len(self.get_ohrc_products()),
                "TMC2_count": len(self.get_tmc2_products()),
                "IIRS_count": len(self.get_iirs_products()),
            },
            "products": [rec.to_dict() for rec in self._records.values()]
        }

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_catalog(self, file_path: str) -> None:
        """Loads product records from an existing catalog JSON file."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Catalog file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        products_raw = data.get("products", [])
        self._records.clear()
        for p in products_raw:
            rec = PradanProductRecord(**p)
            self._records[rec.product_id] = rec

    def get_catalog_summary(self) -> Dict[str, Any]:
        """Generates executive summary of registered products."""
        return {
            "total_products": len(self._records),
            "ohrc_count": len(self.get_ohrc_products()),
            "tmc2_count": len(self.get_tmc2_products()),
            "iirs_count": len(self.get_iirs_products()),
            "with_geographic_footprint": sum(1 for r in self._records.values() if r.has_geographic_footprint),
            "authentic_pradan_count": sum(1 for r in self._records.values() if r.data_category == "AUTHENTIC_CH2_PRADAN"),
            "synthetic_benchmark_count": sum(1 for r in self._records.values() if r.is_synthetic)
        }
