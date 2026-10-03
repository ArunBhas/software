# Theoretical Foundations & Mathematical Equations
# EM-Material-Studio

This document details all the governing physical laws, electromagnetic wave equations, and mathematical derivations implemented in **EM-Material-Studio (Electromagnetic Material, Shielding & Absorption Studio)**.

---

## Table of Contents
1. [Physical Constants & Fundamental Notation](#1-physical-constants--fundamental-notation)
2. [Module 1: Reflection Loss (REL) & Input Impedance Simulation](#2-module-1-reflection-loss-rel--input-impedance-simulation)
   - [Transmission Line Theory for Single-Layer Absorber](#transmission-line-theory-for-single-layer-absorber)
   - [Normalized Input Impedance ($Z_{norm}$)](#normalized-input-impedance-z_norm)
   - [Reflection Coefficient ($\Gamma$ or $S_{11}$)](#reflection-coefficient-gamma-or-s_11)
   - [Reflection Loss (REL in dB)](#reflection-loss-rel-in-db)
   - [Quarter-Wavelength ($\lambda/4$) Matching Condition](#quarter-wavelength-lambda4-matching-condition)
3. [Module 2: Electromagnetic Shielding Effectiveness (SE)](#3-module-2-electromagnetic-shielding-effectiveness-se)
   - [Two-Port S-Parameters & Power Coefficients](#two-port-s-parameters--power-coefficients)
   - [Reflectance ($R$), Transmittance ($T$), and Absorptance ($A$)](#reflectance-r-transmittance-t-and-absorptance-a)
   - [Shielding due to Reflection ($\text{SE}_R$)](#shielding-due-to-reflection-textse_r)
   - [Shielding due to Absorption ($\text{SE}_A$)](#shielding-due-to-absorption-textse_a)
   - [Total Shielding Effectiveness ($\text{SE}_T$)](#total-shielding-effectiveness-textse_t)
   - [Return Loss and Insertion Loss](#return-loss-and-insertion-loss)
4. [Module 3: Dielectric, Magnetic & Loss Characterization](#4-module-3-dielectric-magnetic--loss-characterization)
   - [Complex Permittivity and Permeability](#complex-permittivity-and-permeability)
   - [Dielectric and Magnetic Loss Tangents](#dielectric-and-magnetic-loss-tangents)
   - [Cole-Cole Semicircles (Debye Relaxation)](#cole-cole-semicircles-debye-relaxation)
   - [AC Electrical Conductivity ($\sigma_{ac}$)](#ac-electrical-conductivity-sigma_ac)
   - [Attenuation Constant ($\alpha$)](#attenuation-constant-alpha)
5. [References](#5-references)

---

## 1. Physical Constants & Fundamental Notation

The software uses exact SI physical constants:

| Symbol | Description | Exact / Standard Value | SI Unit |
| :---: | :--- | :--- | :---: |
| $c$ | Speed of light in vacuum | $299,792,458$ | $\text{m/s}$ |
| $\varepsilon_0$ | Permittivity of free space | $8.854187817 \times 10^{-12}$ | $\text{F/m}$ |
| $\mu_0$ | Permeability of free space | $4\pi \times 10^{-7} \approx 1.256637 \times 10^{-6}$ | $\text{H/m}$ |
| $Z_0$ | Characteristic impedance of free space | $\sqrt{\frac{\mu_0}{\varepsilon_0}} \approx 377.0$ | $\Omega$ |

---

## 2. Module 1: Reflection Loss (REL) & Input Impedance Simulation

### Transmission Line Theory for Single-Layer Absorber
Consider a uniform planar electromagnetic absorbing layer of physical thickness $d$ (in meters, where $d = t / 1000$ from thickness $t$ in mm) backed by an ideal Perfect Electric Conductor (PEC, such as a continuous metal plate), with normal electromagnetic wave incidence from air ($Z_0$).

The complex relative permittivity and permeability of the material are:

$$\varepsilon_r = \varepsilon_r' - j \varepsilon_r''$$

$$\mu_r = \mu_r' - j \mu_r''$$

where $\varepsilon_r'$ and $\mu_r'$ represent energy storage, while $\varepsilon_r''$ and $\mu_r''$ represent dielectric and magnetic dissipation losses, respectively.

### Normalized Input Impedance ($Z_{norm}$)
According to transmission line impedance transformation with a short-circuit boundary ($Z_L = 0$ at the PEC interface):

$$Z_{in} = Z_c \tanh(\gamma d)$$

Where:
- Characteristic impedance of the medium: $Z_c = Z_0 \sqrt{\frac{\mu_r}{\varepsilon_r}}$
- Complex propagation constant: $\gamma = j \frac{2\pi f}{c}\sqrt{\mu_r \varepsilon_r}$

In the simulation software, the complex argument $x$ is defined as:

$$x = -j \left( \frac{2\pi f d}{c} \right) \sqrt{\mu_r \varepsilon_r}$$

The **normalized input impedance** $Z_{norm}$ is then given by:

$$Z_{norm} = \frac{Z_{in}}{Z_0} = \sqrt{\frac{\mu_r}{\varepsilon_r}} \tanh(x)$$

### Reflection Coefficient ($\Gamma$ or $S_{11}$)
At the front air-absorber interface, the voltage reflection coefficient $\Gamma$ ($S_{11}$) is:

$$\Gamma = S_{11} = \frac{Z_{in} - Z_0}{Z_{in} + Z_0} = \frac{Z_{norm} - 1}{Z_{norm} + 1}$$

### Reflection Loss (REL in dB)
The power reflectance $R$ is the squared magnitude of the reflection coefficient:

$$R = |\Gamma|^2 = |S_{11}|^2$$

The Reflection Loss ($\text{REL}$), expressed in decibels ($\text{dB}$), is calculated as:

$$\text{REL (dB)} = 10 \log_{10}(R) = 20 \log_{10}|\Gamma| = 20 \log_{10} \left| \frac{Z_{norm} - 1}{Z_{norm} + 1} \right|$$

#### Practical Interpretation:
- $\text{REL} = -10\ \text{dB} \implies 90\%$ of incident electromagnetic energy is absorbed.
- $\text{REL} = -20\ \text{dB} \implies 99\%$ of incident electromagnetic energy is absorbed.
- $\text{REL} = -30\ \text{dB} \implies 99.9\%$ of incident electromagnetic energy is absorbed.
- **Effective Absorption Bandwidth (EAB)**: The continuous frequency range where $\text{REL} \le -10\ \text{dB}$.

### Quarter-Wavelength ($\lambda/4$) Matching Condition
The minimum reflection loss (maximum absorption peak) occurs when the reflected waves from the front interface and the back metal interface interfere destructively (phase difference of $\pi$ radians). The matching thickness $t_m$ satisfies:

$$t_m = \frac{n c}{4 f_m \sqrt{|\mu_r \varepsilon_r|}} = \frac{n \lambda_0}{4 \sqrt{|\mu_r \varepsilon_r|}} \quad (n = 1, 3, 5, \dots)$$

---

## 3. Module 2: Electromagnetic Shielding Effectiveness (SE)

When evaluating electromagnetic interference (EMI) shielding with a Vector Network Analyzer (VNA) in a 2-port waveguide or coaxial fixture, the scattering parameters ($S_{11}$, $S_{21}$, $S_{12}$, $S_{22}$) are recorded as complex numbers:

$$S_{ij} = S_{ij,r} + j S_{ij,i}$$

### Two-Port S-Parameters & Power Coefficients
The power magnitudes are computed as:

$$|S_{11}|^2 = (S_{11,r})^2 + (S_{11,i})^2$$

$$|S_{21}|^2 = (S_{21,r})^2 + (S_{21,i})^2$$

$$|S_{12}|^2 = (S_{12,r})^2 + (S_{12,i})^2$$

$$|S_{22}|^2 = (S_{22,r})^2 + (S_{22,i})^2$$

### Reflectance ($R$), Transmittance ($T$), and Absorptance ($A$)
From power balance:
- **Power Reflectance ($R$)**:
  $$R = |S_{11}|^2$$
- **Power Transmittance ($T$)**:
  $$T = |S_{21}|^2$$
- **Effective Power Absorptance ($A$)**:
  $$A = 1 - R = 1 - |S_{11}|^2$$

Here, $A$ represents the fraction of power transmitted across the first interface into the material.

The transmission factor relative to inside power ($B$) is:

$$B = \frac{T}{1 - R} = \frac{T}{A}$$

### Shielding due to Reflection ($\text{SE}_R$)
The reflection shielding loss represents power reflected at the input boundary:

$$\text{SE}_R = 10 \log_{10}(1 - R) = 10 \log_{10}(1 - |S_{11}|^2)$$

### Shielding due to Absorption ($\text{SE}_A$)
The absorption shielding loss represents attenuation of the wave propagating through the material:

$$\text{SE}_A = 10 \log_{10}\left( \frac{T}{1 - R} \right) = 10 \log_{10}\left( \frac{|S_{21}|^2}{1 - |S_{11}|^2} \right)$$

### Total Shielding Effectiveness ($\text{SE}_T$)
The total shielding effectiveness ($\text{SE}_T$) is the sum of reflection and absorption:

$$\text{SE}_T = \text{SE}_R + \text{SE}_A$$

By algebraic identity:

$$\text{SE}_T = 10 \log_{10}(1 - R) + 10 \log_{10}\left(\frac{T}{1 - R}\right) = 10 \log_{10}(T) = 10 \log_{10}(|S_{21}|^2)$$

*(Note: When total shielding $\text{SE}_T \ge 10 - 15\ \text{dB}$, multiple internal reflections $\text{SE}_M$ are negligible and absorb within the specimen).*

### Return Loss and Insertion Loss
For experimental network diagnostics:

$$\text{Return Loss (dB)} = 10 \log_{10}(R) = 10 \log_{10}(|S_{11}|^2)$$

$$\text{Insertion Loss (dB)} = 10 \log_{10}(T) = 10 \log_{10}(|S_{21}|^2)$$

---

## 4. Module 3: Dielectric, Magnetic & Loss Characterization

### Complex Permittivity and Permeability
Materials in microwave regimes are characterized by:

$$\varepsilon_r = \varepsilon_r' - j \varepsilon_r''$$

$$\mu_r = \mu_r' - j \mu_r''$$

### Dielectric and Magnetic Loss Tangents
Loss tangents indicate the ratio of dissipated energy to stored energy per cycle:

- **Dielectric Loss Tangent ($\tan \delta_e$)**:
  $$\tan \delta_e = \frac{\varepsilon_r''}{\varepsilon_r'}$$

- **Magnetic Loss Tangent ($\tan \delta_m$)**:
  $$\tan \delta_m = \frac{\mu_r''}{\mu_r'}$$

### Cole-Cole Semicircles (Debye Relaxation)
Dielectric relaxation processes (dipole polarization, interface polarization, Maxwell-Wagner effect) are modeled using Debye relaxation theory:

$$\varepsilon_r(\omega) = \varepsilon_\infty + \frac{\varepsilon_s - \varepsilon_\infty}{1 + j \omega \tau}$$

Where:
- $\varepsilon_s$: Static dielectric permittivity at zero frequency.
- $\varepsilon_\infty$: Optical dielectric permittivity at infinite frequency.
- $\tau$: Relaxation time.
- $\omega = 2\pi f$: Angular frequency.

Separating into real ($\varepsilon'$) and imaginary ($\varepsilon''$) components:

$$\varepsilon' = \varepsilon_\infty + \frac{\varepsilon_s - \varepsilon_\infty}{1 + \omega^2 \tau^2}$$

$$\varepsilon'' = \frac{(\varepsilon_s - \varepsilon_\infty) \omega \tau}{1 + \omega^2 \tau^2}$$

Eliminating $\omega \tau$ between the two equations yields the equation of a circle centered at $\left( \frac{\varepsilon_s + \varepsilon_\infty}{2}, 0 \right)$:

$$\left( \varepsilon' - \frac{\varepsilon_s + \varepsilon_\infty}{2} \right)^2 + (\varepsilon'')^2 = \left( \frac{\varepsilon_s - \varepsilon_\infty}{2} \right)^2$$

Each semicircular arc in the plot of $\varepsilon'$ versus $\varepsilon''$ corresponds to a distinct Debye relaxation process.

### AC Electrical Conductivity ($\sigma_{ac}$)
From Maxwell's curl equation for magnetic fields:

$$\nabla \times \mathbf{H} = \mathbf{J} + \frac{\partial \mathbf{D}}{\partial t} = (\sigma_{dc} + j \omega \varepsilon_0 \varepsilon_r) \mathbf{E} = \left( \sigma_{dc} + \omega \varepsilon_0 \varepsilon_r'' \right) \mathbf{E} + j \omega \varepsilon_0 \varepsilon_r' \mathbf{E}$$

The frequency-dependent AC conductivity ($\sigma_{ac}$) arising from dielectric dissipation is:

$$\sigma_{ac} = \omega \varepsilon_0 \varepsilon_r'' = 2 \pi f \varepsilon_0 \varepsilon_r'' \quad (\text{S/m})$$

where:
- $f$ is frequency in $\text{Hz}$
- $\varepsilon_0 = 8.854 \times 10^{-12}\ \text{F/m}$
- $\varepsilon_r''$ is imaginary permittivity

### Attenuation Constant ($\alpha$)
The electromagnetic wave propagation constant $\gamma$ in a lossy medium is:

$$\gamma = \alpha + j \beta = j \frac{2\pi f}{c} \sqrt{\mu_r \varepsilon_r}$$

where $\alpha$ is the attenuation constant ($\text{Np/m}$) and $\beta$ is the phase constant ($\text{rad/m}$).

Expanding the product $\mu_r \varepsilon_r$:

$$\mu_r \varepsilon_r = (\mu' - j\mu'')(\varepsilon' - j\varepsilon'') = (\mu' \varepsilon' - \mu'' \varepsilon'') - j (\mu'' \varepsilon' + \mu' \varepsilon'')$$

Let:
$$A = \mu'' \varepsilon'' - \mu' \varepsilon'$$

$$B = \mu'' \varepsilon' + \mu' \varepsilon''$$

Squaring $\gamma = \alpha + j\beta$:

$$\gamma^2 = \alpha^2 - \beta^2 + 2j\alpha\beta = -\left(\frac{2\pi f}{c}\right)^2 (\mu_r \varepsilon_r) = \left(\frac{2\pi f}{c}\right)^2 (A - jB)$$

Equating real and imaginary parts:
1. $\alpha^2 - \beta^2 = \left(\frac{2\pi f}{c}\right)^2 A$
2. $2\alpha\beta = -\left(\frac{2\pi f}{c}\right)^2 B \implies (\alpha^2 + \beta^2)^2 = (\alpha^2 - \beta^2)^2 + (2\alpha\beta)^2 = \left(\frac{2\pi f}{c}\right)^4 (A^2 + B^2)$

Therefore:
$$\alpha^2 + \beta^2 = \left(\frac{2\pi f}{c}\right)^2 \sqrt{A^2 + B^2}$$

Adding $\alpha^2 - \beta^2$ to $\alpha^2 + \beta^2$:

$$2 \alpha^2 = \left(\frac{2\pi f}{c}\right)^2 \left( A + \sqrt{A^2 + B^2} \right)$$

Taking the square root gives the closed-form expression used in the software:

$$\alpha = \frac{\sqrt{2}\pi f}{c} \sqrt{A + \sqrt{A^2 + B^2}} \quad (\text{Np/m})$$

The attenuation constant $\alpha$ measures the rate at which electromagnetic energy is dissipated into heat as it travels through the absorber material.

---

## 5. References

1. **David M. Pozar**, *Microwave Engineering*, 4th Edition, John Wiley & Sons, 2012.
2. **Y. Naito and K. Suetake**, "Application of Ferrite to Electromagnetic Wave Absorber and its Characteristics," *IEEE Transactions on Microwave Theory and Techniques*, vol. 19, no. 1, pp. 65–72, 1971.
3. **P. S. Neelakanta**, *Handbook of Microwave Materials: Characterization and Analysis*, CRC Press, 1995.
4. **M. S. Cao, et al.**, "Advanced materials for electromagnetic shielding: Mechanisms, performance, and applications," *Journal of Materials Chemistry C*, 2018.
5. **K. S. Cole and R. H. Cole**, "Dispersion and absorption in dielectrics I. Alternating current characteristics," *The Journal of Chemical Physics*, vol. 9, no. 4, pp. 341–351, 1941.

---
*Developed by: Arun B, School of Physics, University of Hyderabad*  
*Website: [https://sites.google.com/view/arunb/home](https://sites.google.com/view/arunb/home)*
