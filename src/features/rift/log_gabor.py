"""
Log-Gabor Filter Bank & Phase Congruency Engine for Illumination-Robust Baselines (SIH26166).
Implements 2D multi-scale, multi-orientation Log-Gabor filtering, Phase Congruency (PC),
and Maximum Index Map (MIM / MIMPC) feature maps.
"""

import numpy as np
import cv2
from typing import Tuple, List, Dict, Any, Optional


class LogGaborFilterBank:
    """
    Constructs 2D Log-Gabor transfer functions in the frequency domain.
    Log-Gabor filters have zero DC component and broad Gaussian transfer functions on logarithmic frequency scales.
    """

    def __init__(
        self,
        n_scales: int = 4,
        n_orientations: int = 6,
        min_wave_length: float = 3.0,
        mult: float = 2.1,
        sigma_on_f: float = 0.55,
        d_theta_on_sigma: float = 1.2
    ):
        self.n_scales = n_scales
        self.n_orientations = n_orientations
        self.min_wave_length = min_wave_length
        self.mult = mult
        self.sigma_on_f = sigma_on_f
        self.d_theta_on_sigma = d_theta_on_sigma

    def compute_phase_congruency(
        self,
        image: np.ndarray,
        k: float = 2.0,
        epsilon: float = 1e-4
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Computes 2D Phase Congruency (PC), Maximum Moment of PC covariance (MIMPC),
        and Maximum Index Map (MIM) from the Log-Gabor filter responses.

        Returns:
            phase_congruency: 2D float32 array in [0, 1] measuring structural edge strength.
            mim: 2D uint8 array with index of orientation with maximum response (0 to n_orientations-1).
            energy_map: 2D float32 total structural energy.
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        rows, cols = gray.shape
        img_f = gray.astype(np.float32)

        # 1. Setup 2D frequency grid
        u = np.fft.fftfreq(cols).astype(np.float32)
        v = np.fft.fftfreq(rows).astype(np.float32)
        u_grid, v_grid = np.meshgrid(u, v)

        radius = np.sqrt(u_grid ** 2 + v_grid ** 2)
        radius[0, 0] = 1.0  # Prevent log(0) at DC

        theta = np.arctan2(-v_grid, u_grid)
        sintheta = np.sin(theta)
        costheta = np.cos(theta)

        # 2. FFT of input image
        image_fft = np.fft.fft2(img_f)

        # Accumulators
        orientation_energy = np.zeros((self.n_orientations, rows, cols), dtype=np.float32)
        orientation_amplitude = np.zeros((self.n_orientations, rows, cols), dtype=np.float32)
        total_sum_an = np.zeros((rows, cols), dtype=np.float32)
        total_energy = np.zeros((rows, cols), dtype=np.float32)

        theta_sigma = (np.pi / self.n_orientations) / self.d_theta_on_sigma

        # 3. Filter across scales and orientations
        for o in range(self.n_orientations):
            angl = o * np.pi / self.n_orientations
            # Angular filter component (Gaussian)
            ds = sintheta * np.cos(angl) - costheta * np.sin(angl)
            dc = costheta * np.cos(angl) + sintheta * np.sin(angl)
            dtheta = np.abs(np.arctan2(ds, dc))
            angular_filter = np.exp(- (dtheta ** 2) / (2.0 * theta_sigma ** 2))

            sum_e_o = np.zeros((rows, cols), dtype=np.float32)
            sum_o_o = np.zeros((rows, cols), dtype=np.float32)

            for s in range(self.n_scales):
                wavelength = self.min_wave_length * (self.mult ** s)
                fo = 1.0 / wavelength

                # Radial Log-Gabor filter
                radial_filter = np.exp(- ((np.log(radius / fo)) ** 2) / (2.0 * (np.log(self.sigma_on_f)) ** 2))
                radial_filter[0, 0] = 0.0  # Zero DC

                log_gabor_filter = radial_filter * angular_filter

                # Convolve in frequency domain
                response_fft = image_fft * log_gabor_filter
                response = np.fft.ifft2(response_fft)

                even = np.real(response).astype(np.float32)
                odd = np.imag(response).astype(np.float32)
                amplitude = np.sqrt(even ** 2 + odd ** 2)

                sum_e_o += even
                sum_o_o += odd
                orientation_amplitude[o] += amplitude
                total_sum_an += amplitude

            # Energy per orientation
            energy_o = np.sqrt(sum_e_o ** 2 + sum_o_o ** 2)
            orientation_energy[o] = energy_o
            total_energy += energy_o

        # 4. Phase Congruency (PC) computation
        phase_congruency = total_energy / (total_sum_an + epsilon)
        phase_congruency = np.clip(phase_congruency, 0.0, 1.0)

        # 5. Maximum Index Map (MIM): index of orientation yielding maximum total energy/amplitude
        mim = np.argmax(orientation_amplitude, axis=0).astype(np.uint8)

        return phase_congruency, mim, total_energy
