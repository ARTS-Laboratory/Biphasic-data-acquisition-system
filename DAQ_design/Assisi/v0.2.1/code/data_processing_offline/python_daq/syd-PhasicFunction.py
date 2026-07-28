# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 06:58:20 2026

@author: SLM30
"""

#%% import modules and set default fonts and colors
"""
Default plot formatting code for Austin Downey's series of open source notes/
books. This common header is used to set the fonts and format.
Header file last updated May 16, 2024
"""
from __future__ import annotations
from IPython import get_ipython
get_ipython().run_line_magic('reset', '-f') 

import argparse
import signal
import threading
import time
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from nidaqmx.stream_readers import AnalogMultiChannelReader

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
NI cDAQ acquisition script
Python replica of the current LabVIEW VI.

Features:
- 3 analog inputs: Voltage_4, Voltage_5, Voltage_6
- cDAQ3Mod1/ai4, ai5, ai6
- RSE, +/-10 V
- 1000 Hz sample rate
- 100 samples per read
- continuous acquisition
- live plotting
- LVM saving with LabVIEW-style formatting
- manual stop button
- optional timed stop
- sequential filenames in a chosen output folder
- Ctrl+C stop

Install:
    pip install nidaqmx numpy matplotlib
"""

#%% Configuration
DEVICE = "cDAQ3Mod1" # change for your specific NI cDAQ module
PHYSICAL_CHANNELS = ["ai4", "ai5", "ai6"]
CHANNEL_NAMES = ["Voltage_4", "Voltage_5", "Voltage_6"]

TERMINAL_CONFIG = TerminalConfiguration.RSE
V_MIN = -10.0
V_MAX = 10.0

SAMPLE_RATE_HZ = 1000.0
SAMPLES_PER_READ = 100
TIMEOUT_S = 1.0

# Set to None for manual stop only.
TEST_DURATION_MIN = 5.0

# Live plot update rate (every N reads)
PLOT_UPDATE_EVERY_N_READS = 5

# If True, plot full history like a LabVIEW chart.
# If False, show only the last ~30 s.
PLOT_FULL_HISTORY = True
PLOT_WINDOW_S = 30.0

# Default file stem
DEFAULT_FILE_STEM = "test"

#%% Helpers
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NI cDAQ acquisition script")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Folder where LVM files will be saved.",
    )
    parser.add_argument(
        "--stem",
        type=str,
        default=DEFAULT_FILE_STEM,
        help="Base filename stem (default: test).",
    )
    return parser.parse_args()


def get_output_dir_from_user(default: Path) -> Path:
    print(f"Enter output folder path or press Enter to use:\n{default}")
    raw = input("Output folder: ").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return default.resolve()


def next_sequential_path(folder: Path, stem: str, suffix: str = ".lvm") -> Path:
    """
    Create sequential filenames like:
        test_001.lvm
        test_002.lvm
        test_003.lvm
    in the chosen folder.
    """
    folder.mkdir(parents=True, exist_ok=True)

    existing_numbers = []
    for p in folder.glob(f"{stem}_*{suffix}"):
        name = p.stem  # e.g. test_003
        parts = name.rsplit("_", 1)
        if len(parts) == 2 and parts[1].isdigit():
            existing_numbers.append(int(parts[1]))

    next_num = 1 if not existing_numbers else max(existing_numbers) + 1
    return folder / f"{stem}_{next_num:03d}{suffix}"


def write_labview_lvm_header(fh, channel_names: list[str]) -> None:
    """
    Match LabVIEW Text (LVM) output closely enough for the same
    post-processing script to read it unchanged.
    """
    now = datetime.now()

    header_lines = [
        "LabVIEW Measurement",
        "Writer_Version\t2",
        "Reader_Version\t2",
        "Separator\tTab",
        "Decimal_Separator\t.",
        "Multi_Headings\tNo",
        "X_Columns\tOne",
        "Time_Pref\tRelative",
        f"Date\t{now.strftime('%m/%d/%Y')}",
        f"Time\t{now.strftime('%H:%M:%S.%f')[:-3]}",
        "Operator\t",
        "Description\t",
        "Y_Unit_Label\tVolts",
        "X_Unit_Label\tSeconds",
        "Logged Data\t",
        "***End_of_Header***",
        "X_Value\t" + "\t".join(channel_names),
    ]
    fh.write("\n".join(header_lines) + "\n")


def format_lvm_row(t: float, row: np.ndarray) -> str:
    return f"{t:.9f}\t{row[0]:.9f}\t{row[1]:.9f}\t{row[2]:.9f}\n"

#%% Main acquisition
def main() -> None:
    args = parse_args()

    default_root = Path.cwd()
    if args.output_dir is None:
        output_root = get_output_dir_from_user(default_root)
    else:
        output_root = Path(args.output_dir).expanduser().resolve()

    output_root.mkdir(parents=True, exist_ok=True)
    output_path = next_sequential_path(output_root, args.stem, ".lvm")

    print(f"Saving to: {output_path}")

    stop_event = threading.Event()

    def request_stop(*_args) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, request_stop)

    test_duration_s = None if TEST_DURATION_MIN is None else TEST_DURATION_MIN * 60.0
    run_start = time.monotonic()

    # Data storage for live plot
    all_time: list[float] = []
    all_v4: list[float] = []
    all_v5: list[float] = []
    all_v6: list[float] = []

    # Live plot setup
    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 6))
    (line_v4,) = ax.plot([], [], label="Voltage_4")
    (line_v5,) = ax.plot([], [], label="Voltage_5")
    (line_v6,) = ax.plot([], [], label="Voltage_6")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Voltage (V)")
    ax.grid(True)
    ax.legend(loc="upper right")
    ax.set_title("Live DAQ Acquisition")

    stop_ax = fig.add_axes([0.88, 0.01, 0.1, 0.05])
    stop_button = Button(stop_ax, "Stop")

    def on_stop_clicked(_event) -> None:
        stop_event.set()

    stop_button.on_clicked(on_stop_clicked)
    fig.canvas.mpl_connect("close_event", lambda _event: stop_event.set())

    plt.show(block=False)

    with output_path.open("w", newline="\n") as fh:
        write_labview_lvm_header(fh, CHANNEL_NAMES)

        with nidaqmx.Task() as task:
            # Add channels
            for phys_ch, name in zip(PHYSICAL_CHANNELS, CHANNEL_NAMES):
                task.ai_channels.add_ai_voltage_chan(
                    physical_channel=f"{DEVICE}/{phys_ch}",
                    name_to_assign_to_channel=name,
                    terminal_config=TERMINAL_CONFIG,
                    min_val=V_MIN,
                    max_val=V_MAX,
                )

            # Timing
            task.timing.cfg_samp_clk_timing(
                rate=SAMPLE_RATE_HZ,
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=max(1000, int(SAMPLES_PER_READ * 10)),
            )

            # Buffer size
            task.in_stream.input_buf_size = max(
                int(SAMPLE_RATE_HZ * 2),
                int(SAMPLES_PER_READ * 50),
            )

            task.start()
            reader = AnalogMultiChannelReader(task.in_stream)

            sample_index = 0
            read_count = 0

            print("Acquisition started.")
            print("Press Stop, close the plot window, or wait for the timer to finish.")

            try:
                while not stop_event.is_set():
                    # Timer stop
                    if test_duration_s is not None:
                        elapsed_s = time.monotonic() - run_start
                        if elapsed_s >= test_duration_s:
                            print(f"Timer stop reached at {elapsed_s / 60.0:.2f} min.")
                            break

                    # Read block
                    data = np.empty((len(CHANNEL_NAMES), SAMPLES_PER_READ), dtype=np.float64)
                    reader.read_many_sample(
                        data,
                        number_of_samples_per_channel=SAMPLES_PER_READ,
                        timeout=TIMEOUT_S,
                    )

                    # Relative time vector
                    t = (sample_index + np.arange(SAMPLES_PER_READ)) / SAMPLE_RATE_HZ
                    sample_index += SAMPLES_PER_READ

                    # Write rows to LVM
                    out = np.column_stack((t, data.T))
                    for row in out:
                        fh.write(format_lvm_row(row[0], row[1:]))
                    fh.flush()

                    # Store for live plotting
                    all_time.extend(t.tolist())
                    all_v4.extend(data[0, :].tolist())
                    all_v5.extend(data[1, :].tolist())
                    all_v6.extend(data[2, :].tolist())

                    read_count += 1

                    # Update plot
                    if read_count % PLOT_UPDATE_EVERY_N_READS == 0:
                        line_v4.set_data(all_time, all_v4)
                        line_v5.set_data(all_time, all_v5)
                        line_v6.set_data(all_time, all_v6)

                        if PLOT_FULL_HISTORY:
                            ax.relim()
                            ax.autoscale_view()
                        else:
                            if all_time:
                                xmax = all_time[-1]
                                ax.set_xlim(max(0.0, xmax - PLOT_WINDOW_S), xmax)

                        fig.canvas.draw_idle()
                        fig.canvas.flush_events()
                        plt.pause(0.001)

            except Exception as exc:
                print(f"Error during acquisition: {exc}")
                stop_event.set()
                raise

            finally:
                try:
                    task.stop()
                except Exception:
                    pass

    plt.ioff()
    plt.show()

    print("Acquisition complete.")
    print(f"LVM saved: {output_path}")


if __name__ == "__main__":
    main()