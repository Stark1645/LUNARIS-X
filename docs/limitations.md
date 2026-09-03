# System Limitations, Assumptions, and Operational Boundaries

## 1. Physical & Theoretical Limitations

1. **Permanently Shadowed Regions (PSRs)**:
   - In lunar polar craters where sunlight never penetrates ($0\text{ photons}$ direct illumination), optical sensors (OHRC/TMC-2) produce pure sensor noise without regolith texture. Optical correspondence in complete darkness is physically impossible without active illumination (e.g. laser altimetry / LiDAR) or secondary scattered light sensors.
2. **Extreme Scale Disparities Beyond $1:1000$**:
   - Matching raw IIRS ($250\text{ m/px}$) directly to sub-meter OHRC ($0.25\text{ m/px}$) without intermediate TMC-2 ($5\text{ m/px}$) bridging is unfeasible, as a single IIRS pixel spans an entire $1000 \times 1000$ OHRC patch.
3. **Severe Perspective Distortion with Missing Ephemeris**:
   - For oblique TMC-2 Fore/Aft angles ($\pm 26^\circ$), severe terrain-induced parallax requires either a coarse prior DEM or sufficient tie-point distribution to solve for non-affine Thin-Plate Spline deformation.

---

## 2. Operational Assumptions
- Images possess valid PDS4 XML metadata with basic latitude/longitude bounding box estimates to initialize coarse tile search spaces.
- Image radiometric bit depth is at least 8-bit (preferably native 10-bit to 16-bit) to allow dynamic range percentile stretching.

---

## 3. Future Scope Beyond SIH26166
- Integration with Chandrayaan-2 DFRS (Dual Frequency Synthetic Aperture Radar) for Optical-SAR multi-modal correspondence.
- Real-time FPGA / On-board spacecraft implementation for autonomous lunar hazard avoidance and landing pin-pointing.
