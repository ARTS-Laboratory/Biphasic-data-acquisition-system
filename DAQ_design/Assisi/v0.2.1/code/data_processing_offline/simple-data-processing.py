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
from scipy.signal import butter, filtfilt

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
TEST_FOLDER = "07212026/test_2" # folder you're using
TEST_FILE = "test_2.lvm" # your data file from labview

FILENAME = Path(TEST_FOLDER) / TEST_FILE # path to save to

TEST_NAME = FILENAME.stem # name figures after your data file

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
v5_full = np.concatenate([df[c].to_numpy() for c in v5_cols[:nblocks]]) # resistance curve
v6_full = np.concatenate([df[c].to_numpy() for c in v6_cols[:nblocks]])

# rewrite voltages to match wiring diagram
v1 = v6_full # before resistor
v2 = v5_full # after resistor
v3 = v4_full # across material

#%% optional lowpass filter
# lowpass filters are the general purpose option
# they reduce high freq and preserve low freq trends
USE_FILTER = True # true is on, false is off

if USE_FILTER:

    fs = 1.0 / dt      # sample rate from the data
    cutoff = 30.0      # freq in Hz
    order = 4          # filter intensity, higher = stricter

    b, a = butter(order, cutoff / (fs / 2), btype="low")
    # butterworth is another general purpose option

    v1_use = filtfilt(b, a, v1)
    v2_use = filtfilt(b, a, v2)
    v3_use = filtfilt(b, a, v3)
else:
    v1_use = v1
    v2_use = v2
    v3_use = v3

#%% core calculations
Rshunt = 1e6 # your plug's resistor (Rshunt) in ohms
Vshunt = v1_use - v2_use # voltage drop after Rshunt
Vmat = v2_use - v3_use # voltage across material
I = Vshunt / Rshunt # current after resistor
Rmat = Vmat / I # resistance of material

#%% steady-state Ravg
# resistance bounds
low_thres = 0.5e6 # must be higher than this (ohms)
high_thres = 1.2e6 # must be lower than this (ohms)

read_delay = 8.0 # wait this long after experiment start to read (s)
pulse_wait = 0.25 # wait this long after bound trigger to read (s)
read_len = 0.20 # read for this long (s)

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

    if np.sum(mask) == 0:
        print(f"No samples found between {average_start:.3f} and {average_end:.3f}")
        continue

    Rpulse.append(np.mean(Rmat[mask]))
    pulse_time.append(average_start)

# Convert to NumPy arrays
pulse_time = np.array(pulse_time)
Rpulse = np.array(Rpulse)

# Keep only valid points based on the raw signal
keep = (pulse_time > read_delay) & (Rpulse > low_thres) & (Rpulse < high_thres)

pulse_time = pulse_time[keep]
Rpulse = Rpulse[keep]

# Make the x-axis evenly spaced: one point per pulse
pulse_time = np.arange(len(Rpulse))

#%% save steady-state Ravg per pulse in CSV
Ravg_df = pd.DataFrame({
    "Time (s)": pulse_time,
    "Average Resistance (Ohms)": Rpulse
})

Ravg_df.to_csv(
    SAVE_FOLDER / f"{TEST_NAME}_Ravg_per_pulse.csv",
    index=False
)

print("Average steady-state resistance per pulse CSV saved.")

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

plt.plot(time_full, Vmat)
plt.plot(time_full, Vshunt)

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
'''
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
'''
# Vmat vs T: whole experiment
plt.figure()
plt.plot(time_full, Vmat)
plt.xlabel("time (s)")
plt.ylabel("voltage (V)")
plt.title("material voltage vs time")
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-Vmat-vs-T.png",
            dpi=300,
'''
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
'''
# Rmat vs T: whole experiment
plt.figure()
plt.plot(time_full, Rmat_use)
plt.xlabel("time (s)")
plt.ylabel("resistance (ohms)")
plt.title("material resistance vs time")
plt.xlim(0,120)
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-Rmat-vs-T.png",
            dpi=300,
            bbox_inches="tight")
'''
# Rmat vs T: zoom
plt.figure()
plt.plot(time_full, Rmat)
plt.xlabel("time (s)")
plt.ylabel("resistance (ohms)")
plt.title("material resistance vs time (zoom)")
plt.xlim(20,22)
plt.ylim(5e5,70e6)
plt.tight_layout()
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-zoom-Rmat-vs-T.png",
            dpi=300,
            bbox_inches="tight")

# steady-state Ravg PER pulse over time
plt.figure()
plt.plot(pulse_time, Rpulse, 'o-')
plt.xlabel("pulse number")
plt.ylabel("Average Resistance (Ω)")
plt.title("Average Steady-State Resistance vs Time")
plt.ylim(9e5, 1e6)
plt.xlim(0,45)
plt.grid(True)
plt.savefig(SAVE_FOLDER / f"{TEST_NAME}-ss-ravg-pp-vs-t.png",
            dpi=300,
            bbox_inches="tight")
'''
# FFT
plt.figure()
plt.plot(freq, fft)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.title("FFT of Resistance")
plt.grid(True)
'''
print('All plots generated and saved.')