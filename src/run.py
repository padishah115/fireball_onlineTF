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
from utils.run_manager import RunManager
from utils.builders import *

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
        myDevices : List[str] = config["DEVICES"]
        
        # DICTIONARY CONTAINING PATHS TO MASTER.CSV FOR 
        master_csv_dict : Dict = config["MASTER_CSV_DICT"]

        # HOW ARE THE SHOT COLUMNS LABELLED IN THE .CSV FILES
        shot_key : str = config["SHOT KEY"]

        # WHICH SHOTS DO WE WANT TO GET DATA FOR
        myShots : List[int] = config["SHOTS"]

        # WHICH OPERATIONS DO WE WANT TO PERFORM ON THE DATA
        myBackgroundCorrections : List[str] = config["BACKGROUND CORRECTIONS"] #specify types of background subtraction
        myOperations : List[str] = config["OPERATIONS"] #specify types of operation (e.g. averaging)


    # FORMAT IN ALL CAPS TO PREVENT KEY ERRORS
    myDevices = [device.upper() for device in myDevices]


    #ARE WE INTERESTED IN SEEING ANY VISUALISATION OF THE DATA?
    plots=True

    # INITIALIZE THE RUN MANAGER USING CONFIGURATION GIVEN ABOVE
    myManager=RunManager(
        devices=myDevices, #devices that we will gather data from
        shots=myShots, #shots that we're interested in
        rm_builder_key=builder_key, #class registry telling the runmanager which builder class is needed for each device
        background_corrections=myBackgroundCorrections,
        operations=myOperations, #operations which we want to perform on the data
        plots=plots #want to plot the data
    )
    
    # Configure the runmanager
    myManager.configure(
        master_csv_dict=master_csv_dict, #dictionary containing paths to each device's .csv containing paths to raw and background-corrected data for each shot
        shot_key=shot_key #column title for shot numbers in the .csv data that will be parsed.
    )
    
    #######
    # RUN #
    #######

    # Execute the run!
    myManager.run()


if __name__ == "__main__":
    main()