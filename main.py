#MODULE IMPORTS
import sys
sys.path.append(".")
from run.run import run
import matplotlib.pyplot as plt
from utils.directory_methods import clear_directory
import copy

# Information about the background shots for each device
from config.background_shots import background_shots

# device information that allows us to more quickly change device by name during the run
from config.device_info import device_info, TIMESTAMP_SLICE

#path information!
from config.paths import PARENT_DIR_WINDOWS, LOG_PATH, FOLDER_NAMES, EXTENSION_DICT, SCOPECACHE_PATH

print("Modules loaded")

#List of devices whom we want to analyse. Check config/allowed_inputs.json to check spellings (e.g. HrM3 will throw an error,
# but HRM3 won't!)

device_names = [
    "HRM6",
    #"HRM6",
    ]

input = {
        "NAME": "PAIR BEAM + ARGON",

        ##################
        # Shot Selection #
        ##################
        "EXP_SHOT_NOS": ["1749040010", "1749040082", "1749040154", "1749040227", "1749040296"], #if timestamps, need to be strings
        "BKG_SHOT_NOS": [],

        "SPECIFY_TIMESTAMP_EXP": True,
        "SPECIFY_TIMESTAMP_BKG": False,

        "BKG_NAME": "DARKFIELD",
        "BACKGROUND_STATUS": "RAW",

        #########################
        # Operations Specifiers #
        #########################
        
        "PLOT_ONLY": False, # in case we want to just quickly display the image live.
        
        "NORM_PLOT": False,
        
        "OPERATIONS": {
            "SHOW_SINGLESHOT_PLOTS": False,
            "LINEOUT_BIN_NO": 100,
            "SHOW_AVERAGE_SHOTS": True,
            "SUBTRACT_DC_OFFSET": False,
            "VMAX":500, #VMAX VALUE FOR THE IMSHOW METHOD
            
            #Warping specifications
            "WARP":{
                "HRM3":False,
                "HRM4":False,
                "HRM5":True,
                "HRM6":True
            }, 
            "WARP_SPECS":{
                # Pixel values corresponding to corner locations
                "CORNERS":{"HRM5":[[100, 128], [1370, 48], [1440, 611], [100, 688]], "HRM6":[[28, 85], [1628, 8], [1648, 481], [33, 603]]},
                
                # Physical dimensions of chromox screens in mm
                "H":{"HRM5":100, "HRM6":100},
                "W":{"HRM5":300, "HRM6":400}
            }

        },

        #########################
        # Directory Information #
        #########################
        "PARENT_DIR":PARENT_DIR_WINDOWS,
        "LOG_PATH":LOG_PATH,
        "FOLDER_NAMES":FOLDER_NAMES,
        "EXTENSION_DICT":EXTENSION_DICT,

        "TIMESTAMP_SLICE":TIMESTAMP_SLICE,

        "SCOPECACHE_PATH":SCOPECACHE_PATH
        
    }

def main(device_names:list):
    """
    Parameters
    ----------
        device_names : list[str]
            List of devices on whom we wish to call the analysis.
    """

    # Iterate through specified devices and call functions.
    for device_name in device_names:
        print(device_name)
        input_config = copy.deepcopy(input)
        myrun = run(device_name, input_config)
        myrun.display_device()
        plt.show()

if __name__ == "__main__":
    #Execute the run.
    main(device_names=device_names)