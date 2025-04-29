from opmanager.operationsmanager import OperationsManager
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Tuple
from scipy.fft import rfftfreq, rfft

############################
# PROBE OPERATIONS MANAGER #
############################

class ProbeManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)

    def plot(self):
        time = self.shot_data["DATA"]["TIMES"]
        voltages = self.shot_data["DATA"]["VOLTAGES"]

        #Calculate number of bin centres, and the time spacing of the 'scope
        N = len(voltages)
        dt = time[1]-time[0]

        # FREQ AND INTENSITY
        fft_time = rfftfreq(N, d=dt)
        fft_voltages = np.abs(rfft(voltages))

        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16,9))

        # REAL DOMAIN
        axs[0].plot(time, voltages)
        axs[0].set_ylabel("Voltage / V")
        axs[0].set_xlabel("Time / s")
        axs[0].set_title("Real Domain")

        #FREQUENCY DOMAIN
        axs[1].plot(fft_time, fft_voltages)
        axs[1].set_ylabel("Amplitude")
        axs[1].set_xlabel("Frequency / Hz")
        axs[1].set_title("Fourier Domain")

        fig.suptitle(f"Oscilloscope Trace from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        plt.show()

    def average_shots(self, shot_data_list, shot_nos):
        
        times = shot_data_list[0]["DATA"]["TIMES"]
        voltage_stack = shot_data_list[0]["DATA"]["VOLTAGES"]

        for data in shot_data_list[1:]:
            voltage_stack = np.stack([voltage_stack, data["VOLTAGES"]], axis=0)

        voltage_sum = np.sum(voltage_stack, axis=0)
        voltage_avg = np.multiply(voltage_sum, 1/len(shot_data_list))

        plt.plot(times, voltage_avg)
        plt.title(f"Oscilloscope Averaged Over Shots {shot_nos}")
        plt.show()