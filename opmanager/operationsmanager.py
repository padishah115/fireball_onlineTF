import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Tuple
from scipy.fft import rfft, rfftfreq
#from stats import arrays_stats

#################################
# OPERATIONS MANAGER BASE CLASS #
#################################

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
    
    def average_shots(self, data_list):
        raise NotImplementedError(f"Warning: no averaging method implemented for {self}")
    
    def chromox_fit(self):
        raise NotImplementedError(f"Warning: no chromox_fit method implemented for {self}")
