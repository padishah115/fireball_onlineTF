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

from utils.dictmanager.dictmanager import DictManager

# IMPLEMENT LATER...
#from utils.dictmanager import DictManager

def main(
        data_json_path="./paths.json",
        input_json_path="./input.json"
    ):

    #######################################
    # DICTIONARY MANAGER- IMPLEMENT LATER #
    #######################################
    
    with open(data_json_path) as jsfile:
        paths = json.load(jsfile)

    dict_manager = DictManager(paths)

    
    ###############################################################
    ###############################################################

    with open(input_json_path) as jsfile:
        input = json.load(jsfile)

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
        1:"./example_data/data/C1_SCOPE1_00013.csv"
    }

    pt100_paths_dict = {
        1:"/Users/hayden/Desktop/HRMT64 data/Temperature/hrmt64_temperatures.csv"
    }

    runmanagerdict : Dict[str, Type[RunManager]]= {
        "PROBE":ProbeRunManager, 
        "CAMERA": CamRunManager,
        "PT100": TempRunManager
    }
    
    # INITIALIZE THE APPROPRIATE RUN MANAGER
    run_manager = runmanagerdict[input["DEVICE_TYPE"]](
        input=input,
        data_paths_dict=pt100_paths_dict
    )

    #Execute the run.
    run_manager.run()
    print("Run terminated successfully without errors. \n")

if __name__ == "__main__":
    main()