#MODULE IMPORTS
import os
import sys
import json
from typing import Dict, Type
sys.path.append(".")

from startupmanager import StartupManager
from operationsmanager import OperationsManager, ImageManager, ProbeManager

def main(json_path="./input.json"):

    with open(json_path) as jsfile:
        input = json.load(jsfile)


    # SOMEHOW BUILD THE DATA PATHS DICT
    # FOR NOW HARDCODED
    data_paths_dict = {
        1:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
        2:"./example_data/data/HRM3.DigiCam_OD0_1714383312791697_1714383306135000.csv",
        3:"./example_data/data/HRM3.DigiCam_OD1_1714604587992043_1714604581335000.csv",
        4:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
    }

    #############################
    # RUN/LOAD MANAGER MATERIAL #
    #############################

    startup_manager = StartupManager(device_type=input["DEVICE_TYPE"], 
                                     raw_shot_nos=input["EXP_SHOT_NOS"], 
                                     bkg_shot_nos=input["BKG_SHOT_NOS"], 
                                     data_paths_dict=data_paths_dict)
    
    raw_data_dict, bkg_data_dict, corrected_data_dict = startup_manager.load()

    ##############################
    # OPERATION MANAGER MATERIAL #
    ##############################
    manager_key : Dict[str, Type[OperationsManager]] = {
        "IMAGE": ImageManager, 
        "PROBE": ProbeManager
    }
    operations = input["OPERATIONS"]
    #for shot_no in input["EXP_SHOT_NOS"]:
    if input["SUBTRACT_BACKGROUND"] == "SUBTRACT":
        LABEL = f"{input["BKG_NAME"]}-SUBTRACTED"
        data_dict = corrected_data_dict
        shot_nos = input["EXP_SHOT_NOS"]
    elif input["SUBTRACT_BACKGROUND"] == "RAW":
        LABEL = f"Raw (no background correction)"
        data_dict = raw_data_dict
        shot_nos = input["EXP_SHOT_NOS"]
    elif input["SUBTRACT_BACKGROUND"] == "SHOW":
        LABEL = f"{input["BKG_NAME"]} BACKGROUND"
        data_dict = bkg_data_dict
        shot_nos = input["BKG_SHOT_NOS"]

    for shot_no in shot_nos:
        operations_manager = manager_key[input["DEVICE_TYPE"]](
            DEVICE_NAME=input["DEVICE_NAME"],
            shot_no=shot_no,
            label=LABEL,
            shot_data=data_dict[shot_no]) 
        if operations["LINEOUT"]:
            operations_manager.lineouts(axis=operations["LINEOUT"], ft_interp=operations["LINEOUT_FT_INTERP"])
        if input["OPERATIONS"]["PLOT"]:
            operations_manager.plot()
        


if __name__ == "__main__":
    main()