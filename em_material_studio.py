"""
EM-Material-Studio: Electromagnetic Material, Shielding & Absorption Suite
Modules:
  1. Reflection Loss (REL) Simulation (Thickness-dependent microwave absorption)
  2. Shielding Effectiveness (SE) Calculator (S-parameters from .txt: SET, SER, SEA)
  3. Dielectric, Magnetic & Cole-Cole Analysis (Permittivity, Permeability, Cole-Cole, AC Conductivity, Attenuation from .csv)

Developed by: Arun B, School of Physics, University of Hyderabad.
Website: https://sites.google.com/view/arunb/home
"""

import os
import sys
import threading
import webbrowser
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend for thread safety
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker as ticker
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Physical Constants (exact SI)
Z0 = 377.0             # Impedance of free space (Ohms)
c = 299792458.0        # Speed of light in vacuum (m/s)
EPS0 = 8.854e-12       # Vacuum permittivity (F/m) as in reference dielectric code

DEVELOPER_NAME = "Arun B, School of Physics, University of Hyderabad"
DEVELOPER_URL = "https://sites.google.com/view/arunb/home"


# =====================================================================
# 1. MODULE: REFLECTION LOSS (REL) SIMULATION
# =====================================================================

def run_rel_simulation(directory, thicknesses, progress_callback=None):
    thicknesses = np.round(thicknesses, 5)

    def report(pct, msg):
        if progress_callback:
            progress_callback(pct, msg)

    report(5, "[REL] Scanning directory for CSV files...")
    all_entries = os.listdir(directory)
    csv_files = [f for f in all_entries if f.lower().endswith(".csv")]
    if not csv_files:
        raise ValueError(f"No CSV files found in selected directory for REL Simulation:\n{directory}")

    report(10, f"[REL] Reading {len(csv_files)} CSV file(s)...")
    raw_dfs = []
    for f in csv_files:
        file_path = os.path.join(directory, f)
        data = pd.read_csv(file_path, skiprows=0, header=5,
                           names=['Frequency', 'er', 'ei', 'ur', 'ui'])
        numeric_columns = ['Frequency', 'er', 'ei', 'ur', 'ui']
        data[numeric_columns] = data[numeric_columns].astype(float)
        raw_dfs.append((f, data))

    processed_inputs = []
    for f, data in raw_dfs:
        df = data.copy()
        df['Er'] = df['er'] + 1j * df['ei']
        df['Ur'] = df['ur'] + 1j * df['ui']
        df['u/e'] = df['Ur'] / df['Er']
        df['ue'] = df['Ur'] * df['Er']
        df['sqrt_ue'] = np.sqrt(df['ue'])
        df['sqrt_u_div_e'] = np.sqrt(df['u/e'])
        processed_inputs.append((f, df))

    frequency_list = []
    thickness_list = []
    rel_values = []

    total_thicks = len(thicknesses)
    report(15, f"[REL] Simulating across {total_thicks} thickness values...")

    for idx, t in enumerate(thicknesses):
        d = t / 1000.0  # Convert mm to meters
        pct = 15 + int((idx / max(1, total_thicks)) * 45)  # 15% -> 60%
        report(pct, f"[REL] Processing thickness: {t:.4f} mm ({idx + 1}/{total_thicks})...")

        for f, df in processed_inputs:
            x = -1j * (2 * np.pi * df['Frequency'].values * d / c) * df['sqrt_ue'].values
            tanhx = np.tanh(x)
            z_norm = df['sqrt_u_div_e'].values * tanhx
            s11 = (z_norm - 1.0) / (z_norm + 1.0)
            r = np.abs(s11)**2
            rel = 10.0 * np.log10(r)

            freq_vals = df['Frequency'].tolist()
            frequency_list.extend(freq_vals)
            thickness_list.extend([t] * len(freq_vals))
            rel_values.extend(rel.tolist())

    report(60, "[REL] Structuring simulation data...")
    frequency_array = np.unique(frequency_list)
    thickness_array = np.unique(thickness_list)
    frequency_grid, thickness_grid = np.meshgrid(frequency_array, thickness_array)

    sim_df = pd.DataFrame({
        'Frequency': frequency_list,
        'Thickness': thickness_list,
        'REL': rel_values
    })
    rel_grid = sim_df.pivot_table(
        index='Thickness', columns='Frequency', values='REL', aggfunc='mean'
    ).reindex(index=thickness_array, columns=frequency_array).values

    # 1. Save Reflection Loss vs thickness Simulation data.xlsx
    report(65, "[REL] Saving 'Reflection Loss vs thickness Simulation data.xlsx'...")
    combined_data = pd.DataFrame({
        'Frequency (Hz)': frequency_list,
        'Thickness (mm)': thickness_list,
        'REL (dB)': rel_values
    })
    output_excel_path = os.path.join(directory, "Reflection Loss vs thickness Simulation data.xlsx")
    combined_data.to_excel(output_excel_path, index=False)

    # 2. Save Frequency_vs_REL_Data.xlsx
    report(70, "[REL] Saving 'Frequency_vs_REL_Data.xlsx'...")
    df_dict = {}
    first = True
    for t in thicknesses:
        mask = np.array(thickness_list) == t
        if first:
            df_dict['Frequency (GHz)'] = np.array(frequency_list)[mask] / 1e9
            first = False
        df_dict[f'{t} mm'] = np.array(rel_values)[mask]
    df_2d = pd.DataFrame(df_dict)
    df_2d.to_excel(os.path.join(directory, "Frequency_vs_REL_Data.xlsx"), index=False)

    # 3. Generate 3D Surface Plot
    report(75, "[REL] Generating 3D Simulation Plot (300 DPI)...")
    fig = plt.figure(figsize=(14, 10), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    ax.zaxis.set_major_locator(MaxNLocator(nbins=6, integer=True))
    ax.plot_surface(frequency_grid / 1e9, thickness_grid, rel_grid, cmap='viridis', edgecolor='none')
    ax.set_xlabel('Frequency (GHz)', fontsize=16, fontweight='bold', labelpad=9)
    ax.set_ylabel('Thickness (mm)', fontsize=16, fontweight='bold', labelpad=8)
    ax.set_zlabel('Reflection Loss (dB)', fontsize=16, fontweight='bold', labelpad=8)
    ax.tick_params(axis='both', which='major', labelsize=14, width=1.5)
    ax.tick_params(axis='both', which='minor', labelsize=12, width=1.5)
    for label in ax.get_xticklabels() + ax.get_yticklabels() + ax.get_zticklabels():
        label.set_fontweight('bold')

    contour_3d = ax.contourf(
        frequency_grid / 1e9, thickness_grid, rel_grid,
        zdir='z', offset=ax.get_zlim()[0], cmap='RdBu', alpha=0.7
    )
    cbar3d = fig.colorbar(contour_3d, ax=ax, shrink=0.5, aspect=15)
    cbar3d.ax.tick_params(labelsize=14)
    for label in cbar3d.ax.get_yticklabels():
        label.set_fontweight('bold')

    image_3d_path = os.path.join(directory, "Reflection Loss vs thickness Simulation.png")
    plt.savefig(image_3d_path, bbox_inches='tight', dpi=300)
    plt.close(fig)

    # 4. Generate 2D Frequency vs REL Plot
    report(85, "[REL] Generating 2D Plot (Frequency vs REL)...")
    fig2 = plt.figure(figsize=(10, 6))
    for t in thicknesses:
        mask = np.array(thickness_list) == t
        plt.plot(np.array(frequency_list)[mask] / 1e9, np.array(rel_values)[mask], label=f'{t} mm')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Reflection Loss (dB)')
    plt.title('2D Plot of Frequency vs Reflection Loss with Thickness as Legend')
    plt.legend(title='Thickness (mm)', loc='lower center', bbox_to_anchor=(0.5, 0.05), ncol=4, fancybox=False, shadow=False, frameon=False)
    image_2d_path = os.path.join(directory, "Frequency_vs_REL_2D_Plot.png")
    plt.savefig(image_2d_path)
    plt.close(fig2)

    # 5. Generate Contour Plot
    report(95, "[REL] Generating Contour Plot (Thickness vs Frequency)...")
    fig3 = plt.figure(figsize=(10, 6))
    contour = plt.contourf(frequency_grid / 1e9, thickness_grid, rel_grid, cmap='RdBu', levels=50)
    plt.xlabel('Frequency (GHz)', fontsize=18, fontweight='bold')
    plt.ylabel('Thickness (mm)', fontsize=18, fontweight='bold')
    plt.xticks(fontsize=16, fontweight='bold')
    plt.yticks(fontsize=16, fontweight='bold')
    cbar = plt.colorbar(contour)
    cbar.ax.tick_params(labelsize=14)
    cbar.set_label('Reflection Loss (dB)', fontsize=18, fontweight='bold')
    cbar.ax.tick_params(labelsize=12)
    for label in cbar.ax.get_xticklabels() + cbar.ax.get_yticklabels():
        label.set_fontweight('bold')
    image_contour_path = os.path.join(directory, "Thickness_vs_Frequency_Contour_Plot.png")
    plt.savefig(image_contour_path, bbox_inches='tight', dpi=300)
    plt.close(fig3)

    report(100, "[REL] Reflection Loss simulation completed! All files generated.")


# =====================================================================
# 2. MODULE: SHIELDING EFFECTIVENESS (SE) CALCULATOR
# =====================================================================

def run_se_calculation(directory, progress_callback=None):
    def report(pct, msg):
        if progress_callback:
            progress_callback(pct, msg)

    report(5, "[SE] Scanning directory for .txt files...")
    all_files = os.listdir(directory)
    txt_files = [f for f in all_files if f.lower().endswith(".txt")]
    if not txt_files:
        raise ValueError(f"No .txt S-parameter files found in selected directory:\n{directory}")

    total_files = len(txt_files)
    report(10, f"[SE] Found {total_files} .txt file(s). Processing S-parameters...")

    for f_idx, file_name in enumerate(txt_files):
        pct_base = 10 + int((f_idx / total_files) * 85)
        report(pct_base, f"[SE] Processing file: {file_name}...")

        file_path = os.path.join(directory, file_name)
        base_name = os.path.splitext(file_name)[0]
        output_excel_path = os.path.join(directory, f"{base_name}_SE_calculation.xlsx")
        image_path = os.path.join(directory, f"{base_name}_Graph.png")

        with open(file_path, "r") as f:
            lines = f.readlines()

        if len(lines) < 7:
            continue

        # Extract sample thickness from line 2
        thickness_line = lines[1]
        thickness_meters = float(thickness_line.split("=")[-1].strip().split()[0])
        thickness_mm = thickness_meters * 1000.0

        data_lines = lines[6:]
        data = pd.DataFrame([line.strip().split() for line in data_lines],
                            columns=['Frequency', 's11r', 's11i', 's21r', 's21i', 's12r', 's12i', 's22r', 's22i'])
        data = data.astype(float)

        # Magnitude square of S-parameters
        data['s11_mag'] = data['s11r'] ** 2 + data['s11i'] ** 2
        data['s21_mag'] = data['s21r'] ** 2 + data['s21i'] ** 2
        data['s12_mag'] = data['s12r'] ** 2 + data['s12i'] ** 2
        data['s22_mag'] = data['s22r'] ** 2 + data['s22i'] ** 2

        # Reflectance and Transmittance
        data['R'] = data['s11_mag']
        data['T'] = data['s21_mag']
        data['A'] = 1.0 - data['R']
        data['B'] = data['T'] / np.maximum(data['A'], 1e-15)

        # SER, SEA, SET
        data['SER'] = 10.0 * np.log10(np.maximum(data['A'], 1e-15))
        data['SEA'] = 10.0 * np.log10(np.maximum(data['B'], 1e-15))
        data['SET'] = data['SER'] + data['SEA']

        # Return Loss and Insertion Loss
        data['Return_Loss'] = 10.0 * np.log10(np.maximum(data['R'], 1e-15))
        data['Insertion_Loss'] = 10.0 * np.log10(np.maximum(data['T'], 1e-15))

        # Create Double Y-Axis Plot
        fig, ax1 = plt.subplots()
        ax1.plot(data['Frequency'], data['SER'], label='SER', color='blue')
        ax1.plot(data['Frequency'], data['SEA'], label='SEA', color='green')
        ax1.plot(data['Frequency'], data['SET'], label='SET', color='purple', marker='*', markersize=8, markevery=20)
        ax1.set_xlabel('Frequency (GHz)')

        tick_positions = np.arange(min(data['Frequency']), max(data['Frequency']) + 1e9, 1e9)
        ax1.set_xticks(tick_positions)
        ax1.set_xticklabels([f'{f/1e9:.0f}' for f in tick_positions])
        ax1.set_ylabel('Shielding Effectiveness (dB)')
        ax1.legend(loc='upper left')

        ax2 = ax1.twinx()
        ax2.plot(data['Frequency'], data['Return_Loss'], label='Return Loss', color='red', linestyle='--', alpha=0.6)
        ax2.plot(data['Frequency'], data['Insertion_Loss'], label='Insertion Loss', color='black', linestyle=':', alpha=0.6)
        ax2.set_ylabel('Return and Insertion Loss (dB) (NOT FOR REPORTING)')
        ax2.legend(loc='upper right')

        plt.title('Shielding Effectiveness (SEA,SER & SET)')
        ax1.text(data['Frequency'].median(), max(data['SET']) * 0.5,
                 f"Sample Thickness: {thickness_mm:.2f} mm",
                 fontsize=12, color='black', ha='center', va='center',
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))

        plt.savefig(image_path)
        plt.close('all')

        # Excel Export
        excel_df = data.copy()
        excel_df.rename(columns={
            'Return_Loss': 'Return_Loss (NOT FOR REPORTING)',
            'Insertion_Loss': 'Insertion_Loss (NOT FOR REPORTING)'
        }, inplace=True)
        cols_to_save = ['Frequency', 's11r', 's11i', 's21r', 's21i', 's12r', 's12i', 's22r', 's22i',
                        'R', 'T', 'Return_Loss (NOT FOR REPORTING)', 'Insertion_Loss (NOT FOR REPORTING)',
                        'SER', 'SEA', 'SET']
        excel_df[cols_to_save].to_excel(output_excel_path, index=False)

    report(100, "[SE] Shielding Effectiveness calculation completed successfully!")


# =====================================================================
# 3. MODULE: DIELECTRIC & COLE-COLE ANALYSIS
# =====================================================================

def run_dielectric_analysis(directory, progress_callback=None):
    def report(pct, msg):
        if progress_callback:
            progress_callback(pct, msg)

    report(5, "[Dielectric] Scanning directory for CSV files...")
    all_files = os.listdir(directory)
    csv_files = [f for f in all_files if f.lower().endswith(".csv")]
    if not csv_files:
        raise ValueError(f"No CSV files found in selected directory for Dielectric Analysis:\n{directory}")

    total_files = len(csv_files)
    report(10, f"[Dielectric] Found {total_files} CSV file(s). Processing dielectric properties...")

    for f_idx, file_name in enumerate(csv_files):
        file_path = os.path.join(directory, file_name)
        base_name = os.path.splitext(file_name)[0]

        data = pd.read_csv(file_path, skiprows=0, header=5,
                           names=['Frequency', 'er', 'ei', 'ur', 'ui'])
        numeric_columns = ['Frequency', 'er', 'ei', 'ur', 'ui']
        data[numeric_columns] = data[numeric_columns].astype(float)
        freq_ghz = data['Frequency'] / 1e9

        # Plot 1: Frequency vs Real and Imaginary Permittivity (_er_ei_plot.png)
        report(20, f"[Dielectric] Plotting permittivity for {file_name}...")
        fig, ax1 = plt.subplots(figsize=(8, 6))
        color = 'tab:blue'
        ax1.set_xlabel('Frequency (GHz)')
        ax1.set_ylabel('Real Permittivity', color=color)
        ax1.plot(data['Frequency']/1e9, data['er'], label='Real', color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True)

        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Imaginary Permittivity', color=color)
        ax2.plot(data['Frequency']/1e9, data['ei'], label='Imaginary', color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        plt.title(f'Frequency vs Real and Imaginary Permittivity - {base_name}')
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        plt.savefig(os.path.join(directory, f"{base_name}_er_ei_plot.png"))
        plt.close('all')

        # Plot 2: Frequency vs Real and Imaginary Permeability (_ur_ui_plot.png)
        report(35, f"[Dielectric] Plotting permeability for {file_name}...")
        fig, ax1 = plt.subplots(figsize=(8, 6))
        color = 'tab:green'
        ax1.set_xlabel('Frequency (GHz)')
        ax1.set_ylabel('Real Permeability', color=color)
        ax1.plot(data['Frequency']/1e9, data['ur'], label='Real', color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.grid(True)

        ax2 = ax1.twinx()
        color = 'black'
        ax2.set_ylabel('Imaginary Permeability', color=color)
        ax2.plot(data['Frequency']/1e9, data['ui'], label='Imaginary', color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        plt.title(f'Frequency vs Real and Imaginary Permeability - {base_name}')
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        plt.savefig(os.path.join(directory, f"{base_name}_ur_ui_plot.png"))
        plt.close('all')

        # Set publication rcParams (active for er_ur and following plots)
        plt.rcParams.update({
            "font.family": "serif",
            "font.size": 14,
            "axes.labelsize": 16,
            "axes.titlesize": 18,
            "legend.fontsize": 14,
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "mathtext.fontset": "stix",
            "figure.autolayout": True
        })

        # Plot 3: Frequency vs Real Permittivity & Real Permeability (_er_ur_plot.png)
        report(50, f"[Dielectric] Generating publication er vs ur plot for {file_name}...")
        fig, ax1 = plt.subplots(figsize=(10, 7), dpi=300)
        color = 'tab:red'
        ax1.set_xlabel(r'Frequency (GHz)')
        ax1.set_ylabel(r'Real Permittivity $\varepsilon_r$', color=color)
        ax1.plot(data['Frequency'] / 1e9, data['er'], label=r'Real Permittivity $\varepsilon_r$', color=color, linewidth=2, linestyle='-')
        ax1.tick_params(axis='y', labelcolor=color)
        ax1.yaxis.set_major_locator(ticker.MaxNLocator(6))
        ax1.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)

        ax2 = ax1.twinx()
        color = 'black'
        ax2.set_ylabel(r'Real Permeability $\mu_r$', color=color)
        ax2.plot(data['Frequency'] / 1e9, data['ur'], label=r'Real Permeability $\mu_r$', color=color, linewidth=2, linestyle='--')
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.yaxis.set_major_locator(ticker.MaxNLocator(6))

        plt.title(f'Frequency vs Real Permittivity and Permeability\n({base_name})')
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=False)
        plt.savefig(os.path.join(directory, f"{base_name}_er_ur_plot.png"), format='png', bbox_inches='tight')
        plt.close('all')

        # Plot 4: Magnetic Loss Tangent (_tandelta_magnetic_plot.png)
        report(65, f"[Dielectric] Plotting magnetic loss tangent for {file_name}...")
        plt.figure(figsize=(8, 6))
        plt.plot(data['Frequency']/1e9, data['ui']/data['ur'], label='imaginary/real', color='blue')
        plt.xlabel('Frequency (GHz)')
        plt.ylabel('Magnetic loss tangent')
        plt.title(f'tan_delta(Magnetic) - {base_name}')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(directory, f"{base_name}_tandelta_magnetic_plot.png"))
        plt.close('all')

        # Plot 5: Cole-Cole Plot (_cole-cole_plot.png)
        report(75, f"[Dielectric] Plotting Cole-Cole for {file_name}...")
        plt.figure(figsize=(8, 6))
        plt.plot(data['er'], data['ei'], label='cole - cole', color='blue')
        plt.xlabel('Real permittivity')
        plt.ylabel('Imaginary permittivity')
        plt.title(f'cole cole - {base_name}')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(directory, f"{base_name}_cole-cole_plot.png"))
        plt.close('all')

        # Plot 6: AC Conductivity (_ac_conductivity_plot.png & .xlsx)
        report(85, f"[Dielectric] Calculating AC conductivity for {file_name}...")
        data['ac_conductivity'] = 2.0 * np.pi * data['Frequency'] * 8.854e-12 * data['ei']
        plt.figure(figsize=(8, 6))
        plt.plot(data['Frequency']/1e9, data['ac_conductivity'], label='cole - cole', color='blue')
        plt.xlabel('Frequency (GHz)')
        plt.ylabel('ac conductivity (S/m)')
        plt.title(f'ac conductivity plot - {base_name}')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(directory, f"{base_name}_ac_conductivity_plot.png"))
        plt.close('all')

        excel_ac = data[['Frequency', 'ac_conductivity']]
        excel_ac.to_excel(os.path.join(directory, f"{base_name}_ac_conductivity.xlsx"), index=False)

        # Plot 7: Attenuation Constant (_attenuation_constant_plot.png & .xlsx)
        report(95, f"[Dielectric] Calculating attenuation constant for {file_name}...")
        data['A'] = data['ui'] * data['ei'] - data['ur'] * data['er']
        data['B'] = data['ui'] * data['er'] + data['ur'] * data['ei']
        data['alpha'] = (np.sqrt(2) * np.pi * data['Frequency'] / c) * np.sqrt(data['A'] + np.sqrt(data['A']**2 + data['B']**2))

        plt.figure(figsize=(8, 6))
        plt.plot(data['Frequency']/1e9, data['alpha'], label='alpha', color='blue')
        plt.xlabel('Frequency (GHz)')
        plt.ylabel('Attenuation constant')
        plt.title(f'Attenuation constant - {base_name}')
        plt.grid(True)
        plt.legend()
        plt.savefig(os.path.join(directory, f"{base_name}_attenuation_constant_plot.png"))
        plt.close('all')

        excel_att = data[['Frequency', 'alpha']]
        excel_att.to_excel(os.path.join(directory, f"{base_name}_attenuation_constant.xlsx"), index=False)

        # Reset rcParams to default
        matplotlib.rcdefaults()
        matplotlib.use('Agg')

    report(100, "[Dielectric] Dielectric and Cole-Cole analysis completed successfully!")


# =====================================================================
# GUI APPLICATION (2-COLUMN FIXED/RESPONSIVE LAYOUT)
# =====================================================================

class EMAnalysisSuiteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EM-Material-Studio: Electromagnetic Material, Shielding & Absorption Suite")
        self.geometry("1320x820")
        self.minsize(1100, 720)

        # Style configuration
        self.setup_styles()

        # State Variables
        self.folder_path_var = tk.StringVar(value="")
        self.file_scan_status_var = tk.StringVar(value="No folder selected")
        self.active_module_var = tk.StringVar(value="all")  # 'rel', 'se', 'dielectric', 'all'

        # REL parameters
        self.param_mode_var = tk.StringVar(value="range")
        self.t_start_var = tk.StringVar(value="0.0")
        self.t_stop_var = tk.StringVar(value="10.0")
        self.t_points_var = tk.StringVar(value="101")
        self.t_custom_var = tk.StringVar(value="1.0, 2.0, 3.0, 4.0, 5.0")
        self.t_summary_var = tk.StringVar(value="101 thicknesses (0.0 to 10.0 mm, step 0.1 mm)")

        # Progress tracking
        self.progress_val = tk.DoubleVar(value=0.0)
        self.progress_pct_str = tk.StringVar(value="0%")
        self.status_text_var = tk.StringVar(value="Ready. Select a data folder and click 'Run Analysis'.")
        self.is_running = False

        # Image cache and references
        self.image_registry = {}  # key -> {container, img_path, orig_img, canvas, status_box, status_win}
        self.rendered_tk_images = {}

        # Traces
        self.t_start_var.trace_add("write", lambda *_: self.update_thickness_summary())
        self.t_stop_var.trace_add("write", lambda *_: self.update_thickness_summary())
        self.t_points_var.trace_add("write", lambda *_: self.update_thickness_summary())
        self.t_custom_var.trace_add("write", lambda *_: self.update_thickness_summary())

        # Construct widgets
        self.create_layout()
        self.update_thickness_summary()

    def setup_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        self.configure(bg="#f4f6f9")
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TLabel", background="#f4f6f9", foreground="#212529")
        style.configure("TFrame", background="#f4f6f9")
        style.configure("TLabelframe", background="#f4f6f9", foreground="#212529")
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), background="#f4f6f9", foreground="#1d3557")

        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), background="#1d3557", foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#457b9d"), ("disabled", "#a8dadc")])

        style.configure("Action.TButton", font=("Segoe UI", 9, "bold"), background="#457b9d", foreground="#ffffff")
        style.map("Action.TButton", background=[("active", "#1d3557"), ("disabled", "#cccccc")])

        # Notebook styling
        style.configure("TNotebook", background="#e9ecef", tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[14, 7], background="#dee2e6")
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#1d3557")])

        style.configure("Horizontal.TProgressbar", background="#1d3557", troughcolor="#e9ecef", thickness=16)

    def create_layout(self):
        # Master grid: 1 Row, 2 Columns
        self.columnconfigure(0, weight=0, minsize=420)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT COLUMN: Parameters, Module Selection & Execution
        # -------------------------------------------------------------
        left_container = ttk.Frame(self, padding="16 16 16 12")
        left_container.grid(row=0, column=0, sticky="nsew")
        left_container.columnconfigure(0, weight=1)
        left_container.rowconfigure(3, weight=1)  # Pushes developer footer down

        # Header
        header_frame = ttk.Frame(left_container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        tk.Label(header_frame, text="EM Material & Shielding Suite",
                 font=("Segoe UI", 15, "bold"), bg="#f4f6f9", fg="#1d3557").pack(anchor="w")
        tk.Label(header_frame, text="Reflection Loss | Shielding Effectiveness | Dielectric Properties",
                 font=("Segoe UI", 9), bg="#f4f6f9", fg="#6c757d").pack(anchor="w")

        # Scrollable/Control content area
        content_frame = ttk.Frame(left_container)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)

        # 1. Folder Selection Group
        folder_group = ttk.LabelFrame(content_frame, text=" 1. Input Data Directory ", padding="10")
        folder_group.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        folder_group.columnconfigure(0, weight=1)

        path_row = ttk.Frame(folder_group)
        path_row.grid(row=0, column=0, sticky="ew")
        path_row.columnconfigure(0, weight=1)

        self.folder_entry = ttk.Entry(path_row, textvariable=self.folder_path_var, font=("Segoe UI", 9))
        self.folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        browse_btn = ttk.Button(path_row, text="Browse...", style="Action.TButton", command=self.browse_folder)
        browse_btn.grid(row=0, column=1, sticky="e")

        self.file_scan_lbl = tk.Label(folder_group, textvariable=self.file_scan_status_var,
                                      font=("Segoe UI", 8, "italic"), bg="#f4f6f9", fg="#495057", anchor="w")
        self.file_scan_lbl.grid(row=1, column=0, sticky="w", pady=(6, 0))

        # 2. Module Selection Group
        module_group = ttk.LabelFrame(content_frame, text=" 2. Select Analysis Module ", padding="10")
        module_group.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        module_group.columnconfigure(0, weight=1)

        modules = [
            ("⚡ Run All Analyses (Complete Suite)", "all"),
            ("📡 1. Reflection Loss (REL) Simulation", "rel"),
            ("🛡️ 2. Shielding Effectiveness (SE) Calculator", "se"),
            ("🔬 3. Dielectric & Cole-Cole Analysis", "dielectric")
        ]

        for text, val in modules:
            rb = ttk.Radiobutton(module_group, text=text, variable=self.active_module_var,
                                 value=val, command=self.on_module_changed)
            rb.pack(anchor="w", pady=2)

        # 3. Dynamic Module Parameters Card
        self.param_card = ttk.LabelFrame(content_frame, text=" 3. Module Settings ", padding="10")
        self.param_card.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.param_card.columnconfigure(0, weight=1)

        # Frame for REL thickness controls
        self.rel_settings_frame = ttk.Frame(self.param_card)
        self.rel_settings_frame.columnconfigure(0, weight=1)

        mode_row = ttk.Frame(self.rel_settings_frame)
        mode_row.pack(fill="x", pady=(0, 6))
        ttk.Radiobutton(mode_row, text="Range (Linspace)", variable=self.param_mode_var,
                        value="range", command=self.toggle_param_mode).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(mode_row, text="Custom List", variable=self.param_mode_var,
                        value="custom", command=self.toggle_param_mode).pack(side="left")

        self.range_inputs_frame = ttk.Frame(self.rel_settings_frame)
        self.range_inputs_frame.pack(fill="x")
        self.range_inputs_frame.columnconfigure(1, weight=1)

        tk.Label(self.range_inputs_frame, text="Start Thickness (mm):", bg="#f4f6f9", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(self.range_inputs_frame, textvariable=self.t_start_var, width=10).grid(row=0, column=1, sticky="e", pady=2)

        tk.Label(self.range_inputs_frame, text="Stop Thickness (mm):", bg="#f4f6f9", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(self.range_inputs_frame, textvariable=self.t_stop_var, width=10).grid(row=1, column=1, sticky="e", pady=2)

        tk.Label(self.range_inputs_frame, text="Points / Steps:", bg="#f4f6f9", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(self.range_inputs_frame, textvariable=self.t_points_var, width=10).grid(row=2, column=1, sticky="e", pady=2)

        self.custom_inputs_frame = ttk.Frame(self.rel_settings_frame)
        self.custom_inputs_frame.columnconfigure(0, weight=1)
        tk.Label(self.custom_inputs_frame, text="Enter values separated by commas (mm):", bg="#f4f6f9", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(self.custom_inputs_frame, textvariable=self.t_custom_var).grid(row=1, column=0, sticky="ew", pady=2)

        self.summary_lbl = tk.Label(self.rel_settings_frame, textvariable=self.t_summary_var,
                                    font=("Segoe UI", 8, "bold"), bg="#e8f4f8", fg="#1d3557",
                                    padx=4, pady=3, relief="solid", bd=1)
        self.summary_lbl.pack(fill="x", pady=(6, 0))

        # Frame for SE description
        self.se_settings_frame = ttk.Frame(self.param_card)
        tk.Label(self.se_settings_frame, text="Processes S-parameters from .txt files.\nExtracts sample thickness from header.\nCalculates SER, SEA, SET, Return Loss & Insertion Loss.",
                 bg="#f4f6f9", fg="#2b2d42", font=("Segoe UI", 8, "italic"), justify="left").pack(anchor="w")

        # Frame for Dielectric description
        self.dielectric_settings_frame = ttk.Frame(self.param_card)
        tk.Label(self.dielectric_settings_frame, text="Processes .csv files.\nGenerates 7 plots:\n• Real & Imaginary Permittivity / Permeability\n• Publication ε_r vs μ_r\n• Magnetic Loss Tangent (tan δ)\n• Cole-Cole Plot\n• AC Conductivity (σ_ac) & Attenuation Constant (α)",
                 bg="#f4f6f9", fg="#2b2d42", font=("Segoe UI", 8, "italic"), justify="left").pack(anchor="w")

        # Initially show REL settings
        self.rel_settings_frame.pack(fill="x")

        # 4. Execution & Progress Group
        exec_group = ttk.LabelFrame(content_frame, text=" 4. Execution & Progress ", padding="10")
        exec_group.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        exec_group.columnconfigure(0, weight=1)

        self.run_btn = ttk.Button(exec_group, text="▶  Run All Analyses", style="Primary.TButton", command=self.start_execution)
        self.run_btn.grid(row=0, column=0, sticky="ew", ipady=4, pady=(0, 8))

        prog_header = ttk.Frame(exec_group)
        prog_header.grid(row=1, column=0, sticky="ew", pady=(0, 2))
        prog_header.columnconfigure(0, weight=1)
        tk.Label(prog_header, text="Task Progress:", bg="#f4f6f9", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w")
        self.pct_label = tk.Label(prog_header, textvariable=self.progress_pct_str, bg="#f4f6f9", font=("Segoe UI", 9, "bold"), fg="#1d3557")
        self.pct_label.grid(row=0, column=1, sticky="e")

        self.progressbar = ttk.Progressbar(exec_group, variable=self.progress_val, maximum=100, style="Horizontal.TProgressbar")
        self.progressbar.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self.status_lbl = tk.Label(exec_group, textvariable=self.status_text_var,
                                   font=("Segoe UI", 8), bg="#f4f6f9", fg="#495057", wraplength=350, justify="left")
        self.status_lbl.grid(row=3, column=0, sticky="w")

        self.open_folder_btn = ttk.Button(exec_group, text="📁 Open Output Folder", command=self.open_output_folder, state="disabled")
        self.open_folder_btn.grid(row=4, column=0, sticky="ew", pady=(6, 0))

        # Bottom Developer Info
        left_container.rowconfigure(3, weight=1)
        dev_frame = ttk.Frame(left_container)
        dev_frame.grid(row=4, column=0, sticky="ew", pady=(8, 0))
        ttk.Separator(dev_frame, orient="horizontal").pack(fill="x", pady=(0, 6))
        tk.Label(dev_frame, text="Developed by:", font=("Segoe UI", 9, "bold"), bg="#f4f6f9", fg="#2b2d42").pack(anchor="w")
        dev_link = tk.Label(dev_frame, text=DEVELOPER_NAME,
                            font=("Segoe UI", 9, "underline"), bg="#f4f6f9", fg="#0066cc",
                            cursor="hand2", wraplength=370, justify="left")
        dev_link.pack(anchor="w", pady=(2, 0))
        dev_link.bind("<Button-1>", lambda e: webbrowser.open_new(DEVELOPER_URL))

        # -------------------------------------------------------------
        # RIGHT COLUMN: Hierarchical Tabs for All 3 Modules
        # -------------------------------------------------------------
        right_container = ttk.Frame(self, padding="16 16 16 16")
        right_container.grid(row=0, column=1, sticky="nsew")
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(0, weight=1)

        self.main_notebook = ttk.Notebook(right_container)
        self.main_notebook.grid(row=0, column=0, sticky="nsew")

        # Top Tab 1: Reflection Loss (REL)
        rel_tab = ttk.Frame(self.main_notebook)
        rel_tab.columnconfigure(0, weight=1)
        rel_tab.rowconfigure(0, weight=1)
        self.main_notebook.add(rel_tab, text="  📡 Reflection Loss (REL)  ")

        self.rel_notebook = ttk.Notebook(rel_tab)
        self.rel_notebook.grid(row=0, column=0, sticky="nsew")
        self.build_plot_tab(self.rel_notebook, "Frequency_vs_REL_2D_Plot", "Frequency_vs_REL_2D_Plot.png", "2D Plot: Frequency vs Reflection Loss")
        self.build_plot_tab(self.rel_notebook, "Reflection Loss vs thickness Simulation", "Reflection Loss vs thickness Simulation.png", "3D Surface & Contour Projection Plot")
        self.build_plot_tab(self.rel_notebook, "Thickness_vs_Frequency_Contour_Plot", "Thickness_vs_Frequency_Contour_Plot.png", "Contour Plot: Thickness vs Frequency")

        # Top Tab 2: Shielding Effectiveness (SE)
        se_tab = ttk.Frame(self.main_notebook)
        se_tab.columnconfigure(0, weight=1)
        se_tab.rowconfigure(0, weight=1)
        self.main_notebook.add(se_tab, text="  🛡️ Shielding Effectiveness (SE)  ")

        self.se_notebook = ttk.Notebook(se_tab)
        self.se_notebook.grid(row=0, column=0, sticky="nsew")
        self.build_plot_tab(self.se_notebook, "Shielding Effectiveness Graph", "_Graph.png", "Shielding Effectiveness (SER, SEA, SET & Loss)")

        # Top Tab 3: Dielectric & Cole-Cole
        dielectric_tab = ttk.Frame(self.main_notebook)
        dielectric_tab.columnconfigure(0, weight=1)
        dielectric_tab.rowconfigure(0, weight=1)
        self.main_notebook.add(dielectric_tab, text="  🔬 Dielectric & Cole-Cole  ")

        self.dielectric_notebook = ttk.Notebook(dielectric_tab)
        self.dielectric_notebook.grid(row=0, column=0, sticky="nsew")
        self.build_plot_tab(self.dielectric_notebook, "Permittivity (er, ei)", "_er_ei_plot.png", "Frequency vs Real & Imaginary Permittivity")
        self.build_plot_tab(self.dielectric_notebook, "Permeability (ur, ui)", "_ur_ui_plot.png", "Frequency vs Real & Imaginary Permeability")
        self.build_plot_tab(self.dielectric_notebook, "er vs ur (Pub Quality)", "_er_ur_plot.png", "Frequency vs Real Permittivity & Permeability")
        self.build_plot_tab(self.dielectric_notebook, "Magnetic Loss Tangent", "_tandelta_magnetic_plot.png", "tan δ (Magnetic Loss Tangent = μ''/μ')")
        self.build_plot_tab(self.dielectric_notebook, "Cole-Cole Plot", "_cole-cole_plot.png", "Cole-Cole Plot (ε' vs ε'')")
        self.build_plot_tab(self.dielectric_notebook, "AC Conductivity", "_ac_conductivity_plot.png", "AC Conductivity vs Frequency")
        self.build_plot_tab(self.dielectric_notebook, "Attenuation Constant", "_attenuation_constant_plot.png", "Attenuation Constant (α) vs Frequency")

        # Tab switch bindings for dynamic scaling
        self.main_notebook.bind("<<NotebookTabChanged>>", self.on_any_tab_changed)
        self.rel_notebook.bind("<<NotebookTabChanged>>", self.on_any_tab_changed)
        self.se_notebook.bind("<<NotebookTabChanged>>", self.on_any_tab_changed)
        self.dielectric_notebook.bind("<<NotebookTabChanged>>", self.on_any_tab_changed)

    def build_plot_tab(self, parent_notebook, tab_title, filename_suffix, description):
        tab_frame = ttk.Frame(parent_notebook)
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(1, weight=1)
        parent_notebook.add(tab_frame, text=f"  {tab_title}  ")

        # Top toolbar
        toolbar = ttk.Frame(tab_frame, padding="6")
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(0, weight=1)

        info_lbl = tk.Label(toolbar, text=f"{description} ({filename_suffix})",
                            font=("Segoe UI", 9, "bold"), bg="#f4f6f9", fg="#1d3557")
        info_lbl.grid(row=0, column=0, sticky="w")

        open_btn = ttk.Button(toolbar, text="Open Full Image",
                              command=lambda fn=filename_suffix: self.open_image_file(fn))
        open_btn.grid(row=0, column=1, sticky="e")

        # Canvas for display
        container = ttk.Frame(tab_frame)
        container.grid(row=1, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        canvas = tk.Canvas(container, bg="#ffffff", highlightthickness=1, highlightbackground="#dee2e6")
        canvas.grid(row=0, column=0, sticky="nsew")

        status_box = tk.Label(canvas, text="Ready\n\nSelect a folder and click 'Run Analysis'.\nPlots will be displayed here upon completion.",
                              font=("Segoe UI", 11), bg="#ffffff", fg="#6c757d", justify="center")
        status_win = canvas.create_window(350, 250, window=status_box, anchor="center")

        self.image_registry[filename_suffix] = {
            "tab_title": tab_title,
            "filename_suffix": filename_suffix,
            "container": container,
            "canvas": canvas,
            "status_box": status_box,
            "status_win": status_win,
            "img_path": None,
            "orig_img": None
        }

        canvas.bind("<Configure>", lambda e, fn=filename_suffix: self.on_canvas_resize(e, fn))

    def on_module_changed(self):
        mod = self.active_module_var.get()
        # Update settings card visibility
        self.rel_settings_frame.pack_forget()
        self.se_settings_frame.pack_forget()
        self.dielectric_settings_frame.pack_forget()

        if mod == "all":
            self.run_btn.config(text="▶  Run All Analyses")
            self.rel_settings_frame.pack(fill="x")
        elif mod == "rel":
            self.run_btn.config(text="▶  Run REL Simulation")
            self.rel_settings_frame.pack(fill="x")
            self.main_notebook.select(0)
        elif mod == "se":
            self.run_btn.config(text="▶  Run SE Calculator")
            self.se_settings_frame.pack(fill="x")
            self.main_notebook.select(1)
        elif mod == "dielectric":
            self.run_btn.config(text="▶  Run Dielectric & Cole-Cole")
            self.dielectric_settings_frame.pack(fill="x")
            self.main_notebook.select(2)

    def toggle_param_mode(self):
        if self.param_mode_var.get() == "range":
            self.custom_inputs_frame.pack_forget()
            self.range_inputs_frame.pack(fill="x")
        else:
            self.range_inputs_frame.pack_forget()
            self.custom_inputs_frame.pack(fill="x")
        self.update_thickness_summary()

    def update_thickness_summary(self):
        try:
            thicks = self.get_thicknesses()
            n = len(thicks)
            if n == 0:
                self.t_summary_var.set("⚠ No thicknesses defined")
                self.summary_lbl.config(fg="#d90429", bg="#ffe3e3")
            elif n == 1:
                self.t_summary_var.set(f"Single thickness: {thicks[0]:.4f} mm")
                self.summary_lbl.config(fg="#1d3557", bg="#e8f4f8")
            else:
                step = (thicks[-1] - thicks[0]) / (n - 1) if n > 1 else 0
                self.t_summary_var.set(f"{n} values ({thicks[0]:.2f} to {thicks[-1]:.2f} mm, ~{step:.2f} mm step)")
                self.summary_lbl.config(fg="#1d3557", bg="#e8f4f8")
        except Exception:
            self.t_summary_var.set("⚠ Invalid parameter format")
            self.summary_lbl.config(fg="#d90429", bg="#ffe3e3")

    def get_thicknesses(self):
        mode = self.param_mode_var.get()
        if mode == "range":
            start = float(self.t_start_var.get())
            stop = float(self.t_stop_var.get())
            points = int(self.t_points_var.get())
            if points < 1:
                raise ValueError("Points must be at least 1")
            return np.round(np.linspace(start, stop, points), 5)
        else:
            raw = self.t_custom_var.get()
            vals = [float(x.strip()) for x in raw.split(",") if x.strip()]
            if not vals:
                raise ValueError("No valid numbers provided in custom list")
            return np.round(np.array(vals), 5)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Measurement Data Folder")
        if folder:
            self.folder_path_var.set(folder)
            self.scan_folder_files(folder)

    def scan_folder_files(self, folder):
        if not os.path.exists(folder):
            self.file_scan_status_var.set("Folder does not exist")
            self.file_scan_lbl.config(fg="#d90429")
            return
        files = os.listdir(folder)
        csvs = [f for f in files if f.lower().endswith(".csv")]
        txts = [f for f in files if f.lower().endswith(".txt")]
        self.file_scan_status_var.set(f"✓ Found {len(csvs)} CSV file(s), {len(txts)} TXT S-parameter file(s)")
        self.file_scan_lbl.config(fg="#2a9d8f" if (csvs or txts) else "#e76f51")

    def update_progress_ui(self, pct, msg):
        self.progress_val.set(pct)
        self.progress_pct_str.set(f"{pct}%")
        self.status_text_var.set(msg)

        # Update completeness message on all tabs
        tab_msg = f"Calculation in Progress...\n\nCompletion: {pct}%\n\n{msg}"
        for key, entry in self.image_registry.items():
            status_box = entry["status_box"]
            status_win = entry["status_win"]
            canvas = entry["canvas"]
            if status_box.winfo_exists():
                status_box.config(text=tab_msg, fg="#1d3557", font=("Segoe UI", 12, "bold"))
                w = canvas.winfo_width() or 400
                h = canvas.winfo_height() or 300
                canvas.coords(status_win, w / 2, h / 2)

    def start_execution(self):
        if self.is_running:
            return

        folder = self.folder_path_var.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid directory containing measurement data.")
            return

        selected_module = self.active_module_var.get()
        thicknesses = None
        if selected_module in ("rel", "all"):
            try:
                thicknesses = self.get_thicknesses()
            except Exception as e:
                messagebox.showerror("Invalid Thickness Parameter", f"Please check thickness settings:\n{e}")
                return

        self.is_running = True
        self.run_btn.config(state="disabled", text="⏳ Running Analysis...")
        self.open_folder_btn.config(state="disabled")

        # Reset canvases to progress state
        for key, entry in self.image_registry.items():
            canvas = entry["canvas"]
            canvas.delete("plot_img")
            status_box = entry["status_box"]
            status_win = entry["status_win"]
            status_box.config(text="Starting calculations...", fg="#1d3557")
            w = canvas.winfo_width() or 400
            h = canvas.winfo_height() or 300
            canvas.coords(status_win, w / 2, h / 2)
            canvas.itemconfigure(status_win, state="normal")

        # Run worker in background thread
        worker = threading.Thread(
            target=self._worker_thread_proc,
            args=(folder, selected_module, thicknesses),
            daemon=True
        )
        worker.start()

    def _worker_thread_proc(self, folder, module, thicknesses):
        def progress_cb(pct, msg):
            self.after(0, self.update_progress_ui, pct, msg)

        errors = []
        try:
            if module == "all":
                # Run all 3 modules
                progress_cb(5, "Running Reflection Loss (REL) Simulation...")
                run_rel_simulation(folder, thicknesses, progress_callback=lambda p, m: progress_cb(int(p * 0.35), m))

                progress_cb(35, "Running Shielding Effectiveness (SE) Calculator...")
                run_se_calculation(folder, progress_callback=lambda p, m: progress_cb(35 + int(p * 0.30), m))

                progress_cb(65, "Running Dielectric & Cole-Cole Analysis...")
                run_dielectric_analysis(folder, progress_callback=lambda p, m: progress_cb(65 + int(p * 0.35), m))

                progress_cb(100, "All analyses completed successfully!")

            elif module == "rel":
                run_rel_simulation(folder, thicknesses, progress_callback=progress_cb)
            elif module == "se":
                run_se_calculation(folder, progress_callback=progress_cb)
            elif module == "dielectric":
                run_dielectric_analysis(folder, progress_callback=progress_cb)

        except Exception as e:
            errors.append(str(e))

        err_msg = "\n".join(errors) if errors else None
        self.after(0, self._on_execution_finished, folder, err_msg)

    def _on_execution_finished(self, folder, error):
        self.is_running = False
        self.on_module_changed()  # Restores correct button text
        self.run_btn.config(state="normal")
        self.open_folder_btn.config(state="normal")

        if error:
            self.status_text_var.set(f"Error: {error}")
            for key, entry in self.image_registry.items():
                status_box = entry["status_box"]
                status_box.config(text=f"Calculation Error:\n\n{error}", fg="#d90429")
            messagebox.showerror("Analysis Error", f"An error occurred during calculation:\n{error}")
            return

        # Success: Scan and render all generated images in tabs
        self.load_all_generated_plots(folder)
        messagebox.showinfo("Success", "Analysis completed successfully! All plots and Excel files have been generated.")

    def load_all_generated_plots(self, folder):
        files_in_dir = os.listdir(folder)
        for key, entry in self.image_registry.items():
            canvas = entry["canvas"]
            status_box = entry["status_box"]
            status_win = entry["status_win"]

            # Match exact file or suffix
            matched_file = None
            if key.startswith("_"):
                # Suffix match, e.g. '_Graph.png', '_er_ei_plot.png'
                for f in files_in_dir:
                    if f.lower().endswith(key.lower()):
                        matched_file = f
                        break
            else:
                # Exact match, e.g. 'Frequency_vs_REL_2D_Plot.png'
                for f in files_in_dir:
                    if f.lower() == key.lower():
                        matched_file = f
                        break

            if matched_file:
                img_path = os.path.join(folder, matched_file)
                try:
                    orig_img = Image.open(img_path)
                    entry["img_path"] = img_path
                    entry["orig_img"] = orig_img
                    canvas.itemconfigure(status_win, state="hidden")
                    self.render_image_on_canvas(key)
                except Exception as ex:
                    status_box.config(text=f"Error loading {matched_file}:\n{ex}", fg="#d90429")
                    canvas.itemconfigure(status_win, state="normal")
            else:
                status_box.config(text=f"No plot file generated for:\n{key}", fg="#6c757d")
                canvas.itemconfigure(status_win, state="normal")

    def render_image_on_canvas(self, key):
        entry = self.image_registry.get(key)
        if not entry:
            return
        orig_img = entry.get("orig_img")
        canvas = entry["canvas"]
        if not orig_img:
            return

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 50 or ch < 50:
            return

        iw, ih = orig_img.size
        scale = min((cw - 20) / iw, (ch - 20) / ih)
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))

        resized = orig_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        tk_img = ImageTk.PhotoImage(resized)
        self.rendered_tk_images[key] = tk_img

        canvas.delete("plot_img")
        canvas.create_image(cw / 2, ch / 2, image=tk_img, anchor="center", tags="plot_img")

    def on_canvas_resize(self, event, key):
        entry = self.image_registry.get(key)
        if not entry:
            return
        if entry.get("orig_img"):
            self.render_image_on_canvas(key)
        else:
            status_win = entry["status_win"]
            canvas = entry["canvas"]
            canvas.coords(status_win, event.width / 2, event.height / 2)

    def on_any_tab_changed(self, event=None):
        for key in self.image_registry:
            self.after(50, lambda k=key: self.render_image_on_canvas(k))

    def open_output_folder(self):
        folder = self.folder_path_var.get().strip()
        if folder and os.path.isdir(folder):
            if sys.platform == "win32":
                os.startfile(folder)
            else:
                import subprocess
                subprocess.Popen(["xdg-open", folder])

    def open_image_file(self, filename_suffix):
        entry = self.image_registry.get(filename_suffix)
        if entry and entry.get("img_path") and os.path.exists(entry["img_path"]):
            if sys.platform == "win32":
                os.startfile(entry["img_path"])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", entry["img_path"]])
        else:
            messagebox.showinfo("Notice", f"Plot has not been generated yet for {filename_suffix}")


def main():
    app = EMAnalysisSuiteApp()
    app.mainloop()


if __name__ == "__main__":
    main()
