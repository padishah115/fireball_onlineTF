#MODULE IMPORTS
import sys
import numpy as np
sys.path.append(".")
import importlib
import runtime
#Import main function that calls the whole run
importlib.reload(runtime)
from runtime import main as runtime

# INPUT CONFIGURATION

background_shots = {
    "ORCA STREAK":"",
}

input = {

    #################################
    # Information about the device. #
    #################################
    # - DEVICE_NAME tells us which directory to search in
    # - DEVICE_TYPE type tells us how many channels of data we have/what type of data we're dealing with.
    # - DEVICE_SPECIES is a subset of type, and helps us decide how to load different types of data files
    #   even if the underlying data type (i.e. "image") is the same.
    "DEVICE_NAME": "ORCA STREAK",
    "DEVICE_TYPE": "CAMERA",
    "DEVICE_SPECIES": "ORCA",

    ##################
    # Shot Selection #
    ##################
    # - Can select from timestamps or from relative shot no., which is a heuristic term that sorts everything
    #   in the target directory by timestamp, then 0-indexes the shot from most recent to most distant.
    # - Can also specify the timestamp specifically. 

    # Shots indexed from 0 in reverse chronology. This is easy, and the shots are 0-indexed automatically
    # in reverse-chronological order of acquisition.
    "EXP_SHOT_NOS": [0], #if timestamps, need to be strings
    "BKG_SHOT_NOS": [],

    # Do we use the timestamps or the relative reverse-chronology method?
    "SPECIFY_TIMESTAMP_EXP": False,
    "SPECIFY_TIMESTAMP_BKG": False,

    ##########################
    # Background Subtraction #
    ##########################
    # - BKG_NAME tells us how the background will be denoted on-screen during plotting.
    # - BACKGROUND_STATUS tells us whether we want to remove the background or not. If so, bkg is subtracted BEFORE
    #   image averaging.
    # - If more than one background shot was specified, these are averaged before being subtracted from the shot image.
    "BKG_NAME": "DARKFIELD",
    "BACKGROUND_STATUS": "RAW",

    #########################
    # Operations Specifiers #
    #########################
    # - Brief details of what analysis we want to see live, but this is largely fixed for the underlying devices.
    
    "PLOT_ONLY": False, # in case we want to just quickly display the image live.
    
    "NORM_PLOT": False,
    
    "OPERATIONS": {
        "SHOW_SINGLESHOT_PLOTS": True,
        "LINEOUT_BIN_NO": 100,
        "SHOW_AVERAGE_SHOTS": True,
    },

    #########################
    # Directory Information #
    #########################
    # - PARENT_DIR tells us which folder contains all the individual devices' data directories.
    # - FOLDER_NAMES tells us where data has been logged for each of the individual devices.
    #"PARENT_DIR":r"/eos/project/h/hiradmat/HRMT Experiments/2025/HRMT68 - FIREBALL 3/FB3 repository/HRMT68_data",
    "PARENT_DIR":r"\\eosproject-smb\eos\project\h\hiradmat\HRMT Experiments\2025\HRMT68 - FIREBALL 3\FB3 repository\HRMT68_data",

    "FOLDER_NAMES": {
            "ANDOR SPECTROMETER":"andor_spectrometer_contingency/original_files",
            "ORCA STREAK":"orca_streak/original_files",
            "HRM3":"chromox_cameras/HRM3",    
            "HRM4":"chromox_cameras/HRM4",
            "HRM5":"chromox_cameras/HRM5",
            "HRM6":"chromox_cameras/HRM6",
            "SCOPE 1":"scope_test",
            "SCOPE 2":"scope_test",
            "SCOPE 3":"scope_test",
            "LDV":"ldv_and_strain_gauges\\Triggers\\2025\\05\\28",
            "PT100":"temperatures",

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
        },

    "TIMESTAMP_SLICE": {
            "ANDOR SPECTROMETER": (23, 39),
            "ORCA STREAK": (21, 37),
            "HRM3": (22, 31),    
            "HRM4": (22, 31),
            "HRM5": (22, 31),
            "HRM6": (22, 31),
            "SCOPE 1": (-21, -4),
            "SCOPE 2": (-21, -4),
            "SCOPE 3": (-21, -4),
            "LDV": (-16, -5),
            "PT100":None,
    } 
    
}

print("Starting runtime ... ")
runtime(
    input=input
)