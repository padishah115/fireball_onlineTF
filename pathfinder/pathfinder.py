######################################################################################################
# SCRIPT WHICH BUILDS DICTIONARIES OF DATA PATHS FOR SHOTS. IDEA IS THAT THIS TAKES SOME INPUT .CSV, #
#  EITHER ONE PER INSTRUMENT OR FROM ONE MASTER.CSV, AND THEN CONVERTS TO SOME DICTIONARY FORMAT     #
#  APPROPRIATE FOR USE IN THE MAIN CODE.                                                             #
######################################################################################################

# !!!!!!!!!! THIS SHOULD BE THE ONLY FILE IN THE PROJECT WITH HARD-CODED VALUES, WHICH ARE THE PATHS TO THE .CSV FILES !!!!!!!!

# MODULE IMPORTS
import pandas as pd
import numpy as np
from typing import List, Dict

class PathFinder:
    """Class responsible for scraping .csv files which contain information about the storage location of data for all equipment across all shots."""

    def __init__(self, RAW_timestamp_csv_path:str, BKG_timestamp_csv_path:str, device_name:str, shot_key:str):
        """
        Parameters
        ----------
            RAW_timestamp_csv_path : str
                Path to the .csv file containing information about where all raw data has been stored for each shot.

            BKG_timestamp_csv_path : str
                Path to the .csv file containing information about where the background data has been stored for the diagnostic.
            
            device_name : str
                Name of device whose data we are interested in. The PathFinder class' mission is to produce a dictionary containing paths to all shot data for all shots
                for this device.
            
            shot_key : str
                The spelling/format of the header denoting shot number in the .csv-> i.e. is is "shot Number", "Shot Number", or "shOt nUmBeR" etc.

        """

        # OBJECT'S CSV PATH. I'VE SHORTENED THIS FOR CLARITY, AND BY THIS POINT THERE
        #  SHOULD BE NO AMBIGUITY ABOUT WHICH .CSV THIS IS.
        self.raw_csv_path = RAW_timestamp_csv_path
        self.bkg_csv_path = BKG_timestamp_csv_path

        # DEVICE NAME SO THAT WE READ FROM THE CORRECT COLUMN IN THE .CSV
        self.device_name = device_name

        # OPEN THE CSV AND GET THE DATA AS A PANDA DATAFRAMES
        self.raw_df = pd.read_csv(self.raw_csv_path, delimiter=",")
        self.background_df = pd.read_csv(self.bkg_csv_path, delimiter=",")

        #Initialise shot key
        self.shot_key = shot_key

        # EMPTY DATA PATHS MATRIX WHICH WE WILL BUILD UP BY USING THE .CSV FILE
        self.RAW_data_paths_dict = {}
        self.BKG_data_paths_dict = {}

    def _find_shots(self):
        """Scrape through the specified .csv looking to see which shots actually happened."""

        # GET THE COLUMN OF THE .CSV INDEXING THE SHOT NUMBERS
        shot_numbers = self.raw_df[self.shot_key]
        
        # ITERATE OVER ALL SHOTS LISTED IN THE .CSV AND GET PATHS TO THE DEVICE'S DATA FROM THAT SHOT
        # IF BOTH (A) THE SHOT HAPPENED AND (B) DATA FOR THE DEVICE WAS LOGGED DURING THE SHOT
        for i, shot in enumerate(shot_numbers):
            shot_data_path = self.raw_df[self.device_name][i]

            #WAS DATA ACTUALLY TAKEN FOR THE SHOT?
            if not shot == np.nan and not shot_data_path == np.nan:
                self.RAW_data_paths_dict[shot] = str(shot_data_path).replace(" ", "") # CONVERT THE LOCATION TO A STRING, stripping whitespaces

    def get_RAW_data_paths_dict(self)->Dict:
        """Get the data paths dictionary containing data locations for the device across all shots.
        
        Returns 
        -------
            RAW_data_paths_dict : Dict
                The dictionary containing paths to the raw shot data.
        """
        
        # FIND ALL VALID SHOTS AND BUILD UP THE DATA PATHS DICTIONARY FOR THE DEVICE
        self._find_shots()
        
        # RETURN THE DATA PATHS DICTIONARY
        return self.RAW_data_paths_dict
    
    def get_BKG_data_paths_dict(self)->Dict:
        """Get a dictionary containing data locations for different types of background for the shots
        
        Returns
        -------
            BKG_data_paths_dict : Dict
                The dictionary containing paths to the background shot data.
        """
        
        background_keys = self.background_df.keys()

        for key in background_keys:
            self.BKG_data_paths_dict[key] = str(self.background_df[key].iloc[0]).replace(" ", "")

        return self.BKG_data_paths_dict

        


