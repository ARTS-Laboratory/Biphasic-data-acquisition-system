import matplotlib.pyplot as plt
import pandas as pd

# Set default fonts and plot colors
plt.rcParams.update({'text.usetex': True})
plt.rcParams.update({'image.cmap': 'viridis'})
plt.rcParams.update({'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif',
                                    'Bitstream Vera Serif', 'Computer Modern Roman', 'New Century Schoolbook',
                                    'Century Schoolbook L', 'Utopia', 'ITC Bookman', 'Bookman',
                                    'Nimbus Roman No9 L', 'Palatino', 'Charter', 'serif']})
plt.rcParams.update({'font.family': 'serif'})
plt.rcParams.update({'font.size': 9})
plt.rcParams.update({'mathtext.rm': 'serif'})
plt.rcParams.update({'mathtext.fontset': 'custom'})
cc = plt.rcParams['axes.prop_cycle'].by_key()['color']
plt.close('all')

def read_voltage_data(filename):
    data = pd.read_csv(filename, header=None, names=['timestamp', 'voltage'])
    return data

def plot_voltage_data(files, labels):
    plt.figure(figsize=(10, 6))

    for filename, label in zip(files, labels):
        data = read_voltage_data(filename)
        plt.plot(data['timestamp'], data['voltage'], label=label)

    plt.xlabel('time (ms)')
    plt.ylabel('resistance (Ohms)')
    plt.title('10 minutes, 220k Ohm')
    plt.legend()
    plt.grid(True)
    plt.savefig('./plots/220k_resistance_plot_10min.png')
    plt.show()

if __name__ == '__main__':
    files = ['./DC.txt',  './1Hz.txt', './2Hz.txt', './5Hz.txt',
             './10Hz.txt', './20Hz.txt']
    labels = ['DC', '1Hz', '2Hz', '5Hz', '10Hz', '20Hz']
    plot_voltage_data(files, labels)
