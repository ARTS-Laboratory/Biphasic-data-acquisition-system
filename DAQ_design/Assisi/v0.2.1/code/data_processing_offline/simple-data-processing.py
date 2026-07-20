# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 09:38:22 2026

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

#%% save settings
# !!!!YOU HAVE TO CHANGE THESE EVERY NEW TEST!!!!
TEST_FOLDER = "07152026" # folder you're using
TEST_FILE = "test_1.lvm" # your data file from labview

FILENAME = Path(TEST_FOLDER) / TEST_FILE # path to save to

TEST_NAME = FILENAME.stem # name files after your data file

SAVE_FOLDER = Path(TEST_FOLDER) / "figures" 
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)

#%% data prep
# Use the filename you already defined
filename = FILENAME # yes, this is lazy. next.

# Find the row that contains the real column headers
with open(filename, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

header_row = None
for i, line in enumerate(lines):
    if line.startswith("X_Value"):
        header_row = i
        break

if header_row is None:
    raise ValueError("Could not find X_Value header row.")

# Read the file using that header row
df = pd.read_csv(filename, sep="\t", header=header_row, engine="python")
df.columns = df.columns.astype(str).str.strip()

# Convert numeric columns
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop blank rows
df = df.dropna(subset=[df.columns[0]]).reset_index(drop=True)

# Find all repeated columns
v4_cols = [c for c in df.columns if c.startswith("Voltage_4")]
v5_cols = [c for c in df.columns if c.startswith("Voltage_5")]
v6_cols = [c for c in df.columns if c.startswith("Voltage_6")]

print(len(v4_cols), len(v5_cols), len(v6_cols)) # you want these to match

# Time inside one block
time_block = df["X_Value"].to_numpy()
dt = np.median(np.diff(time_block))
block_duration = time_block[-1] + dt

# Stitch time and voltage columns into continuous
nblocks = min(len(v4_cols), len(v5_cols), len(v6_cols))

time_full = np.concatenate([time_block + i * block_duration for i in range(nblocks)])
v4_full = np.concatenate([df[c].to_numpy() for c in v4_cols[:nblocks]])
v5_full = np.concatenate([df[c].to_numpy() for c in v5_cols[:nblocks]])
v6_full = np.concatenate([df[c].to_numpy() for c in v6_cols[:nblocks]])

#%% core calculations
Rshunt = 1000000 # your plug's resistor in ohms
Vshunt = v4_full - v5_full # voltage drop after Rshunt
Vmat = v5_full - v6_full # voltage across material
I = Vshunt / Rshunt # current after resistor
Rmat = Vmat / I # resistance of material

#%% steady-state Ravg
# Find where the resistance crosses 0.5 MΩ
low_thres = 0.5e6
high_thres = 1.2e6

pulse_wait = 0.25
read_len = 0.20
read_delay = 3.0

Rpulse = []
pulse_time = []

# Find the rising edges
rising = np.where(
    (Rmat[:-1] < low_thres) &
    (Rmat[1:] >= low_thres)
)[0] + 1

# Skip the first rising edge (startup transient)
for start in rising[1:]:

    start_time = time_full[start]

    average_start = start_time + pulse_wait
    average_end = average_start + read_len

    mask = (
        (time_full >= average_start) &
        (time_full <= average_end)
    )

    Rpulse.append(np.mean(Rmat[mask]))
    pulse_time.append(average_start)

# Convert to NumPy arrays
pulse_time = np.array(pulse_time)
Rpulse = np.array(Rpulse)

keep = (pulse_time > read_delay) & (Rpulse > low_thres) & (Rpulse < high_thres)
pulse_time = pulse_time[keep]
Rpulse = Rpulse[keep]

#%% save steady-state Ravg per pulse in CSV
Ravg_df = pd.DataFrame({
    "Time (s)": pulse_time,
    "Average Resistance (Ohms)": Rpulse
})

Ravg_df.to_csv(
    SAVE_FOLDER / f"{TEST_NAME}_Ravg_per_pulse.csv",
    index=False
)

print("Average resistance per pulse CSV saved.")

#%% steady-state fft
# Remove NaNs
valid = np.isfinite(time_full) & np.isfinite(Rmat)

t = time_full[valid]
R = Rmat[valid]

# Remove the DC offset (mean)
R = R - np.mean(R)

# Sampling interval
dt = np.median(np.diff(t))

# FFT
freq = rfftfreq(len(R), d=dt)
fft = np.abs(rfft(R))

peak = np.argmax(fft[1:]) + 1

print("Dominant frequency:", freq[peak], "Hz")

#%% plots

'''
# A2 vs T: whole experiment
plt.figure()
plt.plot(time_full, v5_full)
plt.xlabel("time (s)")
plt.ylabel("voltage (V)")
plt.title("raw curve (A2) vs time")
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-A2-vs-T.png",
            dpi=300,
            bbox_inches="tight")

# A2 vs T: zoom
plt.figure()
plt.plot(time_full, v5_full)
plt.xlabel("time (s)")
plt.ylabel("voltage (V)")
plt.title("raw curve (A2) vs time (zoom)")
plt.xlim(20,22)
plt.ylim(4,5)
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-zoom-A2-vs-T.png",
            dpi=300,
            bbox_inches="tight")

# Vmat vs T: whole experiment
plt.figure()
plt.plot(time_full, Vmat)
plt.xlabel("time (s)")
plt.ylabel("voltage (V)")
plt.title("material voltage vs time")
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-Vmat-vs-T.png",
            dpi=300,
            bbox_inches="tight")

# Vmat vs T: zoom
plt.figure()
plt.plot(time_full, Vmat)
plt.xlabel("time (s)")
plt.ylabel("voltage (V)")
plt.title("material voltage vs time (zoom)")
plt.xlim(20,22)
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-zoom-Vmat-vs-T.png",
            dpi=300,
            bbox_inches="tight")

# Rmat vs T: whole experiment
plt.figure()
plt.plot(time_full, Rmat)
plt.xlabel("time (s)")
plt.ylabel("resistance (ohms)")
plt.title("material resistance vs time")
plt.xlim(0,120)
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-Rmat-vs-T.png",
            dpi=300,
            bbox_inches="tight")

# Rmat vs T: zoom
plt.figure()
plt.plot(time_full, Rmat)
plt.xlabel("time (s)")
plt.ylabel("resistance (ohms)")
plt.title("material resistance vs time (zoom)")
plt.xlim(20,22)
plt.ylim(-500000,1500000)
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-zoom-Rmat-vs-T.png",
            dpi=300,
            bbox_inches="tight")

# steady-state Ravg PER pulse over time
plt.figure()
plt.plot(pulse_time, Rpulse, 'o-')
plt.xlabel("Time (s)")
plt.ylabel("Average Resistance (Ω)")
plt.title("Average Steady-State Resistance vs Time")
plt.ylim(5e5, 15e5)
plt.xlim(0,120)
plt.grid(True)
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-ss-ravg-pp-vs-t.png",
            dpi=300,
            bbox_inches="tight")

plt.figure()
plt.plot(freq, fft)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.title("FFT of Resistance")
plt.grid(True)
'''
print('All plots generated and saved.')