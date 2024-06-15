import matplotlib.pyplot as plt
import numpy as np
import os
import labellines

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

file_names = ['1ohm.txt', '10ohm.txt', '100ohm.txt', '680ohm.txt', '3p3kohm.txt', '7p5kohm.txt', '15kohm.txt', '56kohm.txt',
              '100kohm.txt', '330kohm.txt', '680kohm.txt', '1p5Mohm.txt', '3p3Mohm.txt']
labels = ['1 $\Omega$', '10 $\Omega$', '100 $\Omega$', '680 $\Omega$', '3.3 k$\Omega$', '7.5 k$\Omega$', '15 k$\Omega$', '56 k$\Omega$',
        '100 k$\Omega$', '330 k$\Omega$', '680 k$\Omega$', '1.5 M$\Omega$', '3.3 M$\Omega$']

plt.figure(figsize=(5, 5))

ax = plt.axes()
ax.set_xlabel('time (ms)')
ax.set_ylabel('resistance (ohms)')

for i, file_name in enumerate(file_names):
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
        plt.plot(time_ms, resistance_ohms, label=labels[i])

plt.title('Drift Tests - 120s - 5Hz')
#plt.legend()
lines = plt.gca().get_lines()
labellines.labelLines(lines, align=True)
plt.tight_layout()
plt.savefig('./figs/drift_testing.png', dpi=300)
plt.show()
