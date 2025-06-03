import os
from utils.filemanager.filemanager import FileManager


class PathManager():
    """Class responsible for handling those pesky functions dealing with the writing and managing of paths."""

    def __init__(self, input):
        """Initialization function for the PathManager class"""

        self.input = input
       
        # INITIALIZE PATH TO THE ALL THE DEVICE'S DATA, USING CONFIGURATION FILES.
        self.all_data_path = os.path.join(input["PARENT_DIR"], input["FOLDER_NAMES"][input["DEVICE_NAME"]])
        
        if not os.path.exists(self.all_data_path):
            raise FileNotFoundError(f"Warning: path {self.all_data_path} doesn't exist")
        
        self.files_dict_sorted = self.create_files_dict()

        # Correct timestamps if using relative indexing.
        self.correct_timestamps()


        
    def get_paths_dict(self)->dict:
        """Method responsible for creating a dictionary of paths, keyed by timestamp (shot number).
        
        Returns
        -------
            paths_dict : dict
                Dictionary of files' paths, keyed by timestamp.
        """

        paths_dict = {timestamp:os.path.join(self.all_data_path, file) for timestamp, file in self.files_dict_sorted.items()\
                    if timestamp in self.input["EXP_SHOT_NOS"] or timestamp in self.input["BKG_SHOT_NOS"]
        }
        
        if not paths_dict:
            raise FileNotFoundError(f"Warning: paths dictionary is empty.")
        
        return paths_dict
    
    
    def create_files_dict(self)->dict:
        """Creates a dictionary of files in the data directory for the device, keyed by timestamp.
        
        Returns
        -------
            files_dict_sorted : dict
                A dictionary of the files in the data directory, which has been sorted wrt timestamp of the data.
        """

        # create a filemanager to list the files in the directory, checking that they all have the appropriate extensions, etc.
        file_manager = FileManager(
            all_data_path=self.all_data_path,
            input=self.input
        )
                    
        #Get a list of files for the device
        files_dict_sorted = file_manager.get_files()
        if not files_dict_sorted:
                raise FileNotFoundError(f"Error: no files of appropriate type found at specified location.")
        
        return files_dict_sorted


    def correct_timestamps(self):
        """If we have specified the shots that we desire using relative indexing, we want to convert this back to actual UNIX timestamps."""

        # If we were using relative indexing, need to convert the shots indices to timestamps
        timestamps = [timestamp for timestamp in self.files_dict_sorted.keys()]
        if self.input["SPECIFY_TIMESTAMP_EXP"] == False:
            self.input["EXP_SHOT_NOS"] = [timestamps[i] for i in self.input["EXP_SHOT_NOS"]]

        if self.input["SPECIFY_TIMESTAMP_BKG"] == False:
            self.input["BKG_SHOT_NOS"] = [timestamps[j] for j in self.input["BKG_SHOT_NOS"]]