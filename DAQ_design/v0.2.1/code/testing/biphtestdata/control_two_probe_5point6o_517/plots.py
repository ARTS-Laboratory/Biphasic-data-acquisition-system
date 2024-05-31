import matplotlib.pyplot as plt
import numpy as np
import os

# set default fonts and plot colors
plt.rcParams.update({'text.usetex': True})
plt.rcParams.update({'image.cmap': 'viridis'})
plt.rcParams.update({'font.serif':['Times New Roman', 'Times', 'DejaVu Serif',
 'Bitstream Vera Serif', 'Computer Modern Roman', 'New Century Schoolbook',
 'Century Schoolbook L',  'Utopia', 'ITC Bookman', 'Bookman', 
 'Nimbus Roman No9 L', 'Palatino', 'Charter', 'serif']})
plt.rcParams.update({'font.family':'serif'})
plt.rcParams.update({'font.size': 9})
plt.rcParams.update({'mathtext.rm': 'serif'})
plt.rcParams.update({'mathtext.fontset': 'custom'}) # I don't think I need this as its set to 'stixsans' above.
cc = plt.rcParams['axes.prop_cycle'].by_key()['color']
plt.close('all')

file_names = ['1Hz_control.txt', '2Hz_control.txt', '5Hz_control.txt', '10Hz_control.txt', '20Hz_control.txt']

plt.figure(figsize=(12, 8))

ax = plt.axes()
ax.set_xlabel('time (ms)')
ax.set_ylabel('resistance (ohms)')

for file_name in file_names:
    file_path = os.path.join('./data', file_name)
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) == 2:
                try:
                    data.append([float(part) for part in parts])
                except ValueError:
                    continue

    if data:
        data = np.array(data)
        time_ms = data[:, 0]
        resistance_ohms = -data[:, 1]
        plt.plot(time_ms, resistance_ohms, label=file_name)

plt.title('Two probe control, 5.6Mohm known resistor')
plt.legend()
plt.tight_layout()
plt.savefig('./figs/two_probe_control_5p6_517.png', dpi=300)
plt.show()
