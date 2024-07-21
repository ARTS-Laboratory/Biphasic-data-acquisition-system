import pandas as pd
import matplotlib.pyplot as plt
import json as json
import pandas as pd

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

file_path = './1Hz.lvm'

data = pd.read_csv(file_path, sep='\t', skiprows=23, names=['X_Value', 'Voltage'], usecols=['Voltage'])

data['Time'] = data.index * 0.000200

plt.figure(figsize=(10, 5))
plt.plot(data['Time'], data['Voltage'], label='Voltage over Time')
plt.xlabel('time (s)')
plt.ylabel('voltage (V)')
plt.title('Biphasic 1Hz')
plt.grid(True)
plt.savefig('./plots/biphasic1Hz.png')
plt.show()
