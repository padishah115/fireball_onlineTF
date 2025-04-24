import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict
from scipy.fft import fft
from stats import arrays_stats

class OperationsManager:
    """Class responsible for performing more advanced analysis and arithmetic on the shot data, including
    but not limited to fourier transforms and lineout calculations."""

    def __init__(self, DEVICE_NAME, shot_no, label, shot_data:np.ndarray):
        """
        Parameters
        ----------
            DEVICE_NAME : str
                The name of the device (e.g. "Synchro" etc.), which is used only for producing labelled plotting
                information.
            shot_no : int
                The shot number corresponding to the data on which the operations are being performed. This
                is used again for clarity in the plot labels.
            label : str
                Additional information, provided by user, about the shot.
            shot_data : np.ndarray
                The shot data, array form, on which we want to perform some specified
                operations
        """

        # INITIALIZE INFORMATION WHICH WE BE USEFUL FOR DISPLAYING THE DATA TO THE USER.
        self.DEVICE_NAME = DEVICE_NAME
        self.shot_no = shot_no
        self.label = label

        # THE RAW DATA ITSELF IN NP.NDARRAY FORMAT
        self.shot_data = shot_data

    def plot(self):
        raise NotImplementedError(f"Warning: no plotting method implemented for {self}")
    
    def average_shots(self, arrays):
        raise NotImplementedError(f"Warning: no averaging method implemented for {self}")

    def lineouts(self, axis:int, ft_interp:str):
        """Computes the lineout of the data, and plots."""
        if axis + axis == axis:
            pixels_1D = np.arange(0, self.shot_data.shape[1], 1)
        else:
            pixels_1D = np.arange(0, self.shot_data.shape[0], 1)
        
        lineout = np.sum(self.shot_data, axis=axis)
        lineout_fft_y = fft(lineout)
        lineout_fft_x = fft(pixels_1D)


        fig, axs = plt.subplots(nrows=1, ncols=2)

        #real-space plot
        axs[0].plot(pixels_1D, lineout)
        axs[0].set_title("Real Domain")
        
        #fourier-space plot
        axs[1].plot(lineout_fft_x, lineout_fft_y)
        axs[1].set_title(f"Fourier Domain \n {ft_interp}")
        
        fig.suptitle(f"Axis {axis} Lineout from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        plt.show()
        
    

# IMAGE MANAGER

class ImageManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)

    def plot(self):
        plt.imshow(self.shot_data)
        plt.title(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        plt.show()

    def average_shots(self, data_list:List[np.ndarray]):
        
        array_stack = data_list[0]

        for array in data_list[1:]:
            array_stack = np.stack([array_stack, array], axis=0)
        
        sum_arr = np.sum(array_stack, axis=0)

        mean_arr = np.multiply(sum_arr, 1/len(data_list))

        plt.imshow(mean_arr)
        plt.title(f"Averaged Image over TKTK Shots")
        plt.show()
        

# PROBE MANAGER

class ProbeManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)

    def plot(self):
        time = self.shot_data["TIMES"]
        voltages = self.shot_data["VOLTAGES"]

        fft_time = fft(time)
        fft_voltages = fft(voltages)

        fig, axs = plt.subplots(nrows=1, ncols=2)


        axs[0].plot(time, voltages)
        axs[0].set_ylabel("Voltage")
        axs[0].set_xlabel("Time")
        axs[0].set_title("Real Domain")

        axs[1].plot(fft_time, fft_voltages)
        axs[1].set_ylabel("Amplitude")
        axs[1].set_xlabel("Frequency")
        axs[1].set_title("Fourier Domain")

        fig.suptitle(f"Oscilloscope Trace from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        plt.show()

    def average_shots(self, data_list):
        
        pass
