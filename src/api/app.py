"""
FastAPI REST Microservice for LUNARIS-X (SIH26166) Lunar Image Registration Engine.
Provides high-performance endpoints for registering Chandrayaan-2 images
using SIFT baseline, RIFT baseline, and the Proposed Structural AMSR method.
- POST /api/v1/register: End-to-end registration with provenance and quality status
- POST /api/v1/catalog/scan: Scan local directories for PRADAN products
- GET /api/v1/catalog/products: Query indexed PRADAN products by instrument
- POST /api/v1/overlap/check: Autonomous geographic overlap verification
- POST /api/v1/reference/select: 4-tier scientific Reference/Moving selection
- GET /api/v1/health: Service readiness, implemented vs proposed algorithms, hardware status
"""

import base64
import json
import os
import time
import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.registration.pipeline import LunarRegistrationPipeline, RegistrationOutput
from src.geometry.models import TransformationType
from src.preprocessing.normalizer import LunarPreprocessor
from src.features.sift.sift_detector import SIFTDetector
from src.features.rift.rift_detector import RIFTDetector
from src.dataset.pradan_catalog import PradanProductCatalog, PradanProductRecord
from src.dataset.overlap_detector import SpatialOverlapDetector, OverlapResult
from src.proposed.reference_selector import ReferenceMovingSelector, SelectionDecision


app = FastAPI(
    title="LUNARIS-X Lunar Image Registration ML Service (SIH26166)",
    description="Python CV/ML microservice providing SIFT, RIFT, and Structural AMSR pipelines for Chandrayaan-2 PRADAN data.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global catalog singleton
default_catalog_path = "data/pradan_catalog.json"
catalog_instance = PradanProductCatalog(
    catalog_path=default_catalog_path if os.path.exists(default_catalog_path) else None
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    supported_algorithms: List[str]
    implemented_algorithms: List[str]
    proposed_algorithms: List[str]
    supported_models: List[str]
    pradan_ingestion_status: str
    pradan_overlap_detection: str


class MatchPointDTO(BaseModel):
    source_x: float
    source_y: float
    reference_x: float
    reference_y: float
    is_inlier: bool


class RegistrationResponseDTO(BaseModel):
    status: str
    algorithm: str
    transformation_model: str
    transformation_matrix: List[List[float]]
    
    # Match Counts
    candidate_matches_count: int
    inlier_matches_count: int
    inlier_ratio_percent: float
    
    # Accuracy & Residuals
    rmse_inliers: float
    rmse_ground_truth: Optional[float]
    ground_truth_status: str  # AVAILABLE | NOT_AVAILABLE
    mean_subpixel_residual: float
    mae_residuals: float
    median_residual: float
    max_residual: float
    subpixel_accuracy_rate_05px: float
    subpixel_accuracy_rate_10px: float
    spatial_gini_coefficient: float
    spatial_quality_status: str  # GOOD | ACCEPTABLE | POOR
    latency_ms: float
    
    # Data Classification
    data_category: str
    is_synthetic: bool
    
    # Match Points List (for frontend rendering)
    match_points: List[MatchPointDTO]
    
    # Base64 Rendered Diagnostics
    warped_source_base64: str
    reference_image_base64: Optional[str] = None
    match_vis_base64: str
    alpha_overlay_base64: str
    checkerboard_base64: str
    difference_map_base64: str
    panoramic_mosaic_base64: Optional[str] = None
    
    step_diagnostics: Dict[str, Any]
    provenance: Dict[str, Any]


def encode_image_base64(img: np.ndarray, format_ext: str = ".png") -> str:
    """Encodes OpenCV numpy image to Base64 data string."""
    if img is None or img.size == 0:
        return ""
    success, buffer = cv2.imencode(format_ext, img)
    if not success:
        return ""
    return f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"


def decode_image_bytes(file_bytes: bytes) -> np.ndarray:
    """Decodes image bytes to OpenCV numpy array."""
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise HTTPException(status_code=400, detail="Failed to decode input image file.")
    return img


@app.get("/api/v1/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="UP",
        service="LUNARIS_X_Python_ML_Service",
        version="2.0.0",
        supported_algorithms=["Proposed_Method", "SIFT_Baseline", "RIFT_Baseline"],
        implemented_algorithms=["Proposed_Method (AMSR / Structural PC)", "SIFT_Baseline", "RIFT_Baseline"],
        proposed_algorithms=["LoFTR_Learned_Transformer (PROPOSED/UNIMPLEMENTED)"],
        supported_models=["HOMOGRAPHY", "AFFINE", "SIMILARITY", "TRANSLATION"],
        pradan_ingestion_status="READY",
        pradan_overlap_detection="READY"
    )


# -----------------------------------------------------------------
# PRADAN CATALOG ENDPOINTS
# -----------------------------------------------------------------

@app.post("/api/v1/catalog/scan")
def scan_pradan_directory(
    directory_path: str = Form("data/pradan"),
    data_category: str = Form("AUTHENTIC_CH2_PRADAN"),
    is_synthetic: bool = Form(False)
):
    """Scans local filesystem directory for PDS4 XML labels and images."""
    if not os.path.exists(directory_path):
        # Gracefully return empty summary without error
        return {
            "status": "DIR_NOT_FOUND",
            "message": f"Directory '{directory_path}' does not exist yet. Create it and place PRADAN products inside.",
            "scanned_count": 0,
            "catalog_summary": catalog_instance.get_catalog_summary()
        }

    scanned = catalog_instance.scan_directory(
        directory_path=directory_path,
        data_category=data_category,
        is_synthetic=is_synthetic
    )
    catalog_instance.save_catalog("data/pradan_catalog.json")

    return {
        "status": "SUCCESS",
        "scanned_count": len(scanned),
        "catalog_summary": catalog_instance.get_catalog_summary(),
        "products": [rec.to_dict() for rec in scanned]
    }


@app.get("/api/v1/catalog/products")
def list_catalog_products(instrument: Optional[str] = Query(None)):
    """Returns products registered in the PRADAN catalog, optionally filtered by instrument."""
    if instrument:
        products = catalog_instance.query_by_instrument(instrument)
    else:
        products = catalog_instance.get_all_products()

    return {
        "total": len(products),
        "products": [p.to_dict() for p in products]
    }


# -----------------------------------------------------------------
# OVERLAP CHECK ENDPOINT
# -----------------------------------------------------------------

@app.post("/api/v1/overlap/check")
def check_products_overlap(
    reference_id: str = Form(...),
    moving_id: str = Form(...),
    is_benchmark: bool = Form(False)
):
    """Checks mathematical geographic overlap between two cataloged products."""
    ref_prod = catalog_instance.get_product(reference_id)
    mov_prod = catalog_instance.get_product(moving_id)

    if ref_prod is None or mov_prod is None:
        missing = []
        if ref_prod is None:
            missing.append(f"Reference '{reference_id}'")
        if mov_prod is None:
            missing.append(f"Moving '{moving_id}'")
        raise HTTPException(
            status_code=404,
            detail=f"Products not found in catalog: {', '.join(missing)}. Please scan or ingest them first."
        )

    res: OverlapResult = SpatialOverlapDetector.check_overlap(ref_prod, mov_prod, is_manual_benchmark=is_benchmark)
    return res.to_dict()


# -----------------------------------------------------------------
# REFERENCE / MOVING SELECTION ENDPOINT
# -----------------------------------------------------------------

@app.post("/api/v1/reference/select")
def select_reference_moving_roles(
    product_a_id: str = Form(...),
    product_b_id: str = Form(...),
    user_choice: Optional[str] = Form(None),
    registration_objective: Optional[str] = Form(None)
):
    """Computes scientifically justified Reference (Fixed) vs Moving (Source) assignment."""
    prod_a = catalog_instance.get_product(product_a_id)
    prod_b = catalog_instance.get_product(product_b_id)

    if prod_a is None or prod_b is None:
        raise HTTPException(status_code=404, detail="One or both products not found in catalog.")

    decision: SelectionDecision = ReferenceMovingSelector.select_roles(
        product_a=prod_a,
        product_b=prod_b,
        user_reference_choice=user_choice,
        registration_objective=registration_objective
    )
    return decision.to_dict()


# -----------------------------------------------------------------
# REGISTRATION ENDPOINT
# -----------------------------------------------------------------

@app.post("/api/v1/register", response_model=RegistrationResponseDTO)
async def register_images(
    source_file: UploadFile = File(..., description="Source (Moving) Image"),
    reference_file: UploadFile = File(..., description="Reference (Fixed) Image"),
    algorithm: str = Form("Proposed_Method"),
    transformation_model: str = Form("HOMOGRAPHY"),
    ratio_threshold: float = Form(0.80),
    ransac_threshold: float = Form(3.0),
    enable_subpixel: bool = Form(True),
    enable_spatial_filter: bool = Form(True),
    gsd_source_m: Optional[float] = Form(None),
    gsd_reference_m: Optional[float] = Form(None),
    data_category: str = Form("AUTHENTIC_CH2_PRADAN"),
    is_synthetic: bool = Form(False),
    ground_truth_json: Optional[str] = Form(None)
):
    """
    Executes end-to-end image registration between Source (Moving) and Reference (Fixed) images.
    """
    try:
        t_start = time.time()
        src_bytes = await source_file.read()
        ref_bytes = await reference_file.read()

        src_img = decode_image_bytes(src_bytes)
        ref_img = decode_image_bytes(ref_bytes)

        # Parse ground truth matrix if provided
        H_gt = None
        if ground_truth_json:
            try:
                parsed_gt = json.loads(ground_truth_json)
                H_gt = np.array(parsed_gt, dtype=np.float64)
            except Exception:
                H_gt = None

        # Map model enum
        try:
            model_enum = TransformationType(transformation_model.upper())
        except ValueError:
            model_enum = TransformationType.HOMOGRAPHY

        if algorithm in ["Proposed_Method", "AMSR", "Adaptive"]:
            from src.proposed.proposed_pipeline import ProposedRegistrationPipeline
            pipeline = ProposedRegistrationPipeline(
                algorithm_name="Proposed_Method",
                enable_adaptive_strategy=True,
                enable_scale_pyramid=True,
                enable_shadow_suppression=True,
                enable_spatial_filter=enable_spatial_filter,
                enable_dynamic_model=True,
                enable_subpixel=enable_subpixel,
                ratio_threshold=ratio_threshold,
                ransac_threshold=ransac_threshold
            )
        else:
            pipeline = LunarRegistrationPipeline(
                algorithm=algorithm,
                transformation_model=model_enum,
                ratio_threshold=ratio_threshold,
                ransac_threshold=ransac_threshold,
                enable_subpixel=enable_subpixel,
                enable_spatial_filter=enable_spatial_filter
            )

        output: RegistrationOutput = pipeline.register(
            source_image=src_img,
            reference_image=ref_img,
            gsd_source_m=gsd_source_m,
            gsd_reference_m=gsd_reference_m,
            ground_truth_homography=H_gt,
            is_synthetic=is_synthetic,
            dataset_category=data_category
        )

        # Build match points DTO list (inliers + sample of outliers)
        match_dtos = []
        for i in range(min(500, len(output.source_inlier_points))):
            match_dtos.append(MatchPointDTO(
                source_x=float(output.source_inlier_points[i, 0]),
                source_y=float(output.source_inlier_points[i, 1]),
                reference_x=float(output.reference_inlier_points[i, 0]),
                reference_y=float(output.reference_inlier_points[i, 1]),
                is_inlier=True
            ))

        for i in range(min(100, len(output.source_outlier_points))):
            match_dtos.append(MatchPointDTO(
                source_x=float(output.source_outlier_points[i, 0]),
                source_y=float(output.source_outlier_points[i, 1]),
                reference_x=float(output.reference_outlier_points[i, 0]),
                reference_y=float(output.reference_outlier_points[i, 1]),
                is_inlier=False
            ))

        # Scientific provenance
        prov_summary = {
            "source_filename": source_file.filename,
            "reference_filename": reference_file.filename,
            "algorithm": output.algorithm,
            "transformation_model": output.transformation_model,
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data_category": data_category,
            "is_synthetic": is_synthetic,
            "ground_truth_status": output.metrics.ground_truth_status,
            "spatial_quality_status": output.metrics.spatial_quality_status,
            "subpixel_refinement_applied": enable_subpixel,
            "spatial_filtering_applied": enable_spatial_filter
        }

        return RegistrationResponseDTO(
            status=output.status,
            algorithm=output.algorithm,
            transformation_model=output.transformation_model,
            transformation_matrix=output.transformation_matrix.tolist(),
            candidate_matches_count=output.candidate_matches_count,
            inlier_matches_count=output.inlier_matches_count,
            inlier_ratio_percent=output.inlier_ratio_percent,
            rmse_inliers=float(output.metrics.rmse_inliers),
            rmse_ground_truth=output.metrics.rmse_ground_truth,
            ground_truth_status=output.metrics.ground_truth_status,
            mean_subpixel_residual=float(output.metrics.mean_subpixel_residual),
            mae_residuals=float(output.metrics.mae_residuals),
            median_residual=float(output.metrics.median_residual),
            max_residual=float(output.metrics.max_residual),
            subpixel_accuracy_rate_05px=float(output.metrics.subpixel_accuracy_rate_05px),
            subpixel_accuracy_rate_10px=float(output.metrics.subpixel_accuracy_rate_10px),
            spatial_gini_coefficient=float(output.metrics.spatial_gini_coefficient),
            spatial_quality_status=output.metrics.spatial_quality_status,
            latency_ms=float(output.metrics.latency_ms),
            data_category=data_category,
            is_synthetic=is_synthetic,
            match_points=match_dtos,
            warped_source_base64=encode_image_base64(output.warped_source_image),
            reference_image_base64=encode_image_base64(output.reference_image),
            match_vis_base64=encode_image_base64(output.match_visualization),
            alpha_overlay_base64=encode_image_base64(output.alpha_overlay),
            checkerboard_base64=encode_image_base64(output.checkerboard),
            difference_map_base64=encode_image_base64(output.difference_map),
            panoramic_mosaic_base64=encode_image_base64(output.panoramic_mosaic) if getattr(output, 'panoramic_mosaic', None) is not None else None,
            step_diagnostics=output.step_diagnostics,
            provenance=prov_summary
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
