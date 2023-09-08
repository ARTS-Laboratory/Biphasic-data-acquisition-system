import serial
import matplotlib.pyplot as plt
from time import sleep

# Set up the serial connection.
# Replace 'COM3' with your Arduino's COM port and adjust the baud rate if necessary.
ser = serial.Serial('/dev/ttyS0', 9600)
ser.flush()

# Lists to hold the data.
times = []
drop_voltages = []
sense_voltages = []
resistances = []

try:
    while True:
        # Read a line from the serial port.
        line = ser.readline().decode('utf-8').strip()
        data = line.split(',')

        if len(data) == 5:  # Ensure we have 5 data points before processing.
            # Append data to lists.
            times.append(len(times))
            drop_voltages.append(float(data[1]))
            sense_voltages.append(float(data[3]))
            resistances.append(float(data[4]))

            # Clear the previous plots.
            plt.clf()

            # Plot drop voltages.
            plt.subplot(3, 1, 1)
            plt.plot(times, drop_voltages, label='Drop Voltage')
            plt.legend(loc='upper right')
            plt.title('Drop Voltage over Time')
            plt.ylabel('Voltage (V)')

            # Plot sense voltages.
            plt.subplot(3, 1, 2)
            plt.plot(times, sense_voltages, label='Sense Voltage')
            plt.legend(loc='upper right')
            plt.title('Sense Voltage over Time')
            plt.ylabel('Voltage (V)')

            # Plot resistances.
            plt.subplot(3, 1, 3)
            plt.plot(times, resistances, label='Structure Resistance')
            plt.legend(loc='upper right')
            plt.title('Structure Resistance over Time')
            plt.ylabel('Resistance (Ohms)')
            plt.xlabel('Time (s)')

            # Update the plots.
            plt.pause(0.05)

except KeyboardInterrupt:
    # Close the serial connection upon exiting.
    ser.close()
    plt.show()
