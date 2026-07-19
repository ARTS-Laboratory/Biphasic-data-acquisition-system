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

TEST_FOLDER = "07152026"
TEST_FILE = "test_1.lvm"

FILENAME = Path(TEST_FOLDER) / TEST_FILE

TEST_NAME = FILENAME.stem

SAVE_FOLDER = Path(TEST_FOLDER) / "figures"
SAVE_FOLDER.mkdir(parents=True, exist_ok=True)

# Use the filename you already defined
filename = FILENAME

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

print(len(v4_cols), len(v5_cols), len(v6_cols))

# Time inside one block
time_block = df["X_Value"].to_numpy()
dt = np.median(np.diff(time_block))
block_duration = time_block[-1] + dt

# Stitch time and voltage columns
nblocks = min(len(v4_cols), len(v5_cols), len(v6_cols))

time_full = np.concatenate([time_block + i * block_duration for i in range(nblocks)])
v4_full = np.concatenate([df[c].to_numpy() for c in v4_cols[:nblocks]])
v5_full = np.concatenate([df[c].to_numpy() for c in v5_cols[:nblocks]])
v6_full = np.concatenate([df[c].to_numpy() for c in v6_cols[:nblocks]])

plt.figure()
plt.plot(time_full, v5_full)
plt.xlabel("time (s)")
plt.ylabel("voltage (V)")
plt.title("raw voltage (A2) vs time")
plt.tight_layout()

Rshunt = 1000000 # in ohms

Vshunt = v4_full - v5_full

Vmat = v5_full - v6_full
plt.figure()
plt.plot(time_full, Vmat)
plt.xlabel("time (s)")
plt.ylabel("voltage (V)")
plt.title("material voltage vs time")
plt.tight_layout()

I = Vshunt / Rshunt

Rmat = Vmat / I
plt.figure()
plt.plot(time_full, Rmat)
plt.xlabel("time (s)")
plt.ylabel("resistance (ohms)")
plt.title("resistance vs time")
plt.xlim(0,120)
plt.tight_layout()