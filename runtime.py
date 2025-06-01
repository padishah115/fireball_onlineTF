#External imports
import os

# pathmanager imports
from utils.filemanager.filemanager import FileManager

# runmanager imports
from utils.runmanager.runmanager import RunManager
from utils.runmanager.camrunmanager import CamRunManager 
from utils.runmanager.proberunmanager import ProbeRunManager
from utils.runmanager.temprunmanager import TempRunManager
from utils.runmanager.ldvrunmanager import LDVRunManager


def main(input):
    """Main function that executes the run.
    
    Parameters
    ----------
        input : dict
            Input configuration information, passed as a dictionary.
    """

    ################
    # PATH LOADING #
    ################
    print("Loading paths...") 
    # INITIALIZE PATH TO THE DEVICE'S DATA, USING CONFIGURATION FILES.
    path = os.path.join(input["PARENT_DIR"], input["FOLDER_NAMES"][input["DEVICE_NAME"]])
    # check to make sure it actually exists
    if not os.path.exists(path):
        raise FileNotFoundError(f"Warning: path {path} doesn't exist")

    # select appropriate filemanager from dictionary.
    file_manager = FileManager(
        path=path,
        input=input
    )
                
    #Get a list of files for the device
    files_dict_sorted = file_manager.get_files()
    if not files_dict_sorted:
            raise FileNotFoundError(f"Error: no files of appropriate type found at specified location.")


    ##########################################################################################
    # INITIALIZE PATH DICTIONARY BASED ON WHETHER USER WANTS TO SCRAPE FROM TIMESTAMP OR NOT #
    ##########################################################################################
    

    # Check to make sure that we have a prescription for extracting timestamp data from the filename
    if input["TIMESTAMP_SLICE"] is None:
        raise ValueError(f"Error: device {input['DEVICE_NAME']} does not have any timestamp or cyclestamp naming implemented.")

    # If we were using relative indexing, need to convert the shots indices to timestamps
    timestamps = [timestamp for timestamp in files_dict_sorted.keys()]
    if input["SPECIFY_TIMESTAMP_EXP"] == False:
        input["EXP_SHOT_NOS"] = [timestamps[i] for i in input["EXP_SHOT_NOS"]]

    if input["SPECIFY_TIMESTAMP_BKG"] == False:
        input["BKG_SHOT_NOS"] = [timestamps[j] for j in input["BKG_SHOT_NOS"]]

    paths_dict = {timestamp:os.path.join(path, file) for timestamp, file in files_dict_sorted.items()\
                  if timestamp in input["EXP_SHOT_NOS"] or timestamp in input["BKG_SHOT_NOS"]
    }
    
    
    if not paths_dict:
        raise FileNotFoundError(f"Warning: paths dictionary is empty.")


    


    #######
    # RUN #
    #######
    print("Starting runs...") 
    # Initialise the runmanager as appropriate for each device.
    runmanagerdict : dict[str, type[RunManager]]= {
        "PROBE":ProbeRunManager, 
        "CAMERA": CamRunManager,
        "PT100": TempRunManager,
        "LDV": LDVRunManager,
    }
    
    # INITIALIZE THE APPROPRIATE RUN MANAGER
    run_manager = runmanagerdict[input["DEVICE_TYPE"]](
        input=input, # input configuration
        #data_paths_dict=data_paths_dict # select appropriate dictionary from the dict_of_dicts variable.
        data_paths_dict=paths_dict
    )

    #Execute the run.
    run_manager.run()
    print("Run terminated successfully without errors. \n")