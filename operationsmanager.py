import numpy as np
import matplotlib.pyplot as plt
from typing import List
from scipy.fft import fft, fft2

class OperationsManager:

    def __init__(self, DEVICE_NAME, shot_no, label, shot_data:np.ndarray, operations:List[str]):
        """
        Parameters
        ----------
            DEVICE_NAME
            shot_no
            label
            shot_data : np.ndarray
                The shot data, array form, on which we want to perform some specified
                operations
            operations : List[str]
                List of operations which we would like to perform on the shot
        """

        self.DEVICE_NAME = DEVICE_NAME
        self.shot_no = shot_no
        self.label = label
        self.shot_data = shot_data
        self.operations = operations

    def run(self):
        
        if "FFT" in self.operations:
            self.fft(self.shot_data)

        if "PLOT" in self.operations:
            self._plot(self.shot_data)

        if "LINEOUTS" in self.operations:
            self._line

    def _plot(self, data):
        pass

    def lineouts(self, axis, plot=False):
        """Computes the lineout of the data, and plots if required."""
        if axis + axis == axis:
            pixels_1D = np.arange(0, self.shot_data.shape[1], 1)
        else:
            pixels_1D = np.arange(0, self.shot_data.shape[0], 1)
        
        lineout = np.sum(self.shot_data, axis=axis)

        if plot:
            plt.plot(pixels_1D, lineout)
            plt.title(f"Axis {axis} Lineout from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
            plt.show()
        
        return lineout, pixels_1D
    
    def FFT(self):
        
        fft_dict = {
            1:fft,
            2:fft2
        }
        
        return fft_dict[len(self.shot_data.shape)](self.shot_data)
