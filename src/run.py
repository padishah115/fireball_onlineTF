###################
# MAIN RUN SCRIPT #
###################

#Module imports
import os
import sys
from config import get_config

# Add devices module to path
sys.path.append(os.path.abspath("."))

#Imports from run_manger
from run_manager.run_manager import RunManager

def main():
    
    # CALL CONFIGURATION SCRIPT- initializes runmanager configuration (where to find data for all shots for all devices) 
    # eventually will want to pass shot numbers as arguments to the get_config function
    rm_builder_key,rm_RAW_data_paths_key, rm_BKG_data_paths_key  = get_config()

    #Think about passing the devices list from an input/configuration file here instead of passing them one-by-one to a list.
    #WHICH DEVICES ARE WE INTERESTED IN ANALYZING DATA FROM?
    myDevices = [
        "Faraday Probe", "HRM3"
    ]

    #WHICH SHOTS ARE WE INTERESTED IN GATHERING DATA FROM?
    myShots = [1, 2, 3]

    #AVERAGING METHODS

    #ARE WE INTERESTED IN SEEING ANY VISUALISATION OF THE DATA?
    plots=True

    # INITIALIZE THE RUN MANAGER USING CONFIGURATION GIVEN ABOVE
    myManager=RunManager(
        devices=myDevices,
        shots=myShots,
        rm_builder_key=rm_builder_key,
        rm_RAW_data_paths_key=rm_RAW_data_paths_key,
        rm_BKG_data_paths_key=rm_BKG_data_paths_key,
        plots=plots
    )

    #Execute the run!
    myManager.run()


if __name__ == "__main__":
    main()