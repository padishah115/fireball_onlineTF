#MODULE IMPORTS
import sys
import json
import os
sys.path.append(".")

from utils.runmanager import RunManager

# IMPLEMENT LATER...
#from utils.dictmanager import DictManager

def main(json_path="./input.json"):
    
    with open(json_path) as jsfile:
        input = json.load(jsfile)

    #######################################
    # DICTIONARY MANAGER- IMPLEMENT LATER #
    #######################################

    # # Need to load the data for all shots, including the background shots.
    # all_shots = input["EXP_SHOT_NOS"] + input["BKG_SHOT_NOS"]

    # # START THE DICTIONARY MANAGER TO CREATE DATA PATH DICTIONARIES
    # dict_manager = DictManager(
    #     shot_nos=all_shots,
    #     data_path=input["DATA_PATH"],
    #     folders=input["DEVICE_FOLDERS"],
    #     template_fnames=input["TEMPLATE_FNAMES"], 
    #     shotlog_path=input["SHOTLOG_PATH"]
    #     )
    
    # # LOAD ALL DATA PATH DICTIONARIES
    # # of form {"DEVICE NAME" : {SHOT NO : /path/to/data}}
    # dict_of_dicts = dict_manager.run()

    # # START THE RUNMANAGER TO PERFORM DATA LOADING AND ARITHMETIC
    # print("Starting run manager ... \n")
    # run_manager = RunManager(
    #     input=input,
    #     data_paths_dict=dict_of_dicts["DEVICE_NAME"]
    # )
    
    ###############################################################
    ###############################################################

    digicam3_paths_dict = {
        1:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
        2:"./example_data/data/HRM3.DigiCam_OD0_1714383312791697_1714383306135000.csv",
        3:"./example_data/data/HRM3.DigiCam_OD1_1714604587992043_1714604581335000.csv",
        4:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
        5:"./example_data/data/HRM3.DigiCam_OD2_1684845285167029_1684845278535000.csv"
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

    run_manager = RunManager(
        input=input,
        data_paths_dict=digicam3_paths_dict
    )

    run_manager.run()
        
    print("Run terminated successfully without errors. \n")

if __name__ == "__main__":
    main()