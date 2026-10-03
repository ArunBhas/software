# EM-Material-Studio

**Electromagnetic Material, Shielding & Microwave Absorption Studio**

A comprehensive, scientific GUI application for electromagnetic (EM) materials research, electromagnetic interference (EMI) shielding effectiveness, complex constitutive parameter analysis, and microwave absorption simulation.

Developed by **Arun B**, School of Physics, University of Hyderabad.  
Website: [https://sites.google.com/view/arunb/home](https://sites.google.com/view/arunb/home)

---

## Overview

**EM-Material-Studio** unifies electromagnetic material characterization and microwave performance simulation into a single, high-performance platform. It processes experimental Vector Network Analyzer (VNA) data across microwave frequency bands (X-band, Ku-band, etc.) to analyze:
- **EMI Shielding Effectiveness** ($\text{SE}_T$, $\text{SE}_R$, $\text{SE}_A$)
- **Microwave Reflection Loss (REL)** as a function of frequency and thickness
- **Complex Permittivity ($\varepsilon_r$) & Permeability ($\mu_r$)**
- **Dielectric & Magnetic Loss Mechanisms** (Loss tangents, Cole-Cole Debye relaxation, AC conductivity, and attenuation constant)

---

## Core Computational Modules

### 1. Reflection Loss (REL) & Impedance Matching Simulator
- **Model**: Transmission Line Theory for Single-Layer Absorber backed by a Perfect Electric Conductor (PEC).
- **Calculations**:
  - Complex input impedance ($Z_{in}$) and normalized impedance ($Z_{norm} = Z_{in}/Z_0$)
  - Complex reflection coefficient $\Gamma$ ($S_{11}$) and power reflectance $R$
  - Reflection Loss ($\text{REL} = 10 \log_{10} R = 20 \log_{10}|\Gamma|$)
  - Simulations over user-defined thickness ranges (e.g. 0 to 10 mm) or custom discrete thicknesses
- **Outputs**:
  - **Publication-Grade 3D Surface Plot** (Frequency vs. Thickness vs. REL with projected 2D colormap, 300 DPI)
  - **2D Frequency vs. REL Spectral Curves** with multi-thickness legend
  - **Thickness vs. Frequency 2D Contour Plot**
  - Structured Excel workbooks: `Reflection Loss vs thickness Simulation data.xlsx` and `Frequency_vs_REL_Data.xlsx`

### 2. EMI Shielding Effectiveness (SE) Calculator
- **Model**: S-parameter power-balance method for two-port waveguide/coaxial fixtures.
- **Calculations**:
  - Power coefficients: Reflectance $R = |S_{11}|^2$, Transmittance $T = |S_{21}|^2$, Absorptance $A = 1 - R$
  - Shielding due to Reflection: $\text{SE}_R = 10 \log_{10}(1 - R)$
  - Shielding due to Absorption: $\text{SE}_A = 10 \log_{10}\left(\frac{T}{1 - R}\right)$
  - **Total Shielding Effectiveness**: $\text{SE}_T = \text{SE}_R + \text{SE}_A = 10 \log_{10}(|S_{21}|^2)$
  - Experimental diagnostic Return Loss ($10 \log_{10} R$) and Insertion Loss ($10 \log_{10} T$)
- **Outputs**:
  - Dual y-axis publication graph with automatic sample thickness extraction from metadata
  - Numerical results exported to `*_SE_calculation.xlsx`

### 3. Dielectric, Magnetic & Loss Mechanism Analyzer
- **Calculations**:
  - Real and imaginary relative permittivity ($\varepsilon_r', \varepsilon_r''$)
  - Real and imaginary relative permeability ($\mu_r', \mu_r''$)
  - Dielectric loss tangent ($\tan \delta_e = \varepsilon'' / \varepsilon'$) & Magnetic loss tangent ($\tan \delta_m = \mu'' / \mu'$)
  - **Cole-Cole Plot** ($\varepsilon'$ vs $\varepsilon''$) for identifying Debye dielectric relaxation processes
  - **AC Electrical Conductivity**: $\sigma_{ac} = 2 \pi f \varepsilon_0 \varepsilon''$ (S/m)
  - **Microwave Attenuation Constant**: $\alpha = \frac{\sqrt{2}\pi f}{c} \sqrt{A + \sqrt{A^2 + B^2}}$ (Np/m)
- **Outputs**:
  - 7 individual high-resolution plots (`_er_ei_plot.png`, `_ur_ui_plot.png`, `_er_ur_plot.png`, `_tandelta_magnetic_plot.png`, `_cole-cole_plot.png`, `_ac_conductivity_plot.png`, `_attenuation_constant_plot.png`)
  - Exported Excel workbooks for AC conductivity and attenuation constant

---

## Governing Equations

Every equation, physical assumption, and derivation implemented in the software is documented with LaTeX math in:  
📄 **[EQUATIONS.md](EQUATIONS.md)**

---

## Repository Structure

```text
├── em_material_studio.py                 # Main scientific GUI application
├── sample_data/                          # Downsampled test datasets (21 data points)
│   ├── sample_permittivity_permeability.csv  # CSV structure for REL & Dielectric modules
│   ├── sample_s_parameters.txt               # TXT structure for SE Calculator
│   └── README.md                             # Guide to headers and columns
├── EQUATIONS.md                          # Comprehensive physical & mathematical derivations
├── requirements.txt                      # Python dependencies
├── README.md                             # Project documentation
└── .gitignore                            # Excludes outputs, build files, and cache
```

---

## Installation & Usage

### 1. Requirements
- Python 3.8 or newer
- Operating System: Windows, macOS, or Linux

### 2. Setup
Clone the repository and install required packages:

```bash
git clone https://github.com/<your-username>/EM-Material-Studio.git
cd EM-Material-Studio
pip install -r requirements.txt
```

### 3. Launching the Software
Run the Python application:

```bash
python em_material_studio.py
```

### 4. Standalone Windows Executable
A compiled standalone binary (`EM-Material-Studio.exe` / `REL_Simulation_Software.exe`) is available under **[GitHub Releases](../../releases)** for Windows users without a Python environment.

---

## Sample Data & File Formats

Pre-formatted 21-point test datasets across the microwave X-band (8.2 GHz – 12.4 GHz) are provided in [`sample_data/`](sample_data/):
- **`.csv` format**: Permittivity and permeability data (7 header lines + columns `frequency, e', e'', u', u''`).
- **`.txt` format**: Two-port S-parameters data (6 header lines with sample thickness + columns `frequency, s11r, s11i, s21r, s21i, s12r, s12i, s22r, s22i`).

Refer to [`sample_data/README.md`](sample_data/README.md) for full details.

---

## Citation & Acknowledgment

If you find **EM-Material-Studio** useful in your research or publications, please cite:

```bibtex
@misc{arun2026emmaterialstudio,
  author = {Arun, B.},
  title = {EM-Material-Studio: Electromagnetic Material, Shielding & Absorption Studio},
  year = {2026},
  publisher = {GitHub},
  howpublished = {\url{https://sites.google.com/view/arunb/home}},
  institution = {School of Physics, University of Hyderabad}
}
```

**Developer**: Arun B  
**Affiliation**: School of Physics, University of Hyderabad, India  
**Website**: [https://sites.google.com/view/arunb/home](https://sites.google.com/view/arunb/home)
