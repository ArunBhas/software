# Sample Data Structure Guide

This directory contains downsampled sample datasets (21 data points across the X-band: 8.2 GHz – 12.4 GHz) to illustrate the exact file format and structure required by **EM-Material-Studio (Electromagnetic Material, Shielding & Absorption Studio)**.

---

## 1. Permittivity & Permeability Data (`.csv`)

- **Sample file**: `sample_permittivity_permeability.csv` (or any `.csv` placed in your measurement directory)
- **Applicable Modules**:
  1. **Reflection Loss (REL) Simulation** (Thickness dependent)
  2. **Dielectric & Cole-Cole Analysis**

### File Structure:
- **Lines 1–5**: Instrument metadata / notes (e.g. Agilent/Keysight 85071 Material Measurement Software output).
- **Line 6**: Blank line.
- **Line 7**: Column header row (`frequency,e',e'',u',u''`).
- **Lines 8 onwards**: Numerical data rows.

### Column Definitions:
| Column | Name | Description | Units / Notes |
| :--- | :--- | :--- | :--- |
| 1 | `frequency` | Measurement frequency | Hertz (Hz), e.g. `8.200000e+09` for 8.2 GHz |
| 2 | `e'` | Real relative permittivity ($\varepsilon_r'$) | Dimensionless |
| 3 | `e''` | Imaginary relative permittivity ($\varepsilon_r''$, dielectric loss factor) | Dimensionless |
| 4 | `u'` | Real relative permeability ($\mu_r'$) | Dimensionless |
| 5 | `u''` | Imaginary relative permeability ($\mu_r''$, magnetic loss factor) | Dimensionless |

```csv
85071 Material Measurement Software E07.02.24
Agilent Technologies,E8361C,US49010187,A.09.42.12
Title:,Title
Sub Title:,SubTitle
Date:,"Friday, January 01, 1988 03:24:05"

frequency,e',e'',u',u''
8200000000.0000,  12.6066,   0.3516,   0.9648,   0.1371
8410000000.0000,  12.6421,   0.2664,   0.9590,   0.1404
...
```

---

## 2. S-Parameters Data (`.txt`)

- **Sample file**: `sample_s_parameters.txt` (or any `.txt` placed in your measurement directory)
- **Applicable Module**:
  - **Shielding Effectiveness (SE) Calculator**

### File Structure:
- **Line 1**: `Sample holder length =\t<value> meters`
- **Line 2**: `Sample thickness =\t<value> meters` *(Crucial: used to extract physical thickness for SE analysis)*
- **Line 3**: `Distance to sample =\t<value> meters`
- **Line 4**: `Sample holder Fco =\t<value> GHz`
- **Line 5**: Blank line.
- **Line 6**: Tab-separated column headers (`frequency\ts11r\ts11i\ts21r\ts21i\ts12r\ts12i\ts22r\ts22i`).
- **Lines 7 onwards**: Tab-separated numerical data rows.

### Column Definitions:
| Column | Name | Description |
| :--- | :--- | :--- |
| 1 | `frequency` | Measurement frequency in Hz |
| 2, 3 | `s11r`, `s11i` | Real and imaginary parts of port-1 reflection parameter $S_{11}$ |
| 4, 5 | `s21r`, `s21i` | Real and imaginary parts of forward transmission parameter $S_{21}$ |
| 6, 7 | `s12r`, `s12i` | Real and imaginary parts of reverse transmission parameter $S_{12}$ |
| 8, 9 | `s22r`, `s22i` | Real and imaginary parts of port-2 reflection parameter $S_{22}$ |

```text
Sample holder length =	9.7800e-003 meters
Sample thickness =	3.9700e-003 meters
Distance to sample =	0.0000e+000 meters
Sample holder Fco =	6.5600e+000 GHz
 
frequency	s11r	s11i	s21r	s21i	s12r	s12i	s22r	s22i
8200000000.0000	  -0.7774	   0.1987	  -0.3290	  -0.1767	  -0.3292	  -0.1766	  -0.1221	   0.8002
8410000000.0000	  -0.7432	   0.2142	  -0.3664	  -0.1515	  -0.3666	  -0.1515	  -0.0330	   0.7861
...
```
