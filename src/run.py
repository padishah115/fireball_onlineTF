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
    # CONFIGURATION test #
    #################

    # TELLS RUNMANAGER WHICH BUILDER CLASS TO USE FOR EACH DEVICE
    builder_key : Dict[str, Builder]= {
        "FARADAY PROBE" : ProbeBuilder,
        "HRM3" : CamBuilder,
    }

    # LOAD CONFIGURATION INFORMATION FROM .JSON
    with open(json_path, "r") as json_file: 
        config = json.load(json_file)

    #ARE WE INTERESTED IN SEEING ANY VISUALISATION OF THE DATA?
    plots=True

    # INITIALIZE THE RUN MANAGER USING CONFIGURATION GIVEN ABOVE
    myManager=RunManager(
        devices=config["DEVICES"], #devices that we will gather data from
        shots=config["SHOTS"], #shots that we're interested in
        rm_builder_key=builder_key, #class registry telling the runmanager which builder class is needed for each device
        background_corrections=config["BACKGROUND CORRECTIONS"],
        operations=config["OPERATIONS"], #operations which we want to perform on the data
        plots=plots #want to plot the data
    )
    
    # Configure the runmanager
    myManager.configure(
        master_csv_dict=config["MASTER_CSV_DICT"], #dictionary containing paths to each device's .csv containing paths to raw and background-corrected data for each shot (GENERATED FROM MASTER.CSV)
        shot_key=config["SHOT KEY"] #column title for shot numbers in the .csv data that will be parsed.
    )
    
    #######
    # RUN #
    #######

    # Execute the run!
    myManager.run()


if __name__ == "__main__":
    main()