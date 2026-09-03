"""
Image Preprocessing & Normalization Module for Lunar Imagery (SIH26166).
Handles 8-bit/16-bit radiometric stretching, percentile clipping, denoising, valid pixel masking,
NaN/Inf handling, multi-band hyperspectral reduction, and modality-aware contrast normalization.
Strictly non-destructive: preserves original scientific arrays and tracks processing provenance.
"""

import os
import cv2
import numpy as np
from typing import Tuple, Optional, Dict, Any, List


class LunarPreprocessor:
    """Preprocesses optical and lunar raster imagery for robust feature extraction."""

    @staticmethod
    def sanitize_raster(
        image: np.ndarray,
        nan_replacement: Optional[float] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Sanitizes raw scientific rasters by eliminating NaN and Inf values without mutating input.
        Returns a clean float32 copy and statistics on corrupted pixels.
        """
        if image is None or image.size == 0:
            raise ValueError("Input raster image is empty or None.")

        # Non-destructive copy
        img_clean = image.copy().astype(np.float32)

        # Multi-band reduction (e.g. IIRS 256-band hyperspectral cube)
        bands = 1
        if len(img_clean.shape) == 3:
            if img_clean.shape[2] > 4:  # Hyperspectral cube
                bands = img_clean.shape[2]
                # Select representative continuum bands (avoid deep water absorption noise)
                # Take robust mean across middle spectral bands (e.g. 50 to 180)
                mid_start = int(bands * 0.2)
                mid_end = int(bands * 0.8)
                img_clean = np.nanmean(img_clean[:, :, mid_start:mid_end], axis=2)
            elif img_clean.shape[2] in [3, 4]:
                # Standard BGR / BGRA
                img_clean = cv2.cvtColor(img_clean[:, :, :3].astype(np.uint8) if img_clean.dtype == np.uint8 else img_clean[:, :, :3], cv2.COLOR_BGR2GRAY).astype(np.float32)

        nan_mask = np.isnan(img_clean)
        inf_mask = np.isinf(img_clean)

        nan_count = int(np.sum(nan_mask))
        inf_count = int(np.sum(inf_mask))

        finite_mask = ~(nan_mask | inf_mask)
        if np.any(finite_mask):
            finite_vals = img_clean[finite_mask]
            min_val = float(np.min(finite_vals))
            max_val = float(np.max(finite_vals))
            med_val = float(np.median(finite_vals)) if nan_replacement is None else nan_replacement
        else:
            min_val, max_val, med_val = 0.0, 0.0, 0.0

        # Replace invalid pixels
        if nan_count > 0:
            img_clean[nan_mask] = med_val
        if inf_count > 0:
            img_clean[img_clean == np.inf] = max_val
            img_clean[img_clean == -np.inf] = min_val

        diag = {
            "original_shape": list(image.shape),
            "sanitized_shape": list(img_clean.shape),
            "bands_processed": bands,
            "nan_pixels_fixed": nan_count,
            "inf_pixels_fixed": inf_count,
            "finite_min": min_val,
            "finite_max": max_val
        }

        return img_clean, diag

    @staticmethod
    def normalize_radiometry(
        image: np.ndarray,
        lower_percentile: float = 2.0,
        upper_percentile: float = 98.0
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Normalizes dynamic range via percentile stretching.
        Handles native 16-bit (PDS4 raw), 32-bit float, and 8-bit images.
        Returns normalized 8-bit [0, 255] grayscale image and stretch metadata.
        """
        if image is None or image.size == 0:
            raise ValueError("Input image is empty or invalid.")

        # 1. Sanitize NaN/Inf first
        sanitized, s_diag = LunarPreprocessor.sanitize_raster(image)

        # 2. Extract valid pixels excluding background zeros
        valid_mask = sanitized > 0
        if np.sum(valid_mask) > 100:
            valid_pixels = sanitized[valid_mask]
        else:
            valid_pixels = sanitized.flatten()

        p_low = float(np.percentile(valid_pixels, lower_percentile))
        p_high = float(np.percentile(valid_pixels, upper_percentile))

        if p_high - p_low < 1e-5:
            norm = np.zeros_like(sanitized, dtype=np.uint8)
        else:
            clipped = np.clip(sanitized, p_low, p_high)
            norm = ((clipped - p_low) / (p_high - p_low) * 255.0).astype(np.uint8)

        stats = {
            "original_dtype": str(image.dtype),
            "original_min": float(sanitized.min()),
            "original_max": float(sanitized.max()),
            "original_mean": float(sanitized.mean()),
            "original_std": float(sanitized.std()),
            "p_low": p_low,
            "p_high": p_high,
            "width": int(norm.shape[1]),
            "height": int(norm.shape[0]),
            "sanitization": s_diag
        }

        return norm, stats

    @staticmethod
    def modality_aware_preprocess(
        image: np.ndarray,
        instrument: str = "GENERIC",
        apply_denoise: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Applies instrument-specific non-destructive radiometric conditioning:
        - OHRC: High-resolution texture preservation + mild edge-preserving bilateral filter.
        - TMC-2: Stereo contrast normalization + gradient equalization.
        - IIRS: Hyperspectral SWIR continuum reduction + local contrast expansion.
        """
        norm_img, stats = LunarPreprocessor.normalize_radiometry(image)

        inst_upper = instrument.upper()
        diag: Dict[str, Any] = {"base_stats": stats, "instrument": instrument}

        if "OHRC" in inst_upper:
            # High-resolution panchromatic: gentle bilateral filter to reduce detector read noise
            # while preserving sharp boulder and crater rim edges
            if apply_denoise:
                processed = cv2.bilateralFilter(norm_img, d=5, sigmaColor=20, sigmaSpace=20)
                diag["conditioning"] = "Bilateral edge-preserving filter (OHRC high-frequency mode)"
            else:
                processed = norm_img
                diag["conditioning"] = "Direct normalized radiometric stretch"

        elif "TMC" in inst_upper:
            # Stereo triplet panchromatic: apply Adaptive Histogram Equalization (CLAHE)
            # to balance illumination differences across stereo pitch angles (+26, 0, -26 deg)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            processed = clahe.apply(norm_img)
            diag["conditioning"] = "CLAHE stereo contrast balancing (TMC-2 mode)"

        elif "IIRS" in inst_upper:
            # Hyperspectral SWIR: apply median filter to suppress spatial dead-pixel stripes,
            # followed by contrast expansion
            med_filtered = cv2.medianBlur(norm_img, 3)
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
            processed = clahe.apply(med_filtered)
            diag["conditioning"] = "Dead-pixel median suppression + CLAHE (IIRS SWIR mode)"

        else:
            processed = norm_img
            diag["conditioning"] = "Standard percentile radiometric normalization"

        return processed, diag

    @staticmethod
    def create_valid_mask(
        image: np.ndarray,
        nodata_value: float = 0.0,
        shadow_threshold: Optional[int] = None
    ) -> np.ndarray:
        """
        Creates a binary mask (255 = valid, 0 = invalid/shadow) to exclude non-informative regions.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        mask = np.ones_like(gray, dtype=np.uint8) * 255

        # Nodata mask
        mask[gray == nodata_value] = 0

        # Optional harsh shadow threshold mask (for permanently shadowed lunar regions)
        if shadow_threshold is not None:
            mask[gray <= shadow_threshold] = 0

        return mask

    @staticmethod
    def denoise_image(
        image: np.ndarray,
        method: str = "gaussian",
        kernel_size: int = 3
    ) -> np.ndarray:
        """
        Applies gentle denoising while preserving morphological edges (crater rims).
        """
        if method == "gaussian":
            return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0.8)
        elif method == "median":
            return cv2.medianBlur(image, kernel_size)
        elif method == "bilateral":
            return cv2.bilateralFilter(image, d=5, sigmaColor=25, sigmaSpace=25)
        else:
            return image
