from utils.opmanager.operationsmanager import OperationsManager
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Tuple
from scipy.fft import rfftfreq, rfft

############################
# PROBE OPERATIONS MANAGER #
############################

class ProbeOperationsManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)

    def plot(self, norm:bool=False):
        """Plots the four-channel voltage data from the 'scope readout as a function of time."""

        ########################
        # CHANNELS ONE AND TWO #
        ########################

        fig1, axs1 = plt.subplots(nrows=2, ncols=2, figsize=(16,9))

        # time information- INCLUDING number of discrete time steps and the interval for each step
        times = self.shot_data["DATA"]["TIMES"]["TIMES"]
        N = self.shot_data["DATA"]["TIMES"]["N"]
        dt = self.shot_data["DATA"]["TIMES"]["dt"]

        # voltage information
        channel1_voltages = self.shot_data["DATA"]["VOLTAGES"]["1"]
        channel2_voltages = self.shot_data["DATA"]["VOLTAGES"]["2"]
        
        # CHANNEL 1 #

        axs1[0, 0].plot(times, channel1_voltages)
        axs1[0, 0].set_ylabel("Amplitude / V")
        axs1[0, 0].set_xlabel("Time / s")
        axs1[0, 0].set_title("Ch 1")

        freq1 = rfftfreq(n=N-1, d=dt)
        fftvol1 = np.abs(rfft(channel1_voltages))
        axs1[0,1].plot(freq1, fftvol1)
        axs1[0,1].set_ylabel("Fourier Amplitude")
        axs1[0,1].set_xlabel("Freq / Hz")
        axs1[0,1].set_title("Ch 1 Fourier Transform")

        # CHANNEL 2 #

        axs1[1,0].plot(times, channel2_voltages)
        axs1[1,0].set_xlabel("Time / s")
        axs1[1,0].set_ylabel("Amplitude / V")
        axs1[1,0].set_title("Ch 2")

        freq2 = rfftfreq(n=N-1, d=dt)
        fftvol2 = np.abs(rfft(channel2_voltages))
        axs1[1,1].plot(freq2, fftvol2)
        axs1[1,1].set_ylabel("Fourier Amplitude")
        axs1[1,1].set_xlabel("Freq / Hz")
        axs1[1,1].set_title("Ch2 Fourier Transform")

        fig1.suptitle("Data from Scope")
        fig1.tight_layout()
        plt.show()

        #############
        # CHANNELS 3 AND 4 #
        #############

        fig2, axs2 = plt.subplots(nrows=2, ncols=2, figsize=(16,9))

        # voltage information
        channel3_voltages = self.shot_data["DATA"]["VOLTAGES"]["3"]
        channel2_voltages = self.shot_data["DATA"]["VOLTAGES"]["3"]
        
        # CHANNEL 1 #

        axs2[0, 0].plot(times, channel1_voltages)
        axs2[0, 0].set_ylabel("Amplitude / V")
        axs2[0, 0].set_xlabel("Time / s")
        axs2[0, 0].set_title("Ch 1")

        freq3 = rfftfreq(n=N-1, d=dt)
        fftvol3 = np.abs(rfft(channel1_voltages))
        axs2[0,1].plot(freq1, fftvol1)
        axs2[0,1].set_ylabel("Fourier Amplitude")
        axs2[0,1].set_xlabel("Freq / Hz")
        axs2[0,1].set_title("Ch 1 Fourier Transform")

        # CHANNEL 2 #

        axs2[1,0].plot(times, channel2_voltages)
        axs2[1,0].set_xlabel("Time / s")
        axs2[1,0].set_ylabel("Amplitude / V")
        axs2[1,0].set_title("Ch 2")

        freq4 = rfftfreq(n=N-1, d=dt)
        fftvol4 = np.abs(rfft(channel2_voltages))
        axs2[1,1].plot(freq2, fftvol2)
        axs2[1,1].set_ylabel("Fourier Amplitude")
        axs2[1,1].set_xlabel("Freq / Hz")
        axs2[1,1].set_title("Ch2 Fourier Transform")

        fig2.suptitle("Data from Scope")
        fig2.tight_layout()
        plt.show()


        

