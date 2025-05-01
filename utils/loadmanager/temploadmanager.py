import pandas as pd
import numpy as np
from utils.loadmanager.loadmanager import LoadManager

class TempLoadManager(LoadManager):
    
    def __init__(self, input, data_paths_dict):
        super().__init__(input, data_paths_dict)
        self.data_dict = {}
    
    def load(self):
        """Loading function for PT100 Temperature vs Time Data"""

        # EXTRACT SHOT NUMBERS AND SHOT DATA PATHS IN ITERABLE FORM
        shot_nos = [shot_no for shot_no in self.data_paths_dict.keys()]
        shot_paths = [shot_path for shot_path in self.data_paths_dict.values()]

        for i, shot_no in enumerate(shot_nos):
            self.data_dict[shot_no] = self._load_pt100_data(shot_paths[i])
            
        return self.data_dict
    
    def _load_pt100_data(self, data_path)->dict:
        """Loads PT100 temperature data from a given data path.
        
        Parameters
        ----------
            data_path : str
                Path to the .csv containing the raw shot information for the
                PT100 diagnostic.
        """

        shot_data_dict = {"TIME": None,
                          "TEMPERATURE": {}}

        df = pd.read_csv(data_path)
        columns_list = df.columns.to_list()
        columns_list 

        #############
        # TIME DATA #
        #############
        time_key = columns_list[0]
        shot_data_dict["TIME"] = np.arange(len(df[time_key]))

        ##########################
        # CABLE TEMPERATURE DATA #
        ##########################
        shot_data_dict["TEMPERATURE"]["TNC"] = df[columns_list[2]]
        shot_data_dict["TEMPERATURE"]["TT61"] = df[columns_list[3]]

        ##############################
        # PRIMARY TARGET TEMPERATURE #
        ##############################
        shot_data_dict["TEMPERATURE"]["PTOP"] = df[columns_list[4]]
        shot_data_dict["TEMPERATURE"]["PBOTTOM"] = df[columns_list[5]]

        #########################
        # SECONDARY TARGET DATA #
        #########################
        shot_data_dict["TEMPERATURE"]["S"] = df[columns_list[6]]

        return shot_data_dict

        
