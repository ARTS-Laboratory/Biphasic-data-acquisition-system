import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.pyplot as plt
import json as json
import pandas as pd
import re

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

def read_voltage_data(filename):
    with open(filename, 'r') as file:
        data = [float(line.strip()) for line in file]
    return data

def extract_info_from_filename(filename):
    pattern = r'SD(\d+Hz)(\d+[kM]?)\.txt'
    match = re.search(pattern, filename)
    if match:
        return match.groups()
    else:
        return None, None

def plot_voltage_data(files):
    plt.figure(figsize=(10, 6))

    for filename in files:
        voltage_data = read_voltage_data(filename)
        freq, resistance = extract_info_from_filename(filename)
        label = f'{freq} {resistance}'
        plt.plot(voltage_data, label=label)

    plt.xlabel('sample number')
    plt.ylabel('resistance (Ohms)')
    plt.title('resistance over time with teensy prototype')
    plt.legend()
    plt.grid(True)
    plt.savefig('./plots/resistance_plot.png')
    plt.show()

if __name__ == '__main__':
    files = ['./SD1Hz680k.txt', './SD5Hz680k.txt', './SD10Hz680k.txt']
    plot_voltage_data(files)
