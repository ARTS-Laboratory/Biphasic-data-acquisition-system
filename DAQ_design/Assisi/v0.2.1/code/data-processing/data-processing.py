# -*- coding: utf-8 -*-

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
LabVIEW .lvm parser for repeated Voltage_5 blocks.

What it does:
- Reads a LabVIEW Measurement .lvm file (or renamed .txt)
- Finds the tabular data after ***End_of_Header***
- Collects every column whose name starts with "Voltage_5"
- Stitches those columns into one continuous trace
- Plots:
    1) full Voltage_5 vs time
    2) zoomed Voltage_5 vs time
    3) FFT of the full trace
    4) FFT of the zoomed trace
    5) steady-state window inside each 1 Hz cycle
- Saves figures into ./figures

Edit only the settings near the top.
"""

# ======================================================
# USER SETTINGS
# ======================================================

# Your LabVIEW export file (.lvm is preferred, but .txt also works)
FILENAME = "test_1.lvm"

# Output folder for plots
SAVE_FOLDER = Path("figures")
SAVE_FOLDER.mkdir(exist_ok=True)

# If your Arduino runs at 1 Hz, one cycle is 1 second.
CYCLE_S = 1.0

# Choose the middle portion of each cycle for the steady-state view
STEADY_START_S = 0.30
STEADY_END_S = 0.80

# Zoom window in the full stitched trace (seconds)
ZOOM_START_S = 20.0
ZOOM_END_S = 25.0

# Column to analyze (all columns starting with this label are stitched)
TARGET_PREFIX = "Voltage_5"


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


def normalize_column_name(name: str) -> str:
    """Normalize a column name so repeated names like 'Voltage_5 1' still match."""
    return str(name).strip()


def natural_key(name: str):
    """
    Sort strings in a human-friendly way:
    Voltage_5, Voltage_5 1, Voltage_5 2, ...
    """
    parts = re.split(r"(\d+)", str(name))
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def plot_signal(x, y, title, xlabel, ylabel, filename, xlim=None):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(x, y, lw=1)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    if xlim is not None:
        ax.set_xlim(*xlim)
    fig.tight_layout()
    fig.savefig(SAVE_FOLDER / filename, dpi=300, bbox_inches="tight")
    plt.show()


def plot_fft(x, y, title, filename, xlim=(0, 100)):
    """
    FFT with DC removed.
    x must be a 1D time axis in seconds.
    """
    x = np.asarray(x)
    y = np.asarray(y)

    if len(x) < 4:
        raise ValueError("Not enough points for FFT.")

    dt = np.median(np.diff(x))
    if not np.isfinite(dt) or dt <= 0:
        raise ValueError("Invalid time spacing for FFT.")

    fs = 1.0 / dt
    y = y - np.mean(y)

    freqs = rfftfreq(len(y), d=dt)
    mag = np.abs(rfft(y)) / len(y)

    # dominant frequency, ignoring DC
    if len(mag) > 1:
        peak_idx = np.argmax(mag[1:]) + 1
        dom_f = freqs[peak_idx]
        print(f"{title}: dominant frequency = {dom_f:.3f} Hz")
    else:
        print(f"{title}: not enough points to determine dominant frequency.")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(freqs, mag, lw=1)
    ax.set_title(title)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Magnitude")
    ax.set_xlim(*xlim)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(SAVE_FOLDER / filename, dpi=300, bbox_inches="tight")
    plt.show()


# ======================================================
# LOAD FILE
# ======================================================

path = Path(FILENAME).expanduser().resolve()
if not path.exists():
    raise FileNotFoundError(f"File not found: {path}")

header_row = find_header_row(path)

# Read the tabular section
df = pd.read_csv(path, sep="\t", skiprows=header_row, engine="python")
df.columns = [normalize_column_name(c) for c in df.columns]

# Convert everything possible to numeric
for c in df.columns:
    df[c] = pd.to_numeric(df[c], errors="coerce")

print("Columns found:")
print(df.columns.tolist())

# First column should be X_Value
time_col = df.columns[0]
if "X_Value" not in str(time_col):
    print(f"Warning: first column is '{time_col}', not obviously X_Value.")

# ======================================================
# PICK ALL Voltage_5 COLUMNS
# ======================================================

v5_cols = [c for c in df.columns if str(c).startswith(TARGET_PREFIX)]
v5_cols = sorted(v5_cols, key=natural_key)

if len(v5_cols) == 0:
    raise ValueError(f"No columns starting with '{TARGET_PREFIX}' were found.")

print(f"Found {len(v5_cols)} '{TARGET_PREFIX}' columns:")
for c in v5_cols[:10]:
    print("  ", c)
if len(v5_cols) > 10:
    print("  ...")

# Use the X_Value column from the first block to get block timing
time_block = df[time_col].to_numpy()
time_block = time_block[np.isfinite(time_block)]

if len(time_block) < 2:
    raise ValueError("Not enough X_Value points to infer block timing.")

dt_block = np.median(np.diff(time_block))
if not np.isfinite(dt_block) or dt_block <= 0:
    raise ValueError("Invalid dt inferred from X_Value.")

block_duration = time_block[-1] + dt_block

# Stitch all Voltage_5 blocks into one long trace
time_full_list = []
voltage_full_list = []

for i, col in enumerate(v5_cols):
    y = df[col].to_numpy()
    valid = np.isfinite(y)

    # Build a fresh time axis for this block, then shift it forward
    t = time_block[:len(y)] + i * block_duration

    # Keep only finite paired samples
    n = min(len(t), len(y))
    t = t[:n]
    y = y[:n]

    valid = np.isfinite(t) & np.isfinite(y)
    time_full_list.append(t[valid])
    voltage_full_list.append(y[valid])

time_full = np.concatenate(time_full_list)
voltage_full = np.concatenate(voltage_full_list)

# Sort by time in case anything came in out of order
sort_idx = np.argsort(time_full)
time_full = time_full[sort_idx]
voltage_full = voltage_full[sort_idx]

print(f"Stitched points: {len(time_full)}")
print(f"Approx. duration: {time_full[-1] - time_full[0]:.3f} s")

# Save stitched data
stitched_csv = SAVE_FOLDER / "Voltage_5_stitched.csv"
pd.DataFrame({"time_s": time_full, "Voltage_5": voltage_full}).to_csv(stitched_csv, index=False)
print(f"Saved stitched CSV: {stitched_csv}")

# ======================================================
# FULL PLOT
# ======================================================

plot_signal(
    time_full,
    voltage_full,
    title="Voltage_5 (Full Stitched Recording)",
    xlabel="Time (s)",
    ylabel="Voltage (V)",
    filename="Voltage_5_full.png",
)

# ======================================================
# FULL FFT
# ======================================================

plot_fft(
    time_full,
    voltage_full,
    title="Voltage_5 FFT (Full Stitched Recording)",
    filename="Voltage_5_FFT_full.png",
    xlim=(0, 100),
)

# ======================================================
# ZOOMED WINDOW
# ======================================================

zoom_mask = (time_full >= ZOOM_START_S) & (time_full <= ZOOM_END_S)
if not np.any(zoom_mask):
    raise ValueError("Zoom window did not match any data. Adjust ZOOM_START_S / ZOOM_END_S.")

time_zoom = time_full[zoom_mask]
voltage_zoom = voltage_full[zoom_mask]

plot_signal(
    time_zoom,
    voltage_zoom,
    title="Voltage_5 (Zoomed Section)",
    xlabel="Time (s)",
    ylabel="Voltage (V)",
    filename="Voltage_5_zoom.png",
)

plot_fft(
    time_zoom,
    voltage_zoom,
    title="Voltage_5 FFT (Zoomed Section)",
    filename="Voltage_5_FFT_zoom.png",
    xlim=(0, 100),
)

# ======================================================
# STEADY-STATE REGION INSIDE EACH 1 Hz CYCLE
# ======================================================

phase = np.mod(time_full, CYCLE_S)
steady_mask = (phase >= STEADY_START_S) & (phase <= STEADY_END_S)

time_steady = time_full[steady_mask]
voltage_steady = voltage_full[steady_mask]

if len(time_steady) > 0:
    plot_signal(
        time_steady,
        voltage_steady,
        title="Voltage_5 (Steady-State Portion of Each Cycle)",
        xlabel="Time (s)",
        ylabel="Voltage (V)",
        filename="Voltage_5_steady.png",
    )

    plot_fft(
        time_steady,
        voltage_steady,
        title="Voltage_5 FFT (Steady-State Portion)",
        filename="Voltage_5_FFT_steady.png",
        xlim=(0, 100),
    )
else:
    print("No steady-state points found. Check STEADY_START_S and STEADY_END_S.")

# ======================================================
# AVERAGE STEADY-STATE VOLTAGE PER PULSE
# ======================================================

# Which pulse (cycle) each steady-state sample belongs to
cycle_index = np.floor(time_steady / CYCLE_S).astype(int)

pulse_numbers = []
steady_means = []

for c in np.unique(cycle_index):
    vals = voltage_steady[cycle_index == c]
    if len(vals) > 0:
        pulse_numbers.append(c)
        steady_means.append(np.mean(vals))

pulse_numbers = np.array(pulse_numbers)
steady_means = np.array(steady_means)

# Save the pulse-averaged steady-state data
avg_csv = SAVE_FOLDER / "Voltage_5_steady_averages.csv"
pd.DataFrame({
    "pulse_number": pulse_numbers,
    "steady_state_voltage_mean": steady_means
}).to_csv(avg_csv, index=False)

print(f"Saved steady-state averages: {avg_csv}")

# Plot the averaged steady-state voltage
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(pulse_numbers, steady_means, marker="o", lw=1)
ax.set_title("Voltage_5: Average Steady-State Voltage per Pulse")
ax.set_xlabel("Pulse number")
ax.set_ylabel("Average Voltage (V)")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(SAVE_FOLDER / "Voltage_5_steady_averages.png", dpi=300, bbox_inches="tight")
plt.show()

print("Done.")