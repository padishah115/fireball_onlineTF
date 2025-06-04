#MODULE IMPORTS
import sys
sys.path.append(".")
from run.runtime import main as runtime
import matplotlib.pyplot as plt
import time

# Information about the background shots for each device
from config.background_shots import background_shots

# device information that allows us to more quickly change device by name during the run
from config.device_info import device_info, TIMESTAMP_SLICE

#path information!
from config.paths import PARENT_DIR, LOG_PATH, FOLDER_NAMES, EXTENSION_DICT

# build a logger! you know you want to!
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)
logger = logging.getLogger(__name__)


device_names = [
    "ORCA STREAK",
    "ANDOR SPECTROMETER",
    "HRM5", 
    "HRM3",
    #"SCOPE 2"
    ]


def main(device_name):
    input = {

        ##################
        # Shot Selection #
        ##################
        "EXP_SHOT_NOS": [0], #if timestamps, need to be strings
        "BKG_SHOT_NOS": [timestamp for timestamp in background_shots[device_name]],

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
            "SHOW_AVERAGE_SHOTS": False,
            "SUBTRACT_DC_OFFSET": True,
            "VMAX":1000, #VMAX VALUE FOR THE IMSHOW METHOD
        },

        #################################
        # Information about the device and run. #
        #################################
        "DEVICE_NAME": device_name,
        "DEVICE_TYPE": device_info["TYPE"][device_name],
        "DEVICE_SPECIES": device_info["SPECIES"][device_name],

        #########################
        # Directory Information #
        #########################
        "PARENT_DIR":PARENT_DIR,
        "LOG_PATH":LOG_PATH,
        "FOLDER_NAMES":FOLDER_NAMES,
        "EXTENSION_DICT":EXTENSION_DICT,

        "TIMESTAMP_SLICE":TIMESTAMP_SLICE,
        
    }


    logger.info("Starting runtime ... \n")
    runtime(
        input=input
    )
    logger.info("Ending runtime ...\n")


if __name__ == "__main__":

    ti = time.time()
    for device_name in device_names:
        print(device_name)
        main(device_name=device_name)
    tf = time.time()
    dt = tf-ti
    print(f"Time to execute: {dt:.5f}")
    plt.show()
    