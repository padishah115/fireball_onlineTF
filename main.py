#MODULE IMPORTS
import os
import sys
import json
from typing import Dict
sys.path.append(".")

from startupmanager import StartupManager
from operationsmanager import *

def main():

    #################
    # JSON MATERIAL #
    #################

    #user-specified device name and device type
    DEVICE_NAME = "CAM3"
    device_type = "IMAGE" #note must be IMAGE or PROBE

    #User-specified input lists raw shots and background shots
    exp_shot_nos = [2, 3] #shots who we are interested in
    bkg_shot_nos = [1, 4] #background(s) to subtract. can be one or several over which we average.
    bkg_name = "DARKFIELD"
    subtract_background = True

     #list of operations which we would like to perform in order to pass to OpManager.
    operations = {
        "LINEOUT" : 1
    }
    lineout_interpretation = "Frequency Spectrum of Data"
    axis = operations["LINEOUT"]#axis for lineout calculations


    # SOMEHOW BUILD THE DATA PATHS DICT
    # FOR NOW HARDCODED
    data_paths_dict = {
        1:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
        2:"./example_data/data/HRM3.DigiCam_OD0_1714383312791697_1714383306135000.csv",
        3:"./example_data/data/HRM3.DigiCam_OD1_1714604587992043_1714604581335000.csv",
        4:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
    }

    #############################
    # RUN/LOAD MANAGER MATERIAL #
    #############################

    print("Experiment", exp_shot_nos)
    print("Background", bkg_shot_nos)
    startup_manager = StartupManager(device_type=device_type, 
                                     raw_shot_nos=exp_shot_nos, 
                                     bkg_shot_nos=bkg_shot_nos, 
                                     data_paths_dict=data_paths_dict)
    
    #NOTE- the form of these variables will be determined by whether the data
    # came from a probe or an image.
    raw_data_dict, averaged_bkg, corrected_data_dict = startup_manager.load()

    ##############################
    # OPERATION MANAGER MATERIAL #
    ##############################
    manager_key : Dict[str, OperationsManager] = {
        "IMAGE": ImageManager, 
        "PROBE": ProbeManager
    }


    for shot_no in exp_shot_nos:
        if subtract_background:
            LABEL = f"{shot_no}, {bkg_name} SUBTRACTED"
            data_dict = corrected_data_dict
        else:
            LABEL = f"{shot_no}, Raw (no background correction)"
            data_dict = raw_data_dict
        operations_manager = manager_key[device_type](
            DEVICE_NAME=DEVICE_NAME,
            shot_no=shot_no,
            label=LABEL,
            shot_data=data_dict[shot_no]) 
        if "LINEOUTS" in operations.keys():
            operations_manager.lineouts(axis=axis, ft_interp=lineout_interpretation)
        if "PLOT" in operations.keys():
            operations_manager.plot()
        


if __name__ == "__main__":
    main()