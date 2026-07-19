# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 07:59:22 2026

@author: SLM30
"""

#%% import modules and set default fonts and colors
"""
Default plot formatting code for Austin Downey's series of open source notes/
books. This common header is used to set the fonts and format.
Header file last updated May 16, 2024
"""

from IPython import get_ipython
get_ipython().run_line_magic('reset', '-f') 

import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq

# set default fonts and plot colors
plt.rcParams.update({'text.usetex': False})
plt.rcParams.update({'image.cmap': 'viridis'})
plt.rcParams.update({'font.serif':['Times New Roman', 'Times', 'DejaVu Serif',
'Bitstream Vera Serif', 'Computer Modern Roman', 'New Century Schoolbook',
'Century Schoolbook L', 'Utopia', 'ITC Bookman', 'Bookman',
'Nimbus Roman No9 L', 'Palatino', 'Charter', 'serif']})
plt.rcParams.update({'font.family':'serif'})
plt.rcParams.update({'font.size': 10})
plt.rcParams.update({'mathtext.rm': 'serif'})
# I don't think I need this next line as its set to 'stixsans' above.
plt.rcParams.update({'mathtext.fontset': 'custom'})
cc = plt.rcParams['axes.prop_cycle'].by_key()['color']
## End of plot formatting code
plt.close('all')
"""
Merged analysis script for LabVIEW .lvm exports.

This version assumes:
- the script is in the SAME folder as the data file
- the data file is named test_1.lvm (or change FILENAME below)
- plots are saved in ./figures

What it does:
1) Reads a LabVIEW Measurement (.lvm) file.
2) Stitches repeated Voltage_4 / Voltage_5 / Voltage_6 blocks into continuous traces.
3) Plots raw voltages.
4) Computes current, material voltage, and material resistance.
5) Plots resistance vs time and its FFT.
6) Extracts the steady-state region of each 1 Hz cycle.
7) Computes average resistance per pulse and ΔR/R0.
8) Plots FFTs for raw channels, resistance, and pulse-averaged resistance.
9) Saves figures and CSV files into ./figures.
"""
# ======================================================
# SETTINGS
# ======================================================

TEST_FOLDER = "07152026"
TEST_FILE = "test_1.lvm"

FILENAME = Path(TEST_FOLDER) / TEST_FILE

TEST_NAME = FILENAME.stem

SAVE_FOLDER = Path(TEST_FOLDER) / "figures"
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)

# Hardware / experiment settings
R_SHUNT_OHMS = 1_000_000.0      # 1 MΩ resistor
CYCLE_S = 1.0                   # biphasic repetition period
STEADY_START_S = 0.30           # steady-state window inside each cycle
STEADY_END_S = 0.80

# Optional zoom window for the stitched full trace
ZOOM_START_S = 20.0
ZOOM_END_S = 25.0

# Columns to stitch from the LabVIEW export
PREFIX_V4 = "Voltage_4"         # A1 (before resistor)
PREFIX_V5 = "Voltage_5"         # A2 (after resistor)
PREFIX_V6 = "Voltage_6"         # A3 (after material)

# FFT display limits
RAW_FFT_XLIM = (0, 100)
RES_FFT_XLIM = (0, 100)
PULSE_RES_FFT_XLIM = (0, 10)

# Moving average window for resistance display
RES_SMOOTH_WINDOW = 101

# Small number to avoid divide-by-zero warnings
EPS_CURRENT = 1e-15


# ======================================================
# HELPERS
# ======================================================

def find_header_row(path: Path) -> int:
    """Return the 0-based row index of the line starting the data table."""
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if line.strip().startswith("X_Value"):
                return i
    raise ValueError("Could not find the X_Value header row.")


def natural_key(name: str):
    """Human-friendly sort for names like Voltage_5, Voltage_5 1, Voltage_5 2, ..."""
    parts = re.split(r"(\d+)", str(name))
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def stitch_prefix(df: pd.DataFrame, time_block: np.ndarray, prefix: str):
    """
    Stitch all columns starting with prefix into one continuous trace.
    Returns stitched time, stitched values, matched columns, inferred dt.
    """
    cols = [c for c in df.columns if str(c).startswith(prefix)]
    cols = sorted(cols, key=natural_key)

    if not cols:
        raise ValueError(f"No columns starting with '{prefix}' were found.")

    time_block = np.asarray(time_block, dtype=float)
    time_block = time_block[np.isfinite(time_block)]

    if len(time_block) < 2:
        raise ValueError("Not enough X_Value points to infer block timing.")

    dt = np.median(np.diff(time_block))
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("Invalid dt inferred from X_Value.")

    block_duration = time_block[-1] + dt

    t_all = []
    y_all = []

    for i, col in enumerate(cols):
        y = np.asarray(df[col], dtype=float)
        n = min(len(time_block), len(y))
        t = time_block[:n] + i * block_duration
        y = y[:n]

        valid = np.isfinite(t) & np.isfinite(y)
        t_all.append(t[valid])
        y_all.append(y[valid])

    t_all = np.concatenate(t_all)
    y_all = np.concatenate(y_all)

    sort_idx = np.argsort(t_all)
    return t_all[sort_idx], y_all[sort_idx], cols, dt


def plot_series(x, y, title, xlabel, ylabel, outpath, xlim=None, sci_y=False):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(x, y, lw=1)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    if xlim is not None:
        ax.set_xlim(*xlim)
    if sci_y:
        ax.ticklabel_format(axis="y", style="sci", scilimits=(6, 6))
    fig.tight_layout()
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.show()


def plot_fft(x, y, title, outpath, xlim=(0, 100)):
    """FFT of y(x). x must be in seconds."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    valid = np.isfinite(x) & np.isfinite(y)
    x = x[valid]
    y = y[valid]

    if len(x) < 4:
        print(f"{title}: not enough points for FFT.")
        return

    y = y - np.mean(y)

    dt = np.median(np.diff(x))
    if not np.isfinite(dt) or dt <= 0:
        print(f"{title}: invalid time spacing for FFT.")
        return

    freqs = rfftfreq(len(y), d=dt)
    mag = np.abs(rfft(y)) / len(y)

    if len(mag) > 1:
        peak_idx = np.argmax(mag[1:]) + 1
        dom_f = freqs[peak_idx]
        print(f"{title}: dominant frequency = {dom_f:.3f} Hz")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(freqs, mag, lw=1)
    ax.set_title(title)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_xlim(*xlim)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300, bbox_inches="tight")
    plt.show()

# ======================================================
# LOAD FILE
# ======================================================

path = FILENAME.expanduser().resolve()
if not path.exists():
    raise FileNotFoundError(f"File not found: {path}")

header_row = find_header_row(path)

df = pd.read_csv(path, sep="\t", skiprows=header_row, engine="python")
df.columns = [str(c).strip() for c in df.columns]

for c in df.columns:
    df[c] = pd.to_numeric(df[c], errors="coerce")

print("Columns found:")
print(df.columns.tolist())

time_col = df.columns[0]
time_block = df[time_col].to_numpy(dtype=float)

# ======================================================
# STITCH CHANNELS
# ======================================================

t4, v4, cols4, dt = stitch_prefix(df, time_block, PREFIX_V4)
t5, v5, cols5, _ = stitch_prefix(df, time_block, PREFIX_V5)
t6, v6, cols6, _ = stitch_prefix(df, time_block, PREFIX_V6)

print(f"Found {len(cols4)} {PREFIX_V4} columns")
print(f"Found {len(cols5)} {PREFIX_V5} columns")
print(f"Found {len(cols6)} {PREFIX_V6} columns")

# Use the A1 time axis as master axis
time_full = t4
n = min(len(time_full), len(v5), len(v6))
time_full = time_full[:n]
v4 = v4[:n]
v5 = v5[:n]
v6 = v6[:n]

# ======================================================
# DERIVED QUANTITIES
# ======================================================

# Current through the 1 MΩ resistor (A1 -> A2)
current_A = (v4 - v5) / R_SHUNT_OHMS

# Voltage across the material (A2 -> A3)
material_voltage_V = v5 - v6

# Material resistance
resistance_ohm = np.where(
    np.abs(current_A) > EPS_CURRENT,
    material_voltage_V / current_A,
    np.nan
)

# Smoothed resistance for cleaner viewing
resistance_interp = pd.Series(resistance_ohm).interpolate(limit_direction="both").to_numpy()
resistance_smooth = (
    pd.Series(resistance_interp)
    .rolling(window=RES_SMOOTH_WINDOW, center=True, min_periods=1)
    .mean()
    .to_numpy()
)

# Save stitched data
stitched_csv = SAVE_FOLDER / f"{TEST_NAME}_stitched_voltage_data.csv"
pd.DataFrame({
    "time_s": time_full,
    "Voltage_4": v4,
    "Voltage_5": v5,
    "Voltage_6": v6,
    "current_A": current_A,
    "material_voltage_V": material_voltage_V,
    "resistance_ohm": resistance_ohm,
    "resistance_smooth_ohm": resistance_smooth,
}).to_csv(stitched_csv, index=False)
print(f"Saved stitched CSV: {stitched_csv}")

# ======================================================
# RAW VOLTAGE PLOTS + FFTs
# ======================================================

fig, ax = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
ax[0].plot(time_full, v4, lw=1)
ax[0].set_ylabel("Voltage_4 (V)")
ax[0].grid(True, alpha=0.3)

ax[1].plot(time_full, v5, lw=1)
ax[1].set_ylabel("Voltage_5 (V)")
ax[1].grid(True, alpha=0.3)

ax[2].plot(time_full, v6, lw=1)
ax[2].set_ylabel("Voltage_6 (V)")
ax[2].set_xlabel("Time (s)")
ax[2].grid(True, alpha=0.3)

fig.suptitle("Raw Voltage Channels")
fig.tight_layout()
fig.savefig(SAVE_FOLDER / f"{TEST_NAME}_raw_voltage_channels.png", dpi=300, bbox_inches="tight")
plt.show()

plot_fft(time_full, v4, "FFT of Voltage_4", SAVE_FOLDER / f"{TEST_NAME}_fft_voltage_4.png", xlim=RAW_FFT_XLIM)
plot_fft(time_full, v5, "FFT of Voltage_5", SAVE_FOLDER / f"{TEST_NAME}_fft_voltage_5.png", xlim=RAW_FFT_XLIM)
plot_fft(time_full, v6, "FFT of Voltage_6", SAVE_FOLDER / f"{TEST_NAME}_fft_voltage_6.png", xlim=RAW_FFT_XLIM)

# ======================================================
# RESISTANCE VS TIME + FFT
# ======================================================

plot_series(
    time_full,
    resistance_smooth,
    title="Material Resistance vs Time (Smoothed)",
    xlabel="Time (s)",
    ylabel="Resistance (Ohms)",
    outpath=SAVE_FOLDER / f"{TEST_NAME}_resistance_vs_time.png",
    sci_y=True,
)

plot_fft(
    time_full,
    resistance_smooth,
    title="Resistance FFT (Full Trace)",
    outpath=SAVE_FOLDER / f"{TEST_NAME}_resistance_fft_full.png",
    xlim=RES_FFT_XLIM,
)

# ======================================================
# ZOOMED RESISTANCE VIEW
# ======================================================

zoom_mask = (time_full >= ZOOM_START_S) & (time_full <= ZOOM_END_S)
if np.any(zoom_mask):
    plot_series(
        time_full[zoom_mask],
        resistance_smooth[zoom_mask],
        title="Material Resistance (Zoomed)",
        xlabel="Time (s)",
        ylabel="Resistance (Ohms)",
        outpath=SAVE_FOLDER / f"{TEST_NAME}_resistance_zoom.png",
        sci_y=True,
    )
else:
    print("Zoom window did not match any data points.")

# ======================================================
# STEADY-STATE AVERAGE PER PULSE
# ======================================================

phase = np.mod(time_full, CYCLE_S)
steady_mask = (phase >= STEADY_START_S) & (phase <= STEADY_END_S)

time_steady = time_full[steady_mask]
v4_steady = v4[steady_mask]
v5_steady = v5[steady_mask]
v6_steady = v6[steady_mask]

if len(time_steady) == 0:
    raise ValueError("No steady-state points found. Check STEADY_START_S and STEADY_END_S.")

cycle_index = np.floor(time_steady / CYCLE_S).astype(int)
unique_cycles = np.unique(cycle_index)

pulse_rows = []
for c in unique_cycles:
    m = cycle_index == c

    mean_v4 = np.mean(v4_steady[m])
    mean_v5 = np.mean(v5_steady[m])
    mean_v6 = np.mean(v6_steady[m])

    mean_current = (mean_v4 - mean_v5) / R_SHUNT_OHMS
    mean_material_voltage = mean_v5 - mean_v6

    if np.abs(mean_current) > EPS_CURRENT:
        mean_resistance = mean_material_voltage / mean_current
    else:
        mean_resistance = np.nan

    pulse_rows.append({
        "pulse_number": c,
        "steady_mean_V4": mean_v4,
        "steady_mean_V5": mean_v5,
        "steady_mean_V6": mean_v6,
        "steady_current_A": mean_current,
        "steady_material_voltage_V": mean_material_voltage,
        "steady_resistance_ohm": mean_resistance,
    })

pulse_df = pd.DataFrame(pulse_rows)

valid_r = pulse_df["steady_resistance_ohm"].to_numpy(dtype=float)
finite_idx = np.where(np.isfinite(valid_r))[0]
if len(finite_idx) == 0:
    raise ValueError("Could not compute any finite pulse resistance values.")

R0 = valid_r[finite_idx[0]]
print(f"Baseline resistance R0 = {R0:.6g} ohm")

pulse_df["delta_R_over_R0"] = (pulse_df["steady_resistance_ohm"] - R0) / R0
pulse_df["pulse_time_s"] = pulse_df["pulse_number"] * CYCLE_S

pulse_csv = SAVE_FOLDER / f"{TEST_NAME}_pulse_steady_state_resistance.csv"
pulse_df.to_csv(pulse_csv, index=False)
print(f"Saved pulse-average CSV: {pulse_csv}")

plot_series(
    pulse_df["pulse_number"].to_numpy(),
    pulse_df["steady_resistance_ohm"].to_numpy(),
    title="Average Steady-State Resistance per Pulse",
    xlabel="Pulse number",
    ylabel="Resistance (Ohms)",
    outpath=SAVE_FOLDER / f"{TEST_NAME}_resistance_per_pulse.png",
    sci_y=True,
)

plot_series(
    pulse_df["pulse_number"].to_numpy(),
    pulse_df["delta_R_over_R0"].to_numpy(),
    title="ΔR / R0 vs Pulse Number",
    xlabel="Pulse number",
    ylabel="ΔR / R0",
    outpath=SAVE_FOLDER / f"{TEST_NAME}_deltaR_over_R0.png",
    sci_y=False,
)

pulse_time = pulse_df["pulse_time_s"].to_numpy(dtype=float)
pulse_res = pulse_df["steady_resistance_ohm"].to_numpy(dtype=float)
valid = np.isfinite(pulse_time) & np.isfinite(pulse_res)

if np.sum(valid) >= 4:
    plot_fft(
        pulse_time[valid],
        pulse_res[valid],
        title="FFT of Pulse-Averaged Resistance",
        outpath=SAVE_FOLDER / f"{TEST_NAME}_pulse_average_resistance_fft.png",
        xlim=PULSE_RES_FFT_XLIM,
    )
else:
    print("Not enough pulse-average points for FFT.")

print("Done.")