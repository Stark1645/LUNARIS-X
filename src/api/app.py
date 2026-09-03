"""
FastAPI REST Microservice for SIH26166 Lunar Image Registration Engine.
Exposes REST endpoints for Spring Boot backend communication:
- POST /api/v1/register: End-to-end registration
- POST /api/v1/features: Keypoint & descriptor extraction
- GET /api/v1/health: Service readiness and hardware capability
"""

import base64
import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.registration.pipeline import LunarRegistrationPipeline, RegistrationOutput
from src.geometry.models import TransformationType
from src.preprocessing.normalizer import LunarPreprocessor
from src.features.sift.sift_detector import SIFTDetector
from src.features.rift.rift_detector import RIFTDetector


app = FastAPI(
    title="SIH26166 Lunar Image Registration ML Service",
    description="Python CV/ML microservice providing SIFT baseline, RIFT baseline, and modular registration pipeline.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    supported_algorithms: List[str]
    supported_models: List[str]


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
    
    # Metrics
    rmse_inliers: float
    rmse_ground_truth: Optional[float]
    mean_subpixel_residual: float
    subpixel_accuracy_rate_05px: float
    spatial_gini_coefficient: float
    latency_ms: float
    
    # Match points list (up to 500 points for frontend rendering)
    match_points: List[MatchPointDTO]
    
    # Base64 Rendered Diagnostics
    warped_source_base64: str
    match_vis_base64: str
    alpha_overlay_base64: str
    checkerboard_base64: str
    difference_map_base64: str
    
    step_diagnostics: Dict[str, Any]


def encode_image_base64(img: np.ndarray, format_ext: str = ".png") -> str:
    """Encodes OpenCV numpy image to Base64 data string."""
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
        service="SIH26166_Python_ML_Service",
        version="1.0.0",
        supported_algorithms=["Proposed_Method", "SIFT_Baseline", "RIFT_Baseline"],
        supported_models=["HOMOGRAPHY", "AFFINE", "SIMILARITY", "TRANSLATION"]
    )


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
    gsd_reference_m: Optional[float] = Form(None)
):
    """
    Executes end-to-end image registration between Source (Moving) and Reference (Fixed) images.
    """
    try:
        src_bytes = await source_file.read()
        ref_bytes = await reference_file.read()

        src_img = decode_image_bytes(src_bytes)
        ref_img = decode_image_bytes(ref_bytes)

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
            gsd_reference_m=gsd_reference_m
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
            mean_subpixel_residual=float(output.metrics.mean_subpixel_residual),
            subpixel_accuracy_rate_05px=float(output.metrics.subpixel_accuracy_rate_05px),
            spatial_gini_coefficient=float(output.metrics.spatial_gini_coefficient),
            latency_ms=float(output.metrics.latency_ms),
            match_points=match_dtos,
            warped_source_base64=encode_image_base64(output.warped_source_image),
            match_vis_base64=encode_image_base64(output.match_visualization),
            alpha_overlay_base64=encode_image_base64(output.alpha_overlay),
            checkerboard_base64=encode_image_base64(output.checkerboard),
            difference_map_base64=encode_image_base64(output.difference_map),
            step_diagnostics=output.step_diagnostics
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
