###################
# MAIN RUN SCRIPT #
###################

#Module imports
import os
import sys
from config import *

# Add devices module to path
sys.path.append(os.path.abspath("."))

#Imports from run_manger
from run_manager.run_manager import RunManager

def main():

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