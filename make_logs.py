##########################################
# MAKE A SHOT LOG FOR A SPECIFIED DEVICE #
##########################################

from main import input
import os
import datetime
import time
import pandas as pd

# Specify the device for which we want to make the shot log
myDevice = "SCOPE 2"

#Gather the parent directory and child folder information from the device
parent_dir : str = input["PARENT_DIR"]
folder_names : dict = input["FOLDER_NAMES"]
DEVICES = [device for device in folder_names.keys()]

#Initiaize a list of paths to different diagnostic's data.
paths_to_data : dict = {
        device:os.path.join(parent_dir, folder_names[device]) for device in folder_names.keys()
}

def generate_log(device):
    """Generates a shot log for a specified device."""

    # Select the appropriate file extension
    extension = input["EXTENSION_DICT"][myDevice]
    path = paths_to_data[device]

    # Dictionary of files for the device.
    files_dict = {str(int(os.stat(os.path.join(path, f)).st_mtime)):f for f in os.listdir(path)\
                if f.endswith(extension) and not os.path.isdir(os.path.join(path, f))}

    # If the path for saving doesn't exist, make it!
    if not os.path.exists(input["LOG_PATH"]):
                os.makedirs(input["LOG_PATH"], exist_ok=True)
            
    # Convert the UNIX timestamp to physical time data.
    times = [datetime.datetime.fromtimestamp(int(timestamp)) for timestamp in files_dict.keys()]

    #Initialise a pandas dataframe to store information about the 
    df = pd.DataFrame({"TIMESTAMPS": files_dict.keys(), "TIMES": times, "FILES": files_dict.values()})
    
    save_path = os.path.join(input["LOG_PATH"], myDevice + ".csv")
    print(save_path)
    df.to_csv(save_path, index=False)


if __name__ == "__main__":
    ti = time.time()
    generate_log(device=myDevice)
    tf = time.time()
    print(tf-ti)


