import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np

directory = "./biphtestdata"

filenames = ["1Hz.txt", "2Hz.txt", "5Hz.txt", "20Hz.txt", "50Hz.txt"]

plt.figure(figsize=(5,5))

for file in filenames:
    file_path = os.path.join(directory, file)
    data = pd.read_csv(file_path)
    data['time'] = pd.to_numeric(data['time'], errors='coerce')
    data_filtered = data[data["time"] <= 100000]

    # Further filter data to exclude resistance values outside 83.0 to 86.0 ohms
    data_filtered = data_filtered[(data_filtered["Structure Resistance (ohms)"] >= 84.0) & 
                                  (data_filtered["Structure Resistance (ohms)"] <= 86.0)]

    time = data_filtered["time"]
    resistance = data_filtered["Structure Resistance (ohms)"]

    plt.plot(time, resistance, label=f"{file.split('.')[0]} Hz")

# Set specific y-axis bounds and tick marks
plt.ylim(84.0, 85.75)
plt.yticks(np.arange(84.0, 85.75, 0.1))

plt.xlabel("time (ms)")
plt.ylabel("resistance (ohms)")
plt.title("Four Probe Differential, 5Vin, 100-Ohm known")
plt.legend()
plt.grid(True)
plt.show()


