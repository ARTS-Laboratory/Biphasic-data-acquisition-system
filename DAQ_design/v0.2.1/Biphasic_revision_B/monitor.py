import serial
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# Set up the serial connection.
ser = serial.Serial('/dev/ttyUSB0', 9600)
ser.flush()

# Lists to hold the data.
times = []
drop_voltages = []
sense_voltages = []
resistances = []

num_points = 60  # Number of data points to collect

try:
    for _ in range(num_points):
        # Read a line from the serial port.
        line = ser.readline().decode('utf-8').strip()
        data = line.split(',')

        if len(data) == 5:  # Ensure we have 5 data points before processing.
            # Append data to thier own lists.
            times.append(len(times))
            drop_voltages.append(float(data[1]))
            sense_voltages.append(float(data[3]))
            resistances.append(float(data[4]))

    # Plot drop and sense 
    plt.subplot(2, 1, 1)
    plt.plot(times, drop_voltages, color='blue', label='Drop Voltage')
    plt.plot(times, sense_voltages, color='red', label='Sense Voltage')
    plt.legend(loc='upper right')
    plt.title('Drop and Sense Voltages over Time')
    plt.ylabel('Voltage (V)')

    # Plot resistance
    plt.subplot(2, 1, 2)
    plt.plot(times, resistances, color='green', label='Structure Resistance')
    plt.legend(loc='upper right')
    plt.title('Structure Resistance over Time')
    plt.ylabel('Resistance (Ohms)')
    plt.xlabel('Time (s)')

    plt.tight_layout()  
    plt.show()

finally:
    ser.close()


