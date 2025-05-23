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
        """Plots the four-channel voltage data from the 'scope readout as a function of time. This will be two 2x2 grids of plots, with each row
        containing the real-space voltage vs. time data in the lefthand column, and the fourier transform of the data in the right column.
        
        Parameters
        ----------
            norm : bool = False
                Whether or not we want to normalize the 
        """

        #2x2 grid of plots, figsize is 16x9.
        nrows = 2
        ncols = 2
        figsize = (16, 9)

        ########################
        # CHANNELS ONE AND TWO #
        ########################

        fig1, axs1 = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)

        # TIME information- INCLUDING number of discrete time steps and the interval for each step
        times, N, dt = self._get_time_data()

        # VOLTAGE information
        channel1_voltages = self.shot_data["DATA"]["VOLTAGES"]["1"]
        channel2_voltages = self.shot_data["DATA"]["VOLTAGES"]["2"]
        channel3_voltages = self.shot_data["DATA"]["VOLTAGES"]["3"]
        channel4_voltages = self.shot_data["DATA"]["VOLTAGES"]["4"]
        
        # CHANNEL 1 #

        axs1[0, 0].plot(times, channel1_voltages)
        axs1[0, 0].set_ylabel("Amplitude / V")
        axs1[0, 0].set_xlabel("Time / s")
        axs1[0, 0].set_title("Ch 1")

        freq1 = rfftfreq(n=N, d=dt)
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

        freq2 = rfftfreq(n=N, d=dt)
        fftvol2 = np.abs(rfft(channel2_voltages))
        axs1[1,1].plot(freq2, fftvol2)
        axs1[1,1].set_ylabel("Fourier Amplitude")
        axs1[1,1].set_xlabel("Freq / Hz")
        axs1[1,1].set_title("Ch2 Fourier Transform")

        fig1.suptitle(f'Data from {self.input["DEVICE_NAME"]}, Shot {self.shot_no}')
        fig1.tight_layout()
        plt.show()

        #############
        # CHANNELS 3 AND 4 #
        #############

        fig2, axs2 = plt.subplots(nrows=2, ncols=2, figsize=(16,9))
        
        # CHANNEL 3 #

        axs2[0, 0].plot(times, channel3_voltages)
        axs2[0, 0].set_ylabel("Amplitude / V")
        axs2[0, 0].set_xlabel("Time / s")
        axs2[0, 0].set_title("Ch 3")

        freq3 = rfftfreq(n=N, d=dt)
        fftvol3 = np.abs(rfft(channel3_voltages))
        axs2[0,1].plot(freq3, fftvol3)
        axs2[0,1].set_ylabel("Fourier Amplitude")
        axs2[0,1].set_xlabel("Freq / Hz")
        axs2[0,1].set_title("Ch 3 Fourier Transform")

        # CHANNEL 4 #

        axs2[1,0].plot(times, channel4_voltages)
        axs2[1,0].set_xlabel("Time / s")
        axs2[1,0].set_ylabel("Amplitude / V")
        axs2[1,0].set_title("Ch 4")

        freq4 = rfftfreq(n=N, d=dt)
        fftvol4 = np.abs(rfft(channel4_voltages))
        axs2[1,1].plot(freq4, fftvol4)
        axs2[1,1].set_ylabel("Fourier Amplitude")
        axs2[1,1].set_xlabel("Freq / Hz")
        axs2[1,1].set_title("Ch4 Fourier Transform")

        fig2.suptitle(f'Data from {self.input["DEVICE_NAME"]}, Shot {self.shot_no}')
        fig2.tight_layout()
        plt.show()

    
    def _get_time_data(self)->tuple[np.ndarray, int, float]:
        """Returns time data (timestamps, number of samples, time interval between samples) from shot data.
        
        Returns
        -------
            times : np.ndarray
                The timestamps of the data (i.e. the points that will be along the "time" axis) from the scope trace.
            N : int
                The number of samples over which data from the 'scopes was taken.
            dt : float
                The size of the timesteps (intervals between samples), in seconds.
        """

        times = self.shot_data["DATA"]["TIMES"]["TIMES"]
        N = self.shot_data["DATA"]["TIMES"]["N"]
        dt = self.shot_data["DATA"]["TIMES"]["dt"]

        return times, N, dt
    
    
    def _get_voltage_data(self, channel_no:str)->np.ndarray:
        """Returns voltage data for a given channel on the 'scope. The time data will of course be in array form.
        
        Parameters
        ----------
            channel_no : str
                The channel number for which we want voltage data. This should be in STRING format.

        Returns
        -------
            channel_voltages : np.ndarray
                The voltage information for the channel, in array format.
        """

        # Check to make sure that the channel number is passed as a string.
        if type(channel_no) != str:
            raise TypeError("Error: channel number must be passed as a string.")

        # Check to make sure that the provided channel number is between 1 and 4.
        if channel_no not in ["1", "2", "3", "4"]:
            raise ValueError("Error: channel number provided is not between 1 and 4.")

        channel_voltages = self.shot_data["DATA"]["VOLTAGES"][channel_no]

        return channel_voltages


        

