import matplotlib.pyplot as plt
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

def read_voltage_data(filename):
    with open(filename, 'r') as file:
        data = [float(line.strip()) for line in file]
    return data

def plot_voltage_data(data):
    plt.figure(figsize=(10, 6))
    plt.plot(data)
    plt.xlabel('sample number')
    plt.ylabel('resistance (ohms)')
    plt.grid(True)
    plt.show()

if __name__ == '__main__':
    filename = './SD10Hz.txt'
    voltage_data = read_voltage_data(filename)
    plot_voltage_data(voltage_data)
