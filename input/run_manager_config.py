###################################################################################################################
# CONTAINS THE DICTIONARIES USED TO TELL THE RUNMANAGER HOW TO BEHAVE WHEN PASSED THE NAMES OF DIFFERENT DEVICES. #
# IF WE TELL THE RUNMANAGER THAT WE WANT HRM3 DATA, HOW DOES IT KNOW WHICH BUILDER SPECIES TO CALL? WHERE DOES    #
# IT LOOK FOR THE BACKGROUND DATA AND RAW DATA? THE INFORMATION IT NEEDS TO MAKE THESE DECISIONS IS ENCODED       #
# IN THE DICTIONARIES BELOW.                                                                                      #
###################################################################################################################

# MODULE IMPORTS
from typing import Dict

# GET THE DATA PATHS FROM PATHS.PY, WHICH HAVE BEEN LOCATED BY THE PATHFINDER CLASS
from input.paths import *

# BUILDER DICTIONARY:
from run_manager.builders import * 
builder_key : Dict[str, Builder]= {
    "faraday probe" : ProbeBuilder,
    "hrm3" : CamBuilder
}

################################################################################################
# USE INFORMATION FROM THE PATHS.PY FILE TO LOCATE DATA FOR EACH SHOT, INDEXED BY SHOT NUMBER  #
################################################################################################

# DICTIONARY OF RAW PATHS DICTIONARIES (dictionary squared)
raw_data_paths_key : Dict[str, Dict[int, str]] = {
    "faraday probe" : FP1_efield_data_paths,
    "hrm3" : HRM3_image_data_paths
}

# DICTIONARY OF BACKGROUND PATHS DICTIONARIES (dictionary squared)
background_data_paths_key : Dict[str, Dict[int, str]] = {
    "faraday probe" : FP1_bkg_efield_data_paths,
    "hrm3" : HRM3_bkg_image_data_paths
}