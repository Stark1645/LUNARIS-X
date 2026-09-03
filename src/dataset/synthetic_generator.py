"""
Synthetic & Semi-Synthetic Benchmark Generator for SIH26166.
Generates physically grounded lunar test pairs with exact analytical ground truth,
simulating solar illumination shifts (Lommel-Seeliger shading), extreme scale ratios (1:1 to 1:20),
and cross-modal spectral absorption.
"""

import os
import numpy as np
import cv2
from typing import Tuple, Dict, Any, List, Optional


class LunarSurfaceGenerator:
    """Generates synthetic lunar DEMs and simulated photometric optical imagery."""

    @staticmethod
    def generate_lunar_elevation_map(
        width: int = 1024,
        height: int = 1024,
        num_craters: int = 40,
        seed: int = 42
    ) -> np.ndarray:
        """
        Generates a continuous, physically realistic lunar Digital Elevation Model (DEM).
        Crater diameter distribution follows lunar power-law N(D) ~ D^-2 with smooth
        parabolic bowls, raised rims, and optional central peaks.
        """
        np.random.seed(seed)
        dem = np.zeros((height, width), dtype=np.float32)

        # 1. Macro undulating topography (smooth low-frequency regional slopes)
        for octave in range(1, 4):
            freq = 2 ** octave
            grid_h = max(3, height // (freq * 16))
            grid_w = max(3, width // (freq * 16))
            noise = np.random.randn(grid_h, grid_w).astype(np.float32)
            noise_smooth = cv2.GaussianBlur(noise, (0, 0), 1.0)
            resized = cv2.resize(noise_smooth, (width, height), interpolation=cv2.INTER_CUBIC)
            dem += resized * (15.0 / (freq ** 1.5))

        # 2. Power-law distributed craters
        radii = np.random.pareto(a=1.5, size=num_craters) * 20.0 + 10.0
        radii = np.clip(radii, 10.0, 180.0)

        for r in radii:
            cx = np.random.uniform(0.05 * width, 0.95 * width)
            cy = np.random.uniform(0.05 * height, 0.95 * height)
            depth = r * np.random.uniform(0.20, 0.30)

            y_min, y_max = max(0, int(cy - 2.5 * r)), min(height, int(cy + 2.5 * r))
            x_min, x_max = max(0, int(cx - 2.5 * r)), min(width, int(cx + 2.5 * r))

            if y_max <= y_min or x_max <= x_min:
                continue

            y_grid, x_grid = np.ogrid[y_min:y_max, x_min:x_max]
            dist = np.sqrt((x_grid - cx) ** 2 + (y_grid - cy) ** 2).astype(np.float32)
            norm_d = dist / r

            crater = np.zeros_like(dist, dtype=np.float32)

            # Bowl depression inside rim (norm_d < 1.0)
            mask_in = norm_d < 1.0
            crater[mask_in] = -depth * (1.0 - norm_d[mask_in] ** 2)

            # Raised rim (continuous exponential profile)
            rim_h = depth * 0.25 * np.exp(-((norm_d - 1.0) / 0.25) ** 2)
            crater += rim_h

            # Central peak for large impact craters (r > 60px)
            if r > 60.0:
                peak = depth * 0.35 * np.exp(-(norm_d / 0.2) ** 2)
                crater += peak

            dem[y_min:y_max, x_min:x_max] += crater

        # 3. Gaussian anti-aliasing to guarantee continuous C1 differentiability
        dem = cv2.GaussianBlur(dem, (5, 5), 1.2)
        return dem

    @staticmethod
    def render_photometric_shading(
        dem: np.ndarray,
        sun_azimuth_deg: float,
        incidence_angle_deg: float,
        albedo: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Renders lunar optical radiance using the Lommel-Seeliger photometric model.
        Simulates direct directional sunlight, harsh binary shadow transitions, and regolith scattering.
        """
        h, w = dem.shape
        dem_f32 = dem.astype(np.float32)
        az_rad = np.deg2rad(sun_azimuth_deg)
        inc_rad = np.deg2rad(incidence_angle_deg)

        # 1. Surface normal gradients
        dz_dy, dz_dx = np.gradient(dem_f32)
        dz_dx = dz_dx.astype(np.float32)
        dz_dy = dz_dy.astype(np.float32)

        nx = -dz_dx
        ny = -dz_dy
        nz = np.ones_like(dem_f32, dtype=np.float32)
        norm = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2) + 1e-6
        nx /= norm
        ny /= norm
        nz /= norm

        # 2. Solar illumination unit vector
        sx = np.sin(inc_rad) * np.cos(az_rad)
        sy = np.sin(inc_rad) * np.sin(az_rad)
        sz = np.cos(inc_rad)

        # 3. Cosine of incidence and emission angles
        cos_i = np.clip(nx * sx + ny * sy + nz * sz, 0.0, 1.0)
        cos_e = np.clip(nz, 1e-3, 1.0)

        # 4. Lommel-Seeliger lunar photometric function: L = cos(i) / (cos(i) + cos(e))
        radiance = np.where(cos_i > 0, cos_i / (cos_i + cos_e), 0.0)

        # 5. Spatially correlated regolith micro-texture (subtle 1.5% variance)
        noise = cv2.GaussianBlur(np.random.RandomState(42).randn(h, w).astype(np.float32), (3, 3), 0.8) * 0.015
        radiance = np.clip(radiance * (1.0 + noise), 0.0, 1.0)

        if albedo is not None:
            radiance *= albedo

        # Scale to 8-bit dynamic range [0, 255]
        img = np.clip(radiance * 255.0 * 1.8, 0, 255).astype(np.uint8)
        return img


class SyntheticBenchmarkPairGenerator:
    """Creates benchmark test pairs with analytical ground truth transformation matrices."""

    @staticmethod
    def generate_pair(
        dem: np.ndarray,
        sun_azimuth_1: float,
        sun_azimuth_2: float,
        incidence_1: float,
        incidence_2: float,
        scale_ratio: float = 1.0,
        rotation_deg: float = 0.0,
        translation_px: Tuple[float, float] = (0.0, 0.0),
        cross_modal: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
        """
        Generates Image 1 and Image 2 from the same underlying lunar DEM with exact ground-truth Homography.
        H_gt maps coordinates from Image 1 coordinate space to Image 2 coordinate space: x2 = H_gt * x1.
        """
        h, w = dem.shape
        center = (w / 2.0, h / 2.0)

        # Render base unscaled Image 1
        img1_base = LunarSurfaceGenerator.render_photometric_shading(dem, sun_azimuth_1, incidence_1)

        # Transformation for Image 2 canvas: Rotation + Scale + Translation
        # In OpenCV warpAffine, M maps from (x_src, y_src) to (x_dst, y_dst)
        M_rot = cv2.getRotationMatrix2D(center, rotation_deg, 1.0)
        M_rot[0, 2] += translation_px[0]
        M_rot[1, 2] += translation_px[1]

        # 3x3 Homography for rigid/affine warp
        H_warp = np.eye(3, dtype=np.float64)
        H_warp[0:2, :] = M_rot

        # Warp DEM to Image 2 geometry
        dem_warped = cv2.warpAffine(dem.astype(np.float32), M_rot, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

        # Render Image 2 under second sun angle
        img2 = LunarSurfaceGenerator.render_photometric_shading(dem_warped, sun_azimuth_2, incidence_2)

        # Cross-modal simulation (IIRS SWIR spectral absorption)
        if cross_modal:
            img2_float = img2.astype(np.float32) / 255.0
            # Mineral absorption band non-linear contrast inversion
            img2_swir = (1.0 - img2_float) ** 1.6 * 255.0
            img2 = np.clip(img2_swir, 0, 255).astype(np.uint8)

        # Scale down Image 1 if scale_ratio > 1.0 (to simulate coarse sensor like TMC-2 vs OHRC)
        if scale_ratio > 1.0:
            target_w = int(w / scale_ratio)
            target_h = int(h / scale_ratio)
            img1 = cv2.resize(img1_base, (target_w, target_h), interpolation=cv2.INTER_AREA)
            # Coordinate mapping: x_base = scale_ratio * x_scaled -> H_gt = H_warp @ S
            S_mat = np.diag([scale_ratio, scale_ratio, 1.0])
            H_gt_final = H_warp @ S_mat
        else:
            img1 = img1_base
            H_gt_final = H_warp

        metadata = {
            "is_synthetic": True,
            "data_category": "SYNTHETIC_BENCHMARK",
            "generation_model": "Lommel-Seeliger Photometric Shading on C1-Smooth Lunar DEM",
            "sun_azimuth_1_deg": float(sun_azimuth_1),
            "sun_azimuth_2_deg": float(sun_azimuth_2),
            "delta_sun_azimuth_deg": float(abs(sun_azimuth_1 - sun_azimuth_2)),
            "incidence_1_deg": float(incidence_1),
            "incidence_2_deg": float(incidence_2),
            "scale_ratio": float(scale_ratio),
            "rotation_deg": float(rotation_deg),
            "translation_px": [float(translation_px[0]), float(translation_px[1])],
            "cross_modal": bool(cross_modal),
            "ground_truth_homography": H_gt_final.tolist()
        }

        return img1, img2, H_gt_final, metadata
