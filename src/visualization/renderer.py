"""
Visualization & Rendering Module for SIH26166.
Renders correspondence lines, inlier/outlier color-coding, spatial coverage plots,
alpha-blended overlays, difference maps, and checkerboard composites.
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List


class RegistrationVisualizer:
    """Generates visual products and diagnostics for image registration."""

    @staticmethod
    def draw_matches(
        source_image: np.ndarray,
        reference_image: np.ndarray,
        src_points: np.ndarray,
        ref_points: np.ndarray,
        inlier_mask: Optional[np.ndarray] = None,
        max_draw: int = 150
    ) -> np.ndarray:
        """
        Draws side-by-side correspondence lines.
        Inliers: Green lines and dots.
        Outliers: Red lines and dots.
        """
        # Ensure 3-channel BGR for drawing
        if len(source_image.shape) == 2:
            img_src = cv2.cvtColor(source_image, cv2.COLOR_GRAY2BGR)
        else:
            img_src = source_image.copy()

        if len(reference_image.shape) == 2:
            img_ref = cv2.cvtColor(reference_image, cv2.COLOR_GRAY2BGR)
        else:
            img_ref = reference_image.copy()

        h_src, w_src = img_src.shape[:2]
        h_ref, w_ref = img_ref.shape[:2]

        h_max = max(h_src, h_ref)
        canvas = np.zeros((h_max, w_src + w_ref, 3), dtype=np.uint8)

        canvas[:h_src, :w_src] = img_src
        canvas[:h_ref, w_src:w_src + w_ref] = img_ref

        n_pts = len(src_points)
        if n_pts == 0:
            return canvas

        indices = list(range(n_pts))
        if n_pts > max_draw:
            # Deterministically sample matches to avoid canvas overcrowding
            indices = list(np.linspace(0, n_pts - 1, max_draw, dtype=int))

        for idx in indices:
            pt_s = (int(round(src_points[idx, 0])), int(round(src_points[idx, 1])))
            pt_r = (int(round(ref_points[idx, 0])) + w_src, int(round(ref_points[idx, 1])))

            is_inlier = bool(inlier_mask[idx]) if inlier_mask is not None else True

            if is_inlier:
                color = (0, 230, 80)  # Bright Green
                radius = 4
                thickness = 1
            else:
                color = (40, 40, 240)  # Red
                radius = 3
                thickness = 1

            cv2.circle(canvas, pt_s, radius, color, -1)
            cv2.circle(canvas, pt_r, radius, color, -1)
            cv2.line(canvas, pt_s, pt_r, color, thickness, cv2.LINE_AA)

        return canvas

    @staticmethod
    def draw_alpha_overlay(
        reference_image: np.ndarray,
        warped_source: np.ndarray,
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Alpha-blended composite overlay of Reference and Warped Source image.
        """
        ref_bgr = cv2.cvtColor(reference_image, cv2.COLOR_GRAY2BGR) if len(reference_image.shape) == 2 else reference_image
        warp_bgr = cv2.cvtColor(warped_source, cv2.COLOR_GRAY2BGR) if len(warped_source.shape) == 2 else warped_source

        # Handle size mismatch if any
        if ref_bgr.shape[:2] != warp_bgr.shape[:2]:
            warp_bgr = cv2.resize(warp_bgr, (ref_bgr.shape[1], ref_bgr.shape[0]))

        overlay = cv2.addWeighted(ref_bgr, 1.0 - alpha, warp_bgr, alpha, 0.0)
        return overlay

    @staticmethod
    def draw_checkerboard(
        reference_image: np.ndarray,
        warped_source: np.ndarray,
        grid_tiles: int = 8
    ) -> np.ndarray:
        """
        Checkerboard composite alternating between Reference and Warped Source tiles.
        Enables visual inspection of continuous linear crater rims across tile boundaries.
        """
        if len(reference_image.shape) == 2:
            ref_bgr = cv2.cvtColor(reference_image, cv2.COLOR_GRAY2BGR)
        else:
            ref_bgr = reference_image

        if len(warped_source.shape) == 2:
            warp_bgr = cv2.cvtColor(warped_source, cv2.COLOR_GRAY2BGR)
        else:
            warp_bgr = warped_source

        h, w = ref_bgr.shape[:2]
        if warp_bgr.shape[:2] != (h, w):
            warp_bgr = cv2.resize(warp_bgr, (w, h))

        composite = np.zeros_like(ref_bgr)
        tile_h = h // grid_tiles
        tile_w = w // grid_tiles

        for r in range(grid_tiles):
            for c in range(grid_tiles):
                y1 = r * tile_h
                y2 = (r + 1) * tile_h if r < grid_tiles - 1 else h
                x1 = c * tile_w
                x2 = (c + 1) * tile_w if c < grid_tiles - 1 else w

                if (r + c) % 2 == 0:
                    composite[y1:y2, x1:x2] = ref_bgr[y1:y2, x1:x2]
                else:
                    composite[y1:y2, x1:x2] = warp_bgr[y1:y2, x1:x2]

        return composite

    @staticmethod
    def draw_difference_map(
        reference_image: np.ndarray,
        warped_source: np.ndarray
    ) -> np.ndarray:
        """
        Absolute intensity difference map | Reference - Warped Source |.
        """
        if len(reference_image.shape) == 3:
            ref_gray = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)
        else:
            ref_gray = reference_image

        if len(warped_source.shape) == 3:
            warp_gray = cv2.cvtColor(warped_source, cv2.COLOR_BGR2GRAY)
        else:
            warp_gray = warped_source

        if ref_gray.shape != warp_gray.shape:
            warp_gray = cv2.resize(warp_gray, (ref_gray.shape[1], ref_gray.shape[0]))

        diff = cv2.absdiff(ref_gray, warp_gray)
        # Apply colormap for visualization (e.g. Jet/Inferno)
        diff_color = cv2.applyColorMap(diff, cv2.COLORMAP_INFERNO)
        return diff_color

    @staticmethod
    def draw_panoramic_mosaic(
        reference_image: np.ndarray,
        source_image: np.ndarray,
        H_matrix: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Builds a full expanded panoramic mosaic displaying the complete spatial coverage
        of BOTH Reference and Source images, with seamless blending across the overlap zone.
        """
        ref_bgr = cv2.cvtColor(reference_image, cv2.COLOR_GRAY2BGR) if len(reference_image.shape) == 2 else reference_image.copy()
        src_bgr = cv2.cvtColor(source_image, cv2.COLOR_GRAY2BGR) if len(source_image.shape) == 2 else source_image.copy()

        h_ref, w_ref = ref_bgr.shape[:2]
        h_src, w_src = src_bgr.shape[:2]

        if H_matrix is None:
            canvas = np.zeros((max(h_ref, h_src), w_ref + w_src, 3), dtype=np.uint8)
            canvas[:h_ref, :w_ref] = ref_bgr
            canvas[:h_src, w_ref:w_ref + w_src] = src_bgr
            return canvas

        try:
            # Source 4 corner points
            src_corners = np.array([
                [0, 0],
                [w_src, 0],
                [w_src, h_src],
                [0, h_src]
            ], dtype=np.float32).reshape(-1, 1, 2)

            warped_corners = cv2.perspectiveTransform(src_corners, H_matrix)

            ref_corners = np.array([
                [0, 0],
                [w_ref, 0],
                [w_ref, h_ref],
                [0, h_ref]
            ], dtype=np.float32).reshape(-1, 1, 2)

            all_corners = np.concatenate((ref_corners, warped_corners), axis=0)

            x_min = float(np.min(all_corners[:, 0, 0]))
            y_min = float(np.min(all_corners[:, 0, 1]))
            x_max = float(np.max(all_corners[:, 0, 0]))
            y_max = float(np.max(all_corners[:, 0, 1]))

            # Safeguard canvas bounds to max 3500 px
            max_dim = 3500
            canvas_w = int(min(max_dim, max(w_ref, round(x_max - x_min))))
            canvas_h = int(min(max_dim, max(h_ref, round(y_max - y_min))))

            if canvas_w <= 0 or canvas_h <= 0 or canvas_w > max_dim or canvas_h > max_dim:
                canvas_w = max(w_ref, w_src)
                canvas_h = max(h_ref, h_src)
                x_min, y_min = 0.0, 0.0

            # Translation matrix to shift union bounding box to (0, 0)
            T = np.array([
                [1.0, 0.0, -x_min],
                [0.0, 1.0, -y_min],
                [0.0, 0.0, 1.0]
            ], dtype=np.float64)

            warped_src_canvas = cv2.warpPerspective(src_bgr, T @ H_matrix, (canvas_w, canvas_h))
            warped_ref_canvas = cv2.warpPerspective(ref_bgr, T, (canvas_w, canvas_h))

            mask_src = (cv2.cvtColor(warped_src_canvas, cv2.COLOR_BGR2GRAY) > 0)
            mask_ref = (cv2.cvtColor(warped_ref_canvas, cv2.COLOR_BGR2GRAY) > 0)

            mosaic = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
            mosaic[mask_ref & ~mask_src] = warped_ref_canvas[mask_ref & ~mask_src]
            mosaic[mask_src & ~mask_ref] = warped_src_canvas[mask_src & ~mask_ref]

            overlap = mask_src & mask_ref
            if np.any(overlap):
                blended = cv2.addWeighted(warped_ref_canvas, 0.5, warped_src_canvas, 0.5, 0.0)
                mosaic[overlap] = blended[overlap]

            return mosaic
        except Exception:
            # Fallback to side-by-side if extreme perspective singularity occurs
            canvas = np.zeros((max(h_ref, h_src), w_ref + w_src, 3), dtype=np.uint8)
            canvas[:h_ref, :w_ref] = ref_bgr
            canvas[:h_src, w_ref:w_ref + w_src] = src_bgr
            return canvas
