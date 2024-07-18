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


def read_adc_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    start_index = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('X_Value'):
            start_index = i + 1
            break

    data = pd.read_csv(file_path, skiprows=start_index)
    data.columns = [col.strip() for col in data.columns]

    data.columns = ['Time', 'Voltage']

    return data

def plot_adc_data(data):
    plt.figure(figsize=(10, 6))
    plt.plot(data['Time'], data['Voltage'], label='ADC Data')
    plt.xlabel('time (s)')
    plt.ylabel('voltage (V)')
    plt.title('Biphasic square wave (1 Hz)')
    plt.grid(True)
    plt.savefig('./plots/plot1hz.png')
    plt.show()

file_path = './71524_1Hz.lvm'
adc_data = read_adc_data(file_path)
plot_adc_data(adc_data)
