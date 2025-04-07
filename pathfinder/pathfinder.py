######################################################################################################
# SCRIPT WHICH BUILDS DICTIONARIES OF DATA PATHS FOR SHOTS. IDEA IS THAT THIS TAKES SOME INPUT .CSV, #
#  EITHER ONE PER INSTRUMENT OR FROM ONE MASTER.CSV, AND THEN CONVERTS TO SOME DICTIONARY FORMAT     #
#  APPROPRIATE FOR USE IN THE MAIN CODE.                                                             #
######################################################################################################

# !!!!!!!!!! THIS SHOULD BE THE ONLY FILE IN THE PROJECT WITH HARD-CODED VALUES, WHICH ARE THE PATHS TO THE .CSV FILES !!!!!!!!

# MODULE IMPORTS
import pandas as pd
import numpy as np

class PathFinder:
    """Class responsible for scraping .csv files which contain information about the storage location of data for all equipment across all shots."""

    def __init__(self, timestamp_csv_path, device_name, shot_key):
        """
        Parameters
        ----------
            timestamp_path : str
                Path to the .csv file containing information about where all data has been stored for each shot.
        """

        # OBJECT'S CSV PATH. I'VE SHORTENED THIS FOR CLARITY, AND BY THIS POINT THERE
        #  SHOULD BE NO AMBIGUITY ABOUT WHICH .CSV THIS IS.
        self.csv_path = timestamp_csv_path

        # DEVICE NAME SO THAT WE READ FROM THE CORRECT COLUMN IN THE .CSV
        self.device_name = device_name

        # OPEN THE CSV AND GET THE DATA AS A PANDAS DATAFRAME
        self.df = pd.read_csv(self.csv_path, delimiter=",")

        self.shot_key = shot_key

        # EMPTY DATA PATHS MATRIX WHICH WE WILL BUILD UP BY USING THE .CSV FILE
        self.data_paths_dict = {}

    def _find_shots(self):
        """Scrape through the specified .csv looking to see which shots actually happened."""

        # GET THE COLUMN OF THE .CSV INDEXING THE SHOT NUMBERS
        shot_numbers = self.df[self.shot_key]
        
        # ITERATE OVER ALL SHOTS LISTED IN THE .CSV AND GET PATHS TO THE DEVICE'S DATA FROM THAT SHOT
        # IF BOTH (A) THE SHOT HAPPENED AND (B) DATA FOR THE DEVICE WAS LOGGED DURING THE SHOT
        for i, shot in enumerate(shot_numbers):
            shot_data_path = self.df[self.device_name][i]

            #WAS DATA ACTUALLY TAKEN FOR THE SHOT?
            if not shot == np.nan and not shot_data_path == np.nan:
                self.data_paths_dict[shot] = str(shot_data_path.replace(" ", "")) # CONVERT THE LOCATION TO A STRING, stripping whitespaces

    def get_data_paths_dict(self):
        """Get the data paths dictionary containing data locations for the device across all shots."""
        
        # FIND ALL VALID SHOTS AND BUILD UP THE DATA PATHS DICTIONARY FOR THE DEVICE
        self._find_shots()
        
        # RETURN THE DATA PATHS DICTIONARY
        return self.data_paths_dict
        


