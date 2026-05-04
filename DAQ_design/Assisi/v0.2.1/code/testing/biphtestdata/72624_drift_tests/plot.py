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

    plt.xlabel('timestamp')
    plt.ylabel('resistance (Ohms)')
    plt.title('5  minutes, 1Hz')
    plt.legend()
    plt.grid(True)
    plt.savefig('./plots/voltage_plot.png')
    plt.show()

if __name__ == '__main__':
    files = ['./680k1Hz.txt', './1p5M1Hz.txt', './2M1Hz.txt', './4p7M1Hz.txt']
    labels = ['680k 1Hz', '1.5M 1Hz', '2M 1Hz', '4.7M 1Hz']
    plot_voltage_data(files, labels)
