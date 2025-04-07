########################
# CONFIGURATION SCRIPT #
########################

# MODULE IMPORTS
import pandas as pd
from typing import Dict
import os, sys

# Add devices module to path
sys.path.append(os.path.abspath("."))

# HOMEBREW IMPORTS
from run_manager.builders import * 
from pathfinder.pathfinder import PathFinder

def get_config():
    #####################################################
    # SHOT LOG .CSVs (must be hardcoded, unfortunately) #
    #####################################################

    shot_key = "shot number"

    #CAMERA SHOT LOG .CSV
    faradayprobe_timestamp_csv_path = './example_data/bogus_HRMT64_timestamps_faradayprobefiles.csv'
    camera_timestamp_csv_path = './example_data/bogus_HRMT64_timestamps_camerafiles.csv'

    ######################################
    # DATA PATH DICTIONARY CONFIGURATION #
    ######################################
    #  This is where, for each device, we use Pascal's .csvs to create dictionaries for each device of form
    # {SHOT_NO : /path/to/device/data/for/shot} - these are the DATA_PATHS_DICT variables.

    # FARADAY PROBE 1
    FP_pathfinder = PathFinder(timestamp_csv_path=faradayprobe_timestamp_csv_path, device_name="Faraday Probe", shot_key=shot_key)
    FP_RAW_data_paths_dict = FP_pathfinder.get_data_paths_dict() #will be 100s of entries long
    FP_BKG_data_paths_dict = {
        "DARKFIELD":"./example_data/C1--XX_SCOPE2--00081.csv",
        "BEAM ON, PLASMA OFF":"./example_data/C1--XX_SCOPE2--00081.csv",
    } #will be 100s of entries long

    # HRM3 CAMERA
    HRM3_pathfinder = PathFinder(timestamp_csv_path=camera_timestamp_csv_path, device_name="HRM3", shot_key=shot_key)
    HRM3_RAW_data_paths_dict = HRM3_pathfinder.get_data_paths_dict()
    HRM3_BKG_data_paths_dict = {
        "DARKFIELD":"./example_data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv", # darkfield image
        "BEAM ON, PLASMA OFF":"./example_data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv"
    } #will be 100s of entries long


    #################################
    # RUNMANAGER (RM) CONFIGURATION #
    #################################
    # These dictionaries tell the run_manager which devices correspond to which builder species and which data_paths. 

    rm_builder_key : Dict[str, Builder]= {
        "faraday probe" : ProbeBuilder,
        "hrm3" : CamBuilder,
        "hrm4" : CamBuilder,
        "hrm5" : CamBuilder,
        "hrm6" : CamBuilder
    }

    rm_RAW_data_paths_key : Dict[str, Dict[int, str]] = {
        "faraday probe" : FP_RAW_data_paths_dict,
        "hrm3" : HRM3_RAW_data_paths_dict
    }

    rm_BKG_data_paths_key : Dict[str, Dict[int, str]] = {
        "faraday probe" : FP_BKG_data_paths_dict,
        "hrm3" : HRM3_BKG_data_paths_dict
    }


    return rm_builder_key, rm_RAW_data_paths_key, rm_BKG_data_paths_key



