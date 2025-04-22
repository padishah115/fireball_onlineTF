# MODULE IMPORTS
import numpy as np
import pandas as pd

#####################
# SHOT PARENT CLASS #
#####################

class Shot:
    """
    
    Attributes
    ----------
        device_name : str
            Name of the parent device for which the shot has been taken
        shot_key : str
            The key or 'label' telling us what exactly the shot is. E.g. "1" or "DARKFIELD"
        raw_data : device_dependent
            The shot's raw data. This could be voltage vs time, or could be an NDarray encoding image data.

    Methods
    -------
        raw()
            Performs raw data extraction for the shot.
    """

    def __init__(self, device_name:str, shot_key:str, shot_data_path:str):
        """
        
        Parameters
        ----------
            device_name : str
                The name of the device on which the shot was taken.
            shot_key : str
                The key or 'label' telling us what exactly the shot is. E.g. "1" or "DARKFIELD"
            shot_data_path : str
                Path to the data for the shot in question- this could be a .csv file containing
                time against voltage, or be an image, etc.
            
        """

        # FOR EASE OF LABELLING, TELLS US WHAT THE NAME OF THE DEVICE IS
        self.device_name = device_name

        # INITIALIZE THE SHOT'S KEY SO THAT WE KNOW HOW TO LABEL THE SHOW
        self.shot_key = shot_key

        # INITIALIZE THE PATH TO THE SHOT'S DATA
        self.shot_data_path = shot_data_path

        # GET THE RAW DATA FOR THE SHOT
        self.raw_data = self.raw()

    def __repr__(self,):
        return f"SHOT NO. : {self.shot_key} | DEVICE: {self.device_name}"
    
    def raw():
        """Returns raw data for the shot"""
        raise NotImplementedError(f"Error: no raw() function implemented for shot")


##########################
# IMAGE SHOT CHILD CLASS #
##########################

class ImageShot(Shot):
    
    def __init__(self, device_name, shot_key, shot_data_path):
        super().__init__(device_name, shot_key, shot_data_path)

    def raw(self)->np.ndarray:
        """Generates the raw image array from a .csv and returns it.
        
        Returns
        -------
            raw_image_array : np.ndarray
                The raw image array generated for the camera
        """
        
        if not self.shot_data_path.endswith('.npy'):
            raise ValueError(f"Warning: expected .csv file for \
                             shot {self.shot_key} on {self.device_name}, but \
                             didn't get one.")

        # GENERATE IMAGE ARRAY FROM .CSV FILE
        raw_image_array = np.genfromtxt(self.shot_data_path)

        return raw_image_array


############################
# VOLTAGE SHOT CHILD CLASS #
############################

class VoltShot(Shot):
    
    def __init__(self, device_name, shot_key, shot_data_path):
        super().__init__(device_name, shot_key, shot_data_path)

    
    def raw(self):
        """Generates time and voltage data from .csv file of oscilloscope data.
        
        Returns
        -------
            scope_dict : Dict
        """

        # OPEN THE .CSV CONTAINING VOLTAGE AND TIME INFORMATION FROM THE
        # OSCILLOSCOPE
        v_and_t_csv = pd.read_csv(self.shot_data_path)

        

