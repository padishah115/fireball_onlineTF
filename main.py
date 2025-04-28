#MODULE IMPORTS
import sys
import json
import os
sys.path.append(".")

from utils.runmanager import RunManager

def main(json_path="./input.json"):
    
    with open(json_path) as jsfile:
        input = json.load(jsfile)

    # Parent data path
    data_path = '/eos/project/h/hiradmat/HRMT Experiments/2024/FIREBALL2/FB2_HRMT64_repository/HRMT64 data'

    # Check to make sure that the parent data path actually exists.
    if not os.path.exists(data_path):
        raise NotImplementedError("Error: parent data_path doesn't exist.")

    # Path to shot log
    shotlog_path = "./example_data/shotlog.csv"

    if not os.path.exists(shotlog_path):
        raise NotImplementedError("Error: path to shot log not found.")

    # List of subdirectories in parent data path which should
    folders = ["SCOPE1", "SCOPE2", "EP_Spectrometer_Cams", "PlasmaCell_Cams"]

    # Make sure all of the folders actually exist.
    for folder in folders:
        new_path = os.path.join(data_path, folder)
        if not os.path.exists(new_path):
            raise NotImplementedError(f"Path {new_path} to folder {folder} does not exist.\n")
    # Template file names at which the data will be stored
    template_fnames = {
        "DIGICAM": 'HRM{}.DigiCam_OD{}_{}_{}.csv',
        "PROBE": 'C{}_SCOPE{}_{}.csv'
    }



    # SOMEHOW BUILD THE DATA PATHS DICT
    # FOR NOW HARDCODED
    digicam3_paths_dict = {
        1:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
        2:"./example_data/data/HRM3.DigiCam_OD0_1714383312791697_1714383306135000.csv",
        3:"./example_data/data/HRM3.DigiCam_OD1_1714604587992043_1714604581335000.csv",
        4:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
    }

    andor_paths_dict = {
        1:'./example_data/data/andor.asc'
    }

    orca_paths_dict = {
        1:'./example_data/data/1ns_test.dac'
    }

    probe_paths_dict = {
        1:"./example_data/data/C1--XX_SCOPE2--00081.csv"
    }

    print("Starting run manager ... \n")
    run_manager = RunManager(
        input=input,
        data_paths_dict=orca_paths_dict
    )

    run_manager.run()
        
    print("Run terminated successfully. \n")

if __name__ == "__main__":
    main()