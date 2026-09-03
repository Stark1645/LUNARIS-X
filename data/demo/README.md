# SIH 2026 (SIH26166) — Demonstration Dataset Registry

This folder contains curated demonstration image pairs representing the critical evaluation challenges defined in the SIH26166 specification. All images are uncompressed, pristine copies of the verified benchmark test suite with cryptographic SHA-256 provenance tracking.

---

## 1. Demonstration Pair Catalog

| Pair Directory | Challenge Type | Source Image | Reference Image | Sensor / Payload | GSD (Src / Ref) | Scale Ratio | Ground Truth | Provenance Category |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`pair_01/`** | Baseline Intra-Sensor | `source.png` ($512\times 512$) | `reference.png` ($512\times 512$) | TMC-2 $\leftrightarrow$ TMC-2 | $5.0\text{ m} / 5.0\text{ m}$ | $1.0\times$ | Exists (`ground_truth.json`) | `SYNTHETIC_BENCHMARK` |
| **`pair_03/`** | $180^\circ$ Solar Shadow Reversal | `source.png` ($512\times 512$) | `reference.png` ($512\times 512$) | TMC-2 $\leftrightarrow$ TMC-2 | $5.0\text{ m} / 5.0\text{ m}$ | $1.0\times$ | Exists (`ground_truth.json`) | `SYNTHETIC_BENCHMARK` |
| **`pair_04/`** | $4\times$ Scale Disparity | `source.png` ($128\times 128$) | `reference.png` ($512\times 512$) | TMC-2 $\leftrightarrow$ High-Res | $5.0\text{ m} / 1.25\text{ m}$ | $4.0\times$ | Exists (`ground_truth.json`) | `SYNTHETIC_BENCHMARK` |
| **`pair_06/`** | $20\times$ Extreme Scale Gap | `source.png` ($26\times 26$) | `reference.png` ($512\times 512$) | TMC-2 $\leftrightarrow$ OHRC | $5.0\text{ m} / 0.25\text{ m}$ | $20.0\times$ | Exists (`ground_truth.json`) | `SYNTHETIC_BENCHMARK` |
| **`pair_07/`** | Cross-Modal Radiometric | `source.png` ($512\times 512$) | `reference.png` ($512\times 512$) | IIRS SWIR $\leftrightarrow$ TMC-2 Pan | $5.0\text{ m} / 5.0\text{ m}$ | $1.0\times$ | Exists (`ground_truth.json`) | `SYNTHETIC_BENCHMARK` |
| **`pair_08/`** | Low-Texture Basaltic Maria | `source.png` ($512\times 512$) | `reference.png` ($512\times 512$) | TMC-2 $\leftrightarrow$ TMC-2 | $5.0\text{ m} / 5.0\text{ m}$ | $1.0\times$ | Exists (`ground_truth.json`) | `SYNTHETIC_BENCHMARK` |

---

## 2. Authentic ISRO PRADAN Flight Archive Guidelines

- **Workspace Status**: Native ISRO PRADAN PDS4 mission archives (`AUTHENTIC_CH2_PRADAN`) are **NOT STORED** locally in this repository.
- **ISRO ISSDC PRADAN Archive Access**:
  - URL: [https://pradan.issdc.gov.in](https://pradan.issdc.gov.in)
  - Mission: Chandrayaan-2 Orbiter
  - Recommended TMC-2 Product ID: `ch2_tmc_ncn_20200115t041042316_d_img_d18.xml`
  - Recommended OHRC Product ID: `ch2_ohr_ncn_20200115t041042316_d_img_d18.xml`
- **Integrity Rule**: Synthetic pairs in this directory must never be represented as authentic orbital flight data.

---

## 3. UI Demonstration Input Guide

For each test pair, upload:
- **`source.png`** as **Source (Moving Image)**
- **`reference.png`** as **Reference (Fixed Image)**
- Select algorithm: **Proposed Method (AMSR)**
- Transformation Model: **Homography (8-DOF)** (or **Affine (6-DOF)** for `pair_06`)
- Click **Execute Registration**
