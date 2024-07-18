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



def read_data(file_path):
    data = pd.read_csv(file_path, sep='\t', comment='*', skiprows=24, header=None, names=['X_Value', 'Voltage_0', 'Voltage_1'])
    return data

file_paths = ['./data100o.lvm', './data10ko.lvm', './data10ko2.lvm', './data100ko.lvm', './data680ko.lvm']
test_names = ['100 Ohm', '10 kOhm', '10 kOhm 2', '100 kOhm', '680 kOhm']

for i, file_path in enumerate(file_paths):
    data = read_data(file_path)

    plt.figure(figsize=(10, 10))

    plt.subplot(2, 1, 1)
    plt.plot(data['Voltage_0'])
    plt.title(f'{test_names[i]}: Channel 0')
    plt.xlabel('sample')
    plt.ylabel('voltage (V)')

    plt.subplot(2, 1, 2)
    plt.plot(data['Voltage_1'])
    plt.title(f'{test_names[i]}: Channel 1')
    plt.xlabel('sample')
    plt.ylabel('voltage (V)')

    plt.tight_layout()
    plt.savefig(f'./plots/{test_names[i]}.png')
    plt.show()
