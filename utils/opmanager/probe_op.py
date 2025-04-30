from utils.opmanager.operationsmanager import OperationsManager
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Tuple
from scipy.fft import rfftfreq, rfft

############################
# PROBE OPERATIONS MANAGER #
############################

class ProbeManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)

    def plot(self, norm:bool=False):
        fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(16,9))

        # time information
        times = self.shot_data["DATA"]["TIMES"]["TIMES"]
        N = self.shot_data["DATA"]["TIMES"]["N"]
        dt = self.shot_data["DATA"]["TIMES"]["dt"]

        # voltage information
        channel1_voltages = self.shot_data["DATA"]["VOLTAGES"]["1"]
        channel2_voltages = self.shot_data["DATA"]["VOLTAGES"]["2"]
        corr_voltages = np.subtract(channel1_voltages, channel2_voltages)

        #############
        # CHANNEL 1 #
        #############

        axs[0, 0].plot(times, channel1_voltages)
        axs[0, 0].set_ylabel("Amplitude / V")
        axs[0, 0].set_xlabel("Time / s")
        axs[0, 0].set_title("Ch 1")

        freq1 = rfftfreq(n=N-1, d=dt)
        fftvol1 = np.abs(rfft(channel1_voltages))
        axs[0,1].plot(freq1, fftvol1)
        axs[0,1].set_ylabel("Fourier Amplitude")
        axs[0,1].set_xlabel("Freq / Hz")
        axs[0,1].set_title("Ch 1 Fourier Transform")

        #############
        # CHANNEL 2 #
        #############

        axs[1,0].plot(times, channel2_voltages)
        axs[1,0].set_xlabel("Time / s")
        axs[1,0].set_ylabel("Amplitude / V")
        axs[1,0].set_title("Ch 2")

        freq2 = rfftfreq(n=N-1, d=dt)
        fftvol2 = np.abs(rfft(channel2_voltages))
        axs[1,1].plot(freq2, fftvol2)
        axs[1,1].set_ylabel("Fourier Amplitude")
        axs[1,1].set_xlabel("Freq / Hz")
        axs[1,1].set_title("Ch2 Fourier Transform")

        #############
        # CORRECTED #
        #############

        axs[2,0].plot(times, corr_voltages)
        axs[2,0].set_xlabel("Time / s")
        axs[2,0].set_ylabel("Amplitude / V")
        axs[2,0].set_title("deltaV Between Channels")

        freq_corr = rfftfreq(n=N-1, d=dt)
        fftvolcorr = np.abs(rfft(corr_voltages))
        axs[2,1].plot(freq_corr, fftvolcorr)
        axs[2,1].set_ylabel("Fourier Amplitude")
        axs[2,1].set_xlabel("Freq / Hz")
        axs[2,1].set_title("deltaV Signal Fourier Transform")

        fig.suptitle("Data from Scope")
        fig.tight_layout()
        plt.show()

