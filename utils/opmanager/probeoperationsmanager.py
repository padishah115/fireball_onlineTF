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

        channel_nos = ["1", "2", "3", "4"]

        #2x2 grid of plots, figsize is 16x9.
        nrows = 2
        ncols = 2
        figsize = (16, 9)

        # TIME information- INCLUDING number of discrete time steps and the interval for each step
        times, N, dt = self._get_time_data()

        # VOLTAGE information
        channel_voltages_dict = {channel_no:self.shot_data["DATA"]["VOLTAGES"][channel_no] for channel_no in channel_nos}
        
        ####################
        # CHANNELS 1 AND 2 #
        ####################
        fig1, axs1 = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        for i in range(2):

            # REAL-SPACE VOLTAGE VS TIME PLOT
            channel_no = channel_nos[i]
            channel_voltage = channel_voltages_dict[channel_no]
            axs1[i, 0].plot(times, channel_voltage)
            if self.std_data is not None:
                sigma_v = self.std_data["DATA"]["VOLTAGES"][channel_no]
                upper_bound = np.add(channel_voltage, sigma_v)
                lower_bound = np.subtract(channel_voltage, sigma_v)
                axs1[i, 0].fill_between(times, lower_bound, upper_bound, color='blue', alpha=0.2)
            axs1[i, 0].set_ylabel("Amplitude / V")
            axs1[i, 0].set_xlabel("Time / s")
            axs1[i, 0].set_title(f"Ch {channel_no}")
            
            # FOURIER TRANSFORM
            freq = rfftfreq(n=N, d=dt)
            fftvol = np.abs(rfft(channel_voltage))
            axs1[i,1].plot(freq, fftvol)
            axs1[i,1].set_ylabel("Fourier Amplitude")
            axs1[i,1].set_xlabel("Freq / Hz")
            axs1[i,1].set_title(f"Ch {channel_no} Fourier Transform")

        ####################
        # CHANNELS 3 AND 4 #
        ####################
        fig2, axs2 = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        for i in range(2):
            channel_no = channel_nos[i+2]
            channel_voltage = channel_voltages_dict[channel_no]

            axs2[i, 0].plot(times, channel_voltage)
            if self.std_data is not None:
                sigma_v = self.std_data["DATA"]["VOLTAGES"]["1"]
                upper_bound = np.add(channel_voltage, sigma_v)
                lower_bound = np.subtract(channel_voltage, sigma_v)
                axs2[i, 0].fill_between(times, lower_bound, upper_bound, color='blue', alpha=0.2)
            axs2[i, 0].set_ylabel("Amplitude / V")
            axs2[i, 0].set_xlabel("Time / s")
            axs2[i, 0].set_title(f"Ch {channel_no}")
            freq = rfftfreq(n=N, d=dt)
            fftvol = np.abs(rfft(channel_voltage))
            axs2[i,1].plot(freq, fftvol)
            axs2[i,1].set_ylabel("Fourier Amplitude")
            axs2[i,1].set_xlabel("Freq / Hz")
            axs2[i,1].set_title(f"Ch {channel_no} Fourier Transform")

        
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


        

