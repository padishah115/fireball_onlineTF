import os

class DictManager:
    
    def __init__(self, shot_nos:list[int], path):
        """Initialization function for the DictManager class.
        
        Parameters
        ----------
            shot_nos : list[int]
                List of shot numbers that we are interested in for the device.
            path : str
                Path to the data for the device.

        """

        # Initialise the shot number list.
        self.shot_nos = shot_nos

        # Initialise the initial path to the device's data.
        self.path = path

    
    def get_data_paths_dict(self)->dict[str, dict[str, str]]:
        """Returns a the dictionary of form {SHOT NO: /PATH/TO/DATA} for the device.

        Returns
        -------
            data_paths_dict : dict
                Dictionary of form {SHOT NO : /PATH/TO/DATA} for the device.
        """

        # We will fill up this dictionary with pairs of shot number and paths to data for a given shot.
        data_paths_dict = {}

        # List of files contained in the directory.
        files = os.listdir(self.path)

        for file in files:
            data_paths_dict[file[:-4]] = file

        
        return data_paths_dict