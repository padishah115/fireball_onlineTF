from utils.opmanager.operationsmanager import OperationsManager
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from scipy.fft import rfftfreq, rfft

############################
# PROBE OPERATIONS MANAGER #
############################

class ProbeOperationsManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data, cache_path):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)
        self.cache_path = cache_path

    def plot(self, norm:bool=False):
        """Plots the four-channel voltage data from the 'scope readout as a function of time. This will be two 2x2 grids of plots, with each row
        containing the real-space voltage vs. time data in the lefthand column, and the fourier transform of the data in the right column.
        
        Parameters
        ----------
            norm : bool = False
                Whether or not we want to normalize the plot. Currently no method of doing this is implemented in the code.
        """

        # Little modifications required to cater to what the two different scopes are doing
        if self.input["DEVICE_NAME"] == "SCOPE 1":
            ch1_label = "Diamond BLM, 6 dB Attenuation"
            ch2_label = "Upstream BDot Azimuthal Line 1"
            ch3_label = "Upstream BDot Azimuthal Line 2"
            ch4_label = "Downstream BDot Longitudinal Line 1"

        elif self.input["DEVICE_NAME"] == "SCOPE 2":
            ch1_label = "Downstream BDot Longitudinal Line 2"
            ch2_label = "(Unconnected)"
            ch3_label = "Downstream BDot Azimuthal Line 1"
            ch4_label = "Downstream BDot Azimuthal Line 2"

        else:
            raise ValueError(f"Error: unrecognised scope, {self.input['DEVICE_NAME']}")

        channel_nos = ["1", "2", "3", "4"]

        #2x2 grid of plots, figsize is 16x9.
        nrows = 2 
        ncols = 2 if not self.input["PLOT_ONLY"] else 1 #modify figure dimensions if we are not doing fourier transforms
        figsize = (16, 9)

        # TIME information- INCLUDING number of discrete time steps and the interval for each step
        times, N, dt = self._get_time_data()

        # VOLTAGE information
        channel_voltages_dict = {channel_no:self.shot_data["DATA"]["VOLTAGES"][channel_no] for channel_no in channel_nos}

        fig1, axs1 = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        fig2, axs2 = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
        axs_tuple = (axs1, axs2)
        
        ####################
        # CHANNELS 1 AND 2 #
        ####################

        ch_labels = [ch1_label, ch2_label, ch3_label, ch4_label]
        
        for j, axs in enumerate(axs_tuple):
            for i in range(2):

                index = 2*j + i

                index_tuple = (i) if self.input["PLOT_ONLY"] else (i, 0)
                ch_label = ch_labels[index]
                
                # REAL-SPACE VOLTAGE VS TIME PLOT
                channel_no = channel_nos[index]
                
                channel_voltage = channel_voltages_dict[channel_no]
                max_voltage = np.max(channel_voltage)
                min_voltage = np.min(channel_voltage)
                axs[index_tuple].plot(times, channel_voltage)
                
                if self.std_data is not None:
                    sigma_v = self.std_data["DATA"]["VOLTAGES"][channel_no]
                    upper_bound = np.add(channel_voltage, sigma_v)
                    lower_bound = np.subtract(channel_voltage, sigma_v)
                    axs[i, 0].fill_between(times, lower_bound, upper_bound, color='blue', alpha=0.2)
                
                axs[index_tuple].set_ylabel("Amplitude / V")
                axs[index_tuple].set_xlabel("Time / s")
                axs[index_tuple].set_title(f"{ch_label}, Min: {min_voltage:.5f} V, Max: {max_voltage:.5f} V")

                # Only perform fourier transforms if we don't have the input set to plot only
                if not self.input["PLOT_ONLY"]:
                    # FOURIER TRANSFORM
                    freq = rfftfreq(n=N, d=dt)
                    fftvol = np.abs(rfft(channel_voltage))
                    axs[i,1].plot(freq, fftvol)
                    axs[i,1].set_ylabel("Fourier Amplitude")
                    axs[i,1].set_xlabel("Freq / Hz")
                    axs[i,1].set_title(f"Fourier Transform")

        fig1.suptitle(f'Probe Data from {self.input["DEVICE_NAME"]}, Shot {self.shot_no}')
        fig1.tight_layout()
        fig2.tight_layout()
        fig1.canvas.manager.set_window_title(f"{self.DEVICE_NAME}")
        fig2.canvas.manager.set_window_title(f"{self.DEVICE_NAME}")
        plt.show(block=False)

        # Plot the subtracted voltages channels for azimuthal BDot
        if self.input["DEVICE_NAME"] == "SCOPE 1":
            fig3, axs3 = plt.subplots(figsize=(8, 4.5))
            ch2_min_ch3 = np.subtract(channel_voltages_dict["2"], channel_voltages_dict["3"])
            
            if self.std_data is not None:
                sigma_2 = self.std_data["DATA"]["VOLTAGES"]["2"]
                sigma_3 = self.std_data["DATA"]["VOLTAGES"]["3"]
                sigma_comb = np.add(sigma_2, sigma_3)
                upper_ch2_min_ch3 = np.add(ch2_min_ch3, sigma_comb)
                lower_ch2_min_ch3 = np.subtract(ch2_min_ch3, sigma_comb) 
                axs3.fill_between(times, lower_ch2_min_ch3, upper_ch2_min_ch3)
            
            axs3.plot(times, ch2_min_ch3)
            fig3.suptitle("Upstream Azimuthal BDot Difference")
            axs3.set_xlabel("Time / s")
            axs3.set_ylabel("Amplitude / V")
            fig3.tight_layout()
            fig3.canvas.manager.set_window_title(f"Upstream Azimuthal BDot")
            plt.show(block=False)

        if self.input["DEVICE_NAME"] == "SCOPE 2":
            fig3, axs3 = plt.subplots(figsize=(8, 4.5))
            ch3_min_ch4 = np.subtract(channel_voltages_dict["3"], channel_voltages_dict["4"])
            
            if self.std_data is not None:
                sigma_3 = self.std_data["DATA"]["VOLTAGES"]["3"]
                sigma_4 = self.std_data["DATA"]["VOLTAGES"]["4"]
                sigma_comb = np.add(sigma_3, sigma_4)
                upper_ch3_min_ch4 = np.add(ch3_min_ch4, sigma_comb)
                lower_ch3_min_ch4 = np.subtract(ch3_min_ch4, sigma_comb) 
                axs3.fill_between(times, lower_ch3_min_ch4, upper_ch3_min_ch4)
            
            axs3.set_xlabel("Time / s")
            axs3.set_ylabel("Amplitude / V")
            axs3.plot(times, ch3_min_ch4)
            fig3.suptitle("Downstream Azimuthal BDot Difference")
            fig3.tight_layout()
            fig3.canvas.manager.set_window_title(f"Downstream Azimuthal BDot")
            plt.show(block=False)


        longitudinal_cache_fpath = os.path.join(self.cache_path, str(self.shot_no) + ".csv")
        #LONGITUDINAL BDOT- need to cache the data for the different scope's info about the BDots in the longitudinal direction.
        if self.input["DEVICE_NAME"] == "SCOPE 1":
            downstream_longitudinal_bdot = self.shot_data["DATA"]["VOLTAGES"]["4"]

            if os.path.exists(longitudinal_cache_fpath):
                df = pd.read_csv(longitudinal_cache_fpath)
                df["DOWNSTREAM"] = downstream_longitudinal_bdot

                longitudinal_difference = np.subtract(df["UPSTREAM"], df["DOWNSTREAM"])


                fig4, axs4 = plt.subplots()
                if self.std_data is not None:
                    df["DOWNSTREAM STD"] = self.std_data["DATA"]["VOLTAGES"]["4"]
                    sigma = np.add(df["DOWNSTREAM STD"], df["UPSTREAM STD"])
                    upper_bound = np.add(longitudinal_difference, sigma)
                    lower_bound = np.subtract(longitudinal_difference, sigma)

                axs4.fill_between(times, lower_bound, upper_bound)
                axs4.plot(times, longitudinal_difference)
                axs4.set_ylabel("Amplitude / V")
                axs4.set_xlabel("Time / s")

                fig4.suptitle("Longitudinal BDot Difference")
                fig4.tight_layout()
                fig4.canvas.manager.set_window_title(f"Longitudinal BDot Difference")
                plt.show(block=False)

            else:
                long_dict = {"DOWNSTREAM":downstream_longitudinal_bdot}
                if self.std_data is not None:
                    long_dict["DOWNSTREAM STD"] = self.std_data["DATA"]["VOLTAGES"]["4"]


                df = pd.DataFrame(long_dict)
                df.to_csv(longitudinal_cache_fpath)


        if self.input["DEVICE_NAME"] == "SCOPE 2":
            upstream_longitudinal_bdot = self.shot_data["DATA"]["VOLTAGES"]["1"]

            if os.path.exists(longitudinal_cache_fpath):
                df = pd.read_csv(longitudinal_cache_fpath)
                df["UPSTREAM"] = upstream_longitudinal_bdot
                
                longitudinal_difference = np.subtract(df["UPSTREAM"], df["DOWNSTREAM"])

                fig4, axs4 = plt.subplots()

                if self.std_data is not None:
                    df["UPSTREAM STD"] = self.std_data["DATA"]["VOLTAGES"]["1"]
                    sigma = np.add(df["DOWNSTREAM STD"], df["UPSTREAM STD"])
                    upper_bound = np.add(longitudinal_difference, sigma)
                    lower_bound = np.subtract(longitudinal_difference, sigma)
                    axs4.fill_between(times, lower_bound, upper_bound)
                
                
                axs4.plot(times, longitudinal_difference)
                axs4.set_ylabel("Amplitude / V")
                axs4.set_xlabel("Time / s")

                fig4.suptitle("Longitudinal BDot Difference")
                fig4.tight_layout()
                fig4.canvas.manager.set_window_title(f"Longitudinal BDot difference")
                plt.show(block=False)

            
            else:
                long_dict = {"UPSTREAM":upstream_longitudinal_bdot}
                if self.std_data is not None:
                    long_dict["UPSTREAM STD"] = self.std_data["DATA"]["VOLTAGES"]["1"]

                df = pd.DataFrame(long_dict)
                df.to_csv(longitudinal_cache_fpath)


    
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


        

