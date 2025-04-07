########################
# CONFIGURATION SCRIPT #
########################

# MODULE IMPORTS
import pandas as pd
from typing import Dict

# HOMEBREW IMPORTS
from run_manager.builders import * 

#######################################################
# PATHS TO ALL DATA FOR ALL INSTRUMENTS FOR ALL SHOTS #
#######################################################

# FARADAY PROBE 1
FP1_efield_data_paths = {
    1:"./example_data/C1--XX_SCOPE2--00081.csv",
    2:"./example_data/C1--XX_SCOPE2--00081.csv",
    3:"./example_data/C1--XX_SCOPE2--00081.csv"
}

FP1_bkg_efield_data_paths = {
    "DARKFIELD":"./example_data/C1--XX_SCOPE2--00081.csv",
    "BEAM ON, PLASMA OFF":"./example_data/C1--XX_SCOPE2--00081.csv",
}

# HRM3 CAMERA
HRM3_image_data_paths = {
    1:"./example_data/HRM3.DigiCam_OD0_1714383312791697_1714383306135000.csv",
    2:"./example_data/HRM3.DigiCam_OD1_1714604587992043_1714604581335000.csv",
    3:"./example_data/HRM3.DigiCam_OD2_1684845285167029_1684845278535000.csv"
}

HRM3_bkg_image_data_paths = {
    "DARKFIELD":"./example_data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv", # darkfield image
    "BEAM ON, PLASMA OFF":"./example_data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv"
}

#################################
# RUNMANAGER (RM) CONFIGURATION #
#################################

# These dictionaries tell the run_manager which devices correspond to which builder species and which data_paths. 
rm_builder_key : Dict[str, Builder]= {
    "faraday probe" : ProbeBuilder,
    "hrm3" : CamBuilder
}

rm_raw_data_paths_key : Dict[str, Dict[int, str]] = {
    "faraday probe" : FP1_efield_data_paths,
    "hrm3" : HRM3_image_data_paths
}

rm_background_data_paths_key : Dict[str, Dict[int, str]] = {
    "faraday probe" : FP1_bkg_efield_data_paths,
    "hrm3" : HRM3_bkg_image_data_paths
}

###########################
# DATA PATH CONFIGURATION #
###########################

# .csv for camerafiles
camera_timestamp_csv_path = './example_data/HRMT64_timestamps_shots_camerafiles.csv'
camera_timestamp_df = pd.read_csv(camera_timestamp_csv_path, delimiter=',')





