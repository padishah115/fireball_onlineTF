#MODULE IMPORTS
import logging.config
import sys
sys.path.append(".")
import runtime
from runtime import main as runtime
import numpy as np
import logging

logging.basicConfig(filename="log.log", level=logging.INFO)
logger = logging.getLogger(__name__)

# INPUT CONFIGURATION

background_shots = {
    "ORCA STREAK":['1748851353','1748851337', '1748851311', '1748851286', '1748851261'],
    "ANDOR SPECTROMETER":['1748852619', '1748852613', '1748852609', '1748852605', '1748852601'],
    "HRM3": [],    
    "HRM4": [],
    "HRM5": [],
    "HRM6": [],
    "SCOPE 1": [],
    "SCOPE 2": [],
    "LDV": [],
    "PT100": [],

    "CHROMOX TEST":[]
}

device_info = {
    "DEVICE_NAME": "HRM4",
    "DEVICE_TYPE": "CAMERA",
    "DEVICE_SPECIES": "DIGICAM",
}

input = {

    ##################
    # Shot Selection #
    ##################
    "EXP_SHOT_NOS": [i for i in np.arange(5)], #if timestamps, need to be strings
    "BKG_SHOT_NOS": [timestamp for timestamp in background_shots[device_info["DEVICE_NAME"]]],

    "SPECIFY_TIMESTAMP_EXP": False,
    "SPECIFY_TIMESTAMP_BKG": True,

    "BKG_NAME": "DARKFIELD",
    "BACKGROUND_STATUS": "RAW",

    #########################
    # Operations Specifiers #
    #########################
    
    "PLOT_ONLY": True, # in case we want to just quickly display the image live.
    
    "NORM_PLOT": False,
    
    "OPERATIONS": {
        "SHOW_SINGLESHOT_PLOTS": True,
        "LINEOUT_BIN_NO": 100,
        "SHOW_AVERAGE_SHOTS": True,
        "SUBTRACT_DC_OFFSET": False,
    },

    #################################
    # Information about the device and run. #
    #################################
    "DEVICE_NAME": device_info["DEVICE_NAME"],
    "DEVICE_TYPE": device_info["DEVICE_TYPE"],
    "DEVICE_SPECIES": device_info["DEVICE_SPECIES"],

    #########################
    # Directory Information #
    #########################
    "PARENT_DIR":r"\\eosproject-smb\eos\project\h\hiradmat\HRMT Experiments\2025\HRMT68 - FIREBALL 3\FB3 repository\HRMT68_data",
    "LOG_PATH":r"H:\user\h\hramm\shot-log",

    "FOLDER_NAMES": {
            
            "ANDOR SPECTROMETER":"andor_spectrometer_contingency\\original_files",
            "ORCA STREAK":"orca_streak\\original_files",
            
            "HRM3":"chromox_cameras\\HRM3",    
            "HRM4":"chromox_cameras\\HRM4",
            "HRM5":"chromox_cameras\\HRM5",
            "HRM6":"chromox_cameras\\HRM6",
            
            "SCOPE 1":"scope_pool05710001",
            "SCOPE 2":"scope_pool05720010",
            
            "LDV":"ldv_and_strain_gauges\\Triggers\\2025\\06\\2",
            "PT100":"temperatures",

            "CHROMOX TEST":"plasmacell_cams"

    },

    ####################
    # File information #
    ####################
    # - EXTENSION_DICT tells us what file extension we are expecting for each of the devices. This is for
    #   exception handling, and tips us off if we are mistaking which device's data we are looking at.
    # - TIMESTAMP_SLICE tells us how to slice up the filename strings in order to extract timestamp information.
    "EXTENSION_DICT" : {
            "ANDOR SPECTROMETER": ".asc",
            "ORCA STREAK": ".dac",
            "HRM3":".csv",    
            "HRM4":".csv",
            "HRM5":".csv",
            "HRM6":".csv",
            "SCOPE 1": ".csv",
            "SCOPE 2": ".csv",
            "SCOPE 3": ".csv",
            "LDV": ".tdms",
            "PT100": ".csv",

            "CHROMOX TEST":".csv",
        },

     "TIMESTAMP_SLICE": {
            "ANDOR SPECTROMETER":None,# (23, 39),
            "ORCA STREAK":None, #(21, 37),
            "HRM3": None, #(22, 31),    
            "HRM4": None, #(22, 31),
            "HRM5": None, #(22, 31),
            "HRM6": None, #(22, 31),
            "SCOPE 1": None, #(-21, -4),
            "SCOPE 2": None, #(-21, -4),
            "SCOPE 3": None,#(-21, -4),
            "LDV": None, #(-16, -5),
            "PT100":None,

            "CHROMOX TEST":None,
    } 
    
}

if __name__ == "__main__":
    logger.info("Starting runtime ... \n")
    runtime(
        input=input
    )
    logger.info("Ending runtime ...\n")