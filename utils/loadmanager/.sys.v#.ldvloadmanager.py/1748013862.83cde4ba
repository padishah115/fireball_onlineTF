from utils.loadmanager.loadmanager import LoadManager
from nptdms import TdmsFile

class LDVLoadManager(LoadManager):
    
    def __init__(self, input, data_paths_dict):
        super().__init__(input, data_paths_dict)
        self.data_dict = {}

    def load(self)->dict:
        """Loading function for LDV and Strain Gauge Data.
        
        Returns
        -------
            self.data_dict
                Dictionary of shot data for all the specified shots. This is of the form {Shot NO: Shot Data Dict}
        """

        # EXTRACT SHOT NUMBERS AND SHOT DATA PATHS IN ITERABLE FORM
        shot_nos = [shot_no for shot_no in self.data_paths_dict.keys()]
        shot_paths = [shot_path for shot_path in self.data_paths_dict.values()]

        for i, shot_no in enumerate(shot_nos):
            self.data_dict[shot_no] = self._load_ldv_data(shot_paths[i])
            
        return self.data_dict
    
    def _load_ldv_data(self, path)->dict:
        """Loads the LDV data in appropriate format. We have channels for time, LDV position, LDV speed, central gauge strain,
        and downstream gauge strain."""

        shot_data_dict = {}

        with TdmsFile.open(path) as tdms_file:
            group = tdms_file["LDV_SG"]

            for channel in group.channels():
                shot_data_dict[channel.name] = channel[:]
                print("Channel:", channel)

            return shot_data_dict

