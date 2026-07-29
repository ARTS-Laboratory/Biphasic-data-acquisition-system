# code
* Codes for Assisi V0.2.0
* Using LabView 2025

## firmware
* This is the code for the microcontroller to control biphasic pulsing.
* This code runs on Arduino.

## data_processing_offline
* Two data aquisition options:
    - labview_daq: LabView 2025 code collects data (voltage) and saves it to a LVM file.
    - python_daq: Python code collects data (voltage) and saves it to a LVM file.
* Python code reads LVM file and returns a CSV file of the resistance over time.
* Experimental data folders are labeled in MM/DD/YYYY format.

## data_processing_online
* LabView code collects data (voltage) and converts to resistance data in the program before saving it as a LVM file.
* In this code, the intermediate voltage signal is never saved.