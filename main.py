#MODULE IMPORTS
import sys
import json
import os
sys.path.append(".")

from typing import Dict, Type
from utils.runmanager.runmanager import RunManager
from utils.runmanager.camrunmanager import CamRunManager 
from utils.runmanager.proberunmanager import ProbeRunManager
from utils.runmanager.temprunmanager import TempRunManager
from utils.runmanager.ldvrunmanager import LDVRunManager


from utils.dictmanager.dictmanager import DictManager

# IMPLEMENT LATER...
#from utils.dictmanager import DictManager

def main(
        data_json_path="./paths.json",
        input_json_path="./input.json"
    ):

    with open(input_json_path) as jsfile:
        input = json.load(jsfile)

    #######################################
    # DICTIONARY MANAGER- IMPLEMENT LATER #
    #######################################
    
    with open(data_json_path) as jsfile:
        paths = json.load(jsfile)

    # INITIALIZE THE DICTIONARY MANAGER
    dict_manager = DictManager(
        shot_nos=input["EXP_SHOT_NOS"],
        path = os.path.join(paths["PARENT_PATH_LOCAL"], paths[input["DEVICE_NAME"]])
    )

    # Create the correct data path dictionary.
    data_paths_dict = dict_manager.get_data_paths_dict()
    print(data_paths_dict)

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
        1:"/Users/hayden/Desktop/FIREBALL/HRMT68_data/scope_test/FastScope_TestSave_ALL_20250520173102723.csv"
    }

    pt100_paths_dict = {
        1:"/Users/hayden/Desktop/FIREBALL/HRMT68_data/temperatures/hrmt64_temperatures.csv"
    }

    ldv_paths_dict = {
        1:"/Users/hayden/Desktop/FIREBALL/HRMT68_data/ldv_and_strain_gauges/Triggers/2025/05/13/2025-05-13T180531_0200.tdms"
    }

    #######
    # RUN #
    #######
    
    # Initialise the runmanager as appropriate for each device.
    runmanagerdict : Dict[str, Type[RunManager]]= {
        "PROBE":ProbeRunManager, 
        "CAMERA": CamRunManager,
        "PT100": TempRunManager,
        "LDV": LDVRunManager,
    }
    
    # INITIALIZE THE APPROPRIATE RUN MANAGER
    run_manager = runmanagerdict[input["DEVICE_TYPE"]](
        input=input, # input configuration
        #data_paths_dict=data_paths_dict # select appropriate dictionary from the dict_of_dicts variable.
        data_paths_dict=ldv_paths_dict
    )

    #Execute the run.
    run_manager.run()
    print("Run terminated successfully without errors. \n")

if __name__ == "__main__":
    main()