###################
# MAIN RUN SCRIPT #
###################

#Module imports
import os
import sys
import json

# Add devices module to path
sys.path.append(os.path.abspath("."))

#Imports from run_manger
from run_manager.run_manager import RunManager
from run_manager.builders import *

def main(json_path:str="./src/input.json"):

    #################
    # CONFIGURATION #
    #################

    # TELLS RUNMANAGER WHICH BUILDER CLASS TO USE FOR EACH DEVICE
    builder_key : Dict[str, Builder]= {
        "FARADAY PROBE" : ProbeBuilder,
        "HRM3" : CamBuilder,
    }

    # LOAD CONFIGURATION INFORMATION FROM .JSON
    with open(json_path, "r") as json_file: 
        config = json.load(json_file)
        
        #LIST OF DEVICES THAT WE WANT DATA FROM
        myDevices : List[str] = config["myDevices"]
        
        # DICTIONARY CONTAINING PATHS TO MASTER.CSV FOR 
        master_timestamps_path_dict : Dict = config["master_timestamps_path_dict"]

        # HOW ARE THE SHOT COLUMNS LABELLED IN THE .CSV FILES
        shot_key : str = config["shot key"]

        # WHICH SHOTS DO WE WANT TO GET DATA FOR
        myShots : List[str] = config["myShots"]


    # FORMAT IN ALL CAPS TO PREVENT KEY ERRORS
    myDevices = [device.upper() for device in myDevices]


    #ARE WE INTERESTED IN SEEING ANY VISUALISATION OF THE DATA?
    plots=True

    # INITIALIZE THE RUN MANAGER USING CONFIGURATION GIVEN ABOVE
    myManager=RunManager(
        devices=myDevices,
        shots=myShots,
        rm_builder_key=builder_key,
        plots=plots
    )
    
    # Configure the runmanager
    myManager.configure(
        master_timestamps_path_dict=master_timestamps_path_dict,
        shot_key=shot_key
    )
    
    #######
    # RUN #
    #######

    # Execute the run!
    myManager.run()


if __name__ == "__main__":
    main()