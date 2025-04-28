#MODULE IMPORTS
import sys
import json
import os
sys.path.append(".")

from utils.runmanager import RunManager
from utils.dictmanager import DictManager

def main(json_path="./input.json"):
    
    with open(json_path) as jsfile:
        input = json.load(jsfile)

    # Need to load the data for all shots, including the background shots.
    all_shots = input["EXP_SHOT_NOS"] + input["BKG_SHOT_NOS"]

    # START THE DICTIONARY MANAGER TO CREATE DATA PATH DICTIONARIES
    dict_manager = DictManager(
        shot_nos=all_shots,
        data_path=input["DATA_PATH"],
        folders=input["DEVICE_FOLDERS"],
        template_fnames=input["TEMPLATE_FNAMES"], 
        shotlog_path=input["SHOTLOG_PATH"]
        )
    
    # LOAD ALL DATA PATH DICTIONARIES
    # of form {"DEVICE NAME" : {SHOT NO : /path/to/data}}
    dict_of_dicts = dict_manager.run()

    # START THE RUNMANAGER TO PERFORM DATA LOADING AND ARITHMETIC
    print("Starting run manager ... \n")
    run_manager = RunManager(
        input=input,
        data_paths_dict=dict_of_dicts["DEVICE_NAME"]
    )

    run_manager.run()
        
    print("Run terminated successfully. \n")

if __name__ == "__main__":
    main()