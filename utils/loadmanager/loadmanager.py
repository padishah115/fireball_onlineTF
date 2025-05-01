from typing import List, Dict, Tuple
import numpy as np
import pandas as pd

from utils.stats.stats import img_arrays_stats

class LoadManager:
    """Class responsible for loading data for specified shots at runtime. This is responsible,
    in the main function, for producing dictionaries of experimental shot data, background shot data, and
    background-corrected shot data."""

    def __init__(self, 
                 input:Dict,
                 data_paths_dict:Dict[int, str]):
        """
        Parameters
        ----------
            input : Dict
                The Python dictionary which has been generated via loading the input.json file.
            data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT NO : /path/to/shot/data} keeping track of where the data for each shot number
                is stored.
        """
        
        # INITIALIZE INPUT DICTIONARY
        self.input = input

        # INITIALIZE DEVICE TYPE SO THAT WE KNOW WHETHER WE ARE LOADING _PROBE_ DATA OR _IMAGE_ DATA.
        self.device_type = self.input["DEVICE_TYPE"]

        # LIST OF EXPERIMENTAL (I.E. NON-BACKGROUND) SHOTS WHOSE DATA WE ARE PROCESSING
        self.exp_shot_nos = self.input["EXP_SHOT_NOS"]

        # LIST OF BACKGROUND SHOT NUMBERS - THESE ARE SHOTS OVER WHOM WE WANT TO TAKE AN AVERAGE
        # BEFORE SUBTRACTION
        self.bkg_shot_nos = self.input["BKG_SHOT_NOS"]
        
        # DICTIONARY KEYED BY SHOT NUMBER, WITH VALUES CORRESPONDING TO THE PATHS TO THE DATA
        # FOR BOTH BACKGROUND AND EXPERIMENTAL SHOTS
        self.data_paths_dict = data_paths_dict

        #SEE WHETHER WE WANT TO NORMALIZE THE DATA
        self.norm = self.input["NORM_PLOT"]
        

    def load(self)->Tuple[Dict[int, np.ndarray], Dict[int, np.ndarray], Dict[int, np.ndarray]]:
        """Loads dictionaries of indexed experimental, background, and background-corrected data. Each of these
        three dictionaries returned by the function is of the form {SHOT NO : np.ndarray}, where the
        np.ndarray is the data itself."""
        raise NotImplementedError(f"Error: no load method implemented for {self}.")
    



    