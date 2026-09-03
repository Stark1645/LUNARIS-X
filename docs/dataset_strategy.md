# Dataset Acquisition, Verification & Provenance Strategy

## 1. Official Primary Data Sources & Portals

```
+---------------------------------------------------------------------------------------------------+
| PORTAL / SOURCE                     | URL                               | HOSTING INSTITUTION     |
+-------------------------------------+-----------------------------------+-------------------------+
| 1. Chandrayaan-2 PRADAN Archive     | https://pradan.issdc.gov.in/ch2/  | ISSDC / ISRO            |
| 2. Chandrayaan-2 Science Data       | https://www.issdc.gov.in/         | ISSDC / ISRO            |
| 3. ISRO Mission Science Information | https://www.isro.gov.in/          | ISRO                    |
| 4. NASA LRO LROC-NAC PDS Archive    | https://ode.rsl.wustl.edu/moon/   | NASA PDS / WUSTL / ASU  |
| 5. LROC QuickMap Interactive        | https://quickmap.lroc.asu.edu/    | Arizona State University|
| 6. JAXA SELENE (Kaguya) TC Archive  | https://darts.isas.jaxa.jp/       | JAXA / DARTS / ISAS     |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Sensor Verification & Capability Matrix

| Parameter | Chandrayaan-2 OHRC | Chandrayaan-2 TMC-2 | Chandrayaan-2 IIRS | NASA LRO NAC (Reference) | JAXA Kaguya TC (Reference) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Full Sensor Name** | Orbiter High Resolution Camera | Terrain Mapping Camera-2 | Imaging Infrared Spectrometer | Narrow Angle Camera | Terrain Camera |
| **Operating Agency** | ISRO (India) | ISRO (India) | ISRO (India) | NASA / ASU (USA) | JAXA (Japan) |
| **Spectral Regime** | Panchromatic (450–900 nm) | Panchromatic (500–850 nm) | Hyperspectral (0.8–5.0 µm, 256 bands) | Panchromatic (400–750 nm) | Panchromatic (430–850 nm) |
| **Spatial Resolution (GSD)** | **0.25 m to 0.32 m/pixel** (at 100 km orbit) | **5.0 m/pixel** (Nadir, Fore, Aft) | **80 m to 250 m/pixel** | **0.5 m to 1.0 m/pixel** | **10.0 m/pixel** |
| **Swath Width** | ~12 km | ~20 km | ~20 km | ~5 km | ~35 km |
| **Viewing Geometry** | Nadir (Pointable $\pm 25^\circ$) | Triplet: Fore ($+26^\circ$), Nadir ($0^\circ$), Aft ($-26^\circ$) | Nadir | Symmetrical stereo pair ($\pm 2.85^\circ$) | Stereo Triplet |
| **Data Format Standard** | PDS4 (`.xml` + `.tif`/`.img`) | PDS4 (`.xml` + `.tif`) | PDS4 (`.xml` + `.qub`/`.cub`) | PDS3/PDS4 (`.lbl`/`.xml` + `.img`) | PDS3 (`.lbl` + `.img`) |
| **Projection / Reference Frame** | Moon 2000 IAU / Simple Cylindrical / Equirectangular | Moon 2000 IAU / Polar Stereographic | Moon 2000 IAU / Simple Cylindrical | Moon 2000 IAU / Equirectangular | Moon 2000 IAU / Simple Cylindrical |
| **Illumination Geometry in Label** | `sun_azimuth`, `incidence_angle`, `phase_angle`, `emission_angle` | Full stereo solar angles per frame | Solar angles & thermal radiance parameters | Backplane incidence, emission, phase per-pixel (`SDRPHO`) | Incidence, emission, phase in label header |
| **Overlapping Scene Mechanics** | Repeated orbital passes over high-interest regions (e.g., South Pole, Boguslawsky, Manzi) | Contiguous global strips; Fore/Nadir/Aft intra-pass overlap | Global strip mapping co-aligned with TMC-2 footprints | Repeated coverage under varying solar azimuth ($0^\circ \leftrightarrow 360^\circ$) | Multi-orbit global coverage |
| **Licensing & Legal Status** | ISRO Open Science Data Policy (Free for research/education) | ISRO Open Science Data Policy (Free for research/education) | ISRO Open Science Data Policy (Free for research/education) | NASA Open Data / Public Domain (CC0) | JAXA Open Data Policy |
| **Experimental Suitability** | High-resolution target; fine hazard & crater matching | Intermediate scale anchor & DEM stereo matching | Multimodal / spectral absorption testing | Primary ground-truth cross-validation | Global baseline context |

---

## 3. Data Access Constraints & Reproducible Acquisition Procedure

### 3.1 Authentication & Technical Limitations
- **ISSDC PRADAN**: Access to raw Chandrayaan-2 PDS4 data requires user authentication (registered email + password). The portal utilizes dynamic session cookies, tokenized requests, and Captcha verification.
- **Rule Compliance**: In accordance with ISRO terms of use and responsible AI safety guidelines, **no automated web scraping, headless bot bypass, or credential hardcoding** is employed.
- **Acquisition Paradigm**: We establish a standard, fully documented manual download protocol for raw PRADAN products, paired with an automated offline validation, verification, and ingestion pipeline.

### 3.2 Standard Operating Procedure (SOP) for PRADAN Data Acquisition:
1. **Account Registration**: Navigate to [https://pradan.issdc.gov.in/ch2/](https://pradan.issdc.gov.in/ch2/) and log in with verified credentials.
2. **Search Parameters**:
   - *Target Region*: Select Lunar South Pole ($70^\circ\text{S} - 90^\circ\text{S}$) or Equatorial Craters (e.g., Tycho, Copernicus, Boguslawsky).
   - *Payload Selection*: Choose `OHRC`, `TMC-2`, and `IIRS`.
   - *Processing Level*: Select `Level-2 MAP` (Map-projected GeoTIFF) for direct correspondence experiments, or `Level-1 CAL` (Radiometrically calibrated) for raw sensor model testing.
3. **Download Package**: Download the product package containing both the `.xml` PDS4 label and the `.tif` / `.img` image data.
4. **Local Repository Ingestion**: Place downloaded products into the local workspace staging directory:
   ```
   data/raw/
   ├── ohrc/
   ├── tmc2/
   ├── iirs/
   └── reference/
   ```
5. **Automated Ingestion & Validation**: Run the dataset ingestion script:
   ```bash
   python -m src.dataset.ingest_pipeline --input data/raw/ --benchmark data/benchmark/
   ```

---

## 4. Benchmark Dataset Composition (`Ch-2-MatchBench`)

```
data/
└── benchmark/
    ├── suite_a_intra_sensor/
    │   ├── pair_01_tmc2_nadir_nadir/       # Same orbit, small delta-azimuth (< 10°)
    │   └── pair_02_ohrc_ohrc_same_sun/     # High-res intra-sensor baseline
    ├── suite_b_sun_angle/
    │   ├── pair_03_ohrc_opposing_sun/      # Solar azimuth shift Δϕ = 180°
    │   └── pair_04_tmc2_morning_afternoon/ # Solar azimuth shift Δϕ = 120°, incidence > 65°
    ├── suite_c_scale_disparity/
    │   ├── pair_05_tmc2_to_ohrc_1_16/      # 5.0m/px to 0.31m/px resolution jump
    │   └── pair_06_tmc2_to_ohrc_1_20/      # 5.0m/px to 0.25m/px resolution jump
    ├── suite_d_cross_modal/
    │   ├── pair_07_iirs_swir_to_tmc2/      # IIRS 2.0µm band vs TMC-2 panchromatic
    │   └── pair_08_iirs_swir_to_ohrc/      # IIRS 1.5µm band vs OHRC panchromatic
    └── suite_e_difficult_terrain/
        ├── pair_09_flat_maria_regolith/    # Extremely low contrast, feature-sparse
        └── pair_10_dense_crater_cluster/   # Heavy overlapping crater morphology
```

---

## 5. Metadata Schema & Provenance Tracking

Every dataset file ingested into `Ch-2-MatchBench` automatically generates an immutable provenance manifest (`provenance.json`) containing:
- **`product_id`**: Official ISRO / NASA PDS product identifier.
- **`sensor_id`**: `CH2_OHRC`, `CH2_TMC2`, `CH2_IIRS`, `LRO_NAC`, or `SELENE_TC`.
- **`sha256_checksum`**: Cryptographic hash verifying raw file integrity.
- **`acquisition_time_utc`**: ISO-8601 acquisition timestamp.
- **`solar_geometry`**:
  - `sun_azimuth_deg`: $[0.0^\circ, 360.0^\circ]$
  - `incidence_angle_deg`: $[0.0^\circ, 90.0^\circ]$
  - `emission_angle_deg`: $[0.0^\circ, 90.0^\circ]$
  - `phase_angle_deg`: $[0.0^\circ, 180.0^\circ]$
- **`spatial_bounds`**:
  - `min_lat`, `max_lat`, `min_lon`, `max_lon` (Degrees)
  - `ground_sampling_distance_m`: Meters per pixel.
- **`projection`**: IAU Moon 2000 projection string / WKT.
- **`source_url`**: Official portal origin.
