########################
# CONFIGURATION SCRIPT #
########################
# everything ugly is in one place...

# MODULE IMPORTS
import pandas as pd
from typing import Dict
import os, sys

# Add devices module to path
sys.path.append(os.path.abspath("."))

# HOMEBREW IMPORTS
from run_manager.builders import * 
from pathfinder.pathfinder import PathFinder

#WHICH DEVICES ARE WE INTERESTED IN ANALYZING DATA FROM?
myDevices = [
        "Faraday Probe", 
        "HRM3"
    ]

#WHICH SHOTS ARE WE INTERESTED IN GATHERING DATA FROM?
myShots = [1, 2, 3]

master_timestamps_path_dict = {
    "FARADAY PROBE" : {
        "RAW_csv_path" : './example_data/bogus_HRMT64_timestamps_faradayprobefiles.csv',
        "BKG_csv_path" : './example_data/bogus_HRMT64_timestamps_fpbackgrounds.csv'
    },

    "HRM3" : {
        "RAW_csv_path" : './example_data/bogus_HRMT64_timestamps_camerafiles.csv',
        "BKG_csv_path" :'./example_data/bogus_HRMT64_timestamps_cambackgrounds.csv'
    }
}


#What is the name of the column indexing shot numbers in the .csv files?
shot_key = "shot number"

######################################
# DATA PATH DICTIONARY CONFIGURATION #
######################################

master_path_dict = {device_name.upper() : {} for device_name in myDevices}
print("Master path dictionary: ", master_path_dict)

for device_name in myDevices:

    device_name = device_name.upper()

    RAW_csv_path = master_timestamps_path_dict[device_name]["RAW_csv_path"]
    BKG_csv_path = master_timestamps_path_dict[device_name]["BKG_csv_path"]

    pathfinder = PathFinder(
        RAW_timestamp_csv_path=RAW_csv_path,
        BKG_timestamp_csv_path=BKG_csv_path,
        device_name=device_name,
        shot_key=shot_key
    )

    master_path_dict[device_name]["RAW_data_path"] = pathfinder.get_RAW_data_paths_dict()
    master_path_dict[device_name]["BKG_data_path"] = pathfinder.get_BKG_data_paths_dict()

# ###################
# # FARADAY PROBE 1 #
# ###################
# FP_pathfinder = PathFinder(RAW_timestamp_csv_path=RAW_fp_timestamp_csv_path, 
#                            BKG_timestamp_csv_path=BKG_fp_timestamp_csv_path,
#                            device_name="Faraday Probe", 
#                            shot_key=shot_key)

# FP_RAW_data_paths_dict = FP_pathfinder.get_RAW_data_paths_dict() #will be 100s of entries long
# FP_BKG_data_paths_dict = FP_pathfinder.get_BKG_data_paths_dict() #will be 100s of entries long

# ###############
# # HRM3 CAMERA #
# ###############
# HRM3_pathfinder = PathFinder(RAW_timestamp_csv_path=RAW_cam_timestamp_csv_path, 
#                              BKG_timestamp_csv_path=BKG_cam_timestamp_csv_path,
#                              device_name="HRM3", 
#                              shot_key=shot_key)

# HRM3_RAW_data_paths_dict = HRM3_pathfinder.get_RAW_data_paths_dict()
# HRM3_BKG_data_paths_dict = HRM3_pathfinder.get_BKG_data_paths_dict()


#################################
# RUNMANAGER (RM) CONFIGURATION #
#################################
# These dictionaries tell the run_manager which devices correspond to which builder species and which data_paths. 

rm_builder_key : Dict[str, Builder]= {
    "FARADAY PROBE" : ProbeBuilder,
    "HRM3" : CamBuilder,
}

rm_RAW_data_paths_key : Dict[str, Dict[int, str]] = {
    "FARADAY PROBE" : master_path_dict["FARADAY PROBE"]["RAW_data_path"],
    "HRM3" : master_path_dict["HRM3"]["RAW_data_path"]
}

rm_BKG_data_paths_key : Dict[str, Dict[int, str]] = {
    "FARADAY PROBE" : master_path_dict["FARADAY PROBE"]["BKG_data_path"],
    "HRM3" : master_path_dict["HRM3"]["BKG_data_path"]
}

print("Builder key: ", rm_builder_key)
print("Raw data paths", rm_RAW_data_paths_key)
print("Background paths", rm_BKG_data_paths_key)





