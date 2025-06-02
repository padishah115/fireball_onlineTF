import os
import pandas as pd
import datetime

class FileManager:
    """Class which is responsible for handling files for a device at some specified location."""
    
    def __init__(self, all_data_path, input):
        """Initialization function for the FileManager class.
        
        Parameters
        ----------
            all_data_path : str
                Path to the directory containing all the data files for the device.
            input : dict
                Input configuration dictionary for the run.
        """

        # Initialise the path and input configuration dictionary
        self.all_data_path = all_data_path
        self.input = input
        print(f"Path contents: {os.listdir(all_data_path)}\n")


    def get_files(self)->dict[str, str]:
        """Returns a list of file names in the provided directory, so long as the files contain the appropriate extension.
        
        Returns
        -------
            files_dict_sorted : dict[str, str]
                Dictionary of files and timestamps, sorted in reverse-chronological order by timestamp. The KEY is the timestamp,
                the VALUE is the filename.
        """

        # Select the appropriate file extension
        extension = self.input["EXTENSION_DICT"][self.input["DEVICE_NAME"]]

        # Accumulate list of files with the correct extension in the directory provided.
        timestamp_slice = self.input["TIMESTAMP_SLICE"][self.input["DEVICE_NAME"]] # slice we need to take from the string to get the timestamp
        
        # Create dictionary of files and their timestamps. If we have no pre-determined means of doing this, fall back on using os.stat().st_mtime. The dictionaries are of form {Timestamp:Slice}
        if timestamp_slice is not None:
            files_dict = {f[timestamp_slice[0]:timestamp_slice[1]]:f for f in os.listdir(self.all_data_path) if f.endswith(extension)\
                    and not os.path.isdir(os.path.join(self.all_data_path, f))}
        else:
            print(f"Warning: no timestamp slice provided for {self.input['DEVICE_NAME']}")
            files_dict = {str(int(os.stat(os.path.join(self.all_data_path, f)).st_mtime)):f for f in os.listdir(self.all_data_path) if f.endswith(extension)\
                    and not os.path.isdir(os.path.join(self.all_data_path, f))}
            
        print(f"File dictionary: {files_dict}\n")

        #######################################
        # Maintain a SHOT LOG of all devices. #
        #######################################
        if not os.path.exists(self.input["LOG_PATH"]):
            os.makedirs(self.input["LOG_PATH"], exist_ok=True)
        
        times = [datetime.datetime.fromtimestamp(int(timestamp)) for timestamp in files_dict.keys()]
        
        df = pd.DataFrame({"TIMESTAMPS": files_dict.keys(), "TIMES": times, "FILES": files_dict.values()})
        df.to_csv(os.path.join(self.input["LOG_PATH"], self.input["DEVICE_NAME"] + ".csv"), index=False)
        

        # Sort the files in reverse order to their timestamps (i.e. most recent files are earlier in the list)
        files_dict_sorted = dict(sorted(files_dict.items(), key=lambda item : item[0], reverse=True))
        # make sure that we are not asking for a larger number of shots than actually exist ...
        if len(self.input["EXP_SHOT_NOS"]) > len(files_dict_sorted.values()):
            no_of_req_shots = len(self.input["EXP_SHOT_NOS"])
            no_of_files = len(files_dict_sorted)
            raise ValueError(f"Error: requested {no_of_req_shots} shots, but only {no_of_files} were found.")

        return files_dict_sorted
