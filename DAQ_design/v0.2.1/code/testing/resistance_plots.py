import matplotlib.pyplot as plt
import numpy as np
import os

good_files = ['1Hz.txt', '2Hz.txt', '5Hz.txt', '10Hz.txt']
cracked_files = ['1HzCracked.txt', '2HzCracked.txt', '5HzCracked.txt', '10HzCracked.txt']
good_labels = ['1Hz Solid', '2Hz Solid', '5Hz Solid', '10Hz Solid']
cracked_labels = ['1Hz Cracked', '2Hz Cracked', '5Hz Cracked', '10Hz Cracked']

all_files = good_files + cracked_files
all_labels = good_labels + cracked_labels

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(12, 10))

for file_name, label in zip(good_files, good_labels):
    file_path = os.path.join('./biphtestdata/', file_name)
    data = np.loadtxt(file_path, delimiter=',')
    time_ms = data[:, 0]
    resistance_ohms = data[:, 1]
    axes[0].plot(time_ms, resistance_ohms, label=label)

axes[0].set_xlabel('time (ms)')
axes[0].set_ylabel('resistance (ohms)')
axes[0].legend()
axes[0].grid(True)

for file_name, label in zip(cracked_files, cracked_labels):
    file_path = os.path.join('./biphtestdata/', file_name)
    data = np.loadtxt(file_path, delimiter=',')
    time_ms = data[:, 0]
    resistance_ohms = data[:, 1]
    axes[1].plot(time_ms, resistance_ohms, label=label)

axes[1].set_xlabel('time (ms)')
axes[1].set_ylabel('resistance (ohms)')
axes[1].legend()
axes[1].grid(True)

for file_name, label in zip(all_files, all_labels):
    file_path = os.path.join('./biphtestdata/', file_name)
    data = np.loadtxt(file_path, delimiter=',')
    time_ms = data[:, 0]
    resistance_ohms = data[:, 1]
    axes[2].plot(time_ms, resistance_ohms, label=label)

axes[2].set_xlabel('time (ms)')
axes[2].set_ylabel('resistance (ohms)')
axes[2].legend()
axes[2].grid(True)

plt.suptitle('330 ohm, 5V H-brdige, solid and cracked sample')
plt.tight_layout()

plt.show()
