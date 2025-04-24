#MODULE IMPORTS
import os
import sys
import json
sys.path.append(".")

from startupmanager import StartupManager
from operationsmanager import OperationsManager

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

    operations = [] #list of operations which we would like to perform in order to pass to OpManager.

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
    
    raw_data_dict, averaged_bkg, corrected_data_dict = startup_manager.load()

    ##############################
    # OPERATION MANAGER MATERIAL #
    ##############################

    #SO BY THIS POINT WE HAVE:
        # a dictionary of raw shot data: {SHOT NO : RAW DATA}
        # a dictionary of corrected shot data: {SHOT NO : CORRECTED DATA}
        # a single, averaged background datum which was used to make the corrected shot data

    for shot_no in exp_shot_nos:
        operations_manager = OperationsManager(
            DEVICE_NAME=DEVICE_NAME,
            shot_no=shot_no,
            label=f"{shot_no} with {bkg_name} correction",
            shot_data=raw_data_dict[shot_no], 
            operations=[]) 
        #if "LINEOUTS" in operations:
        pixels_1D, lineouts = operations_manager.lineouts(axis=1, plot=True) #want user-input to determine axis
    #   operations_manager_lineouts = OperationsManager(lineouts, )
    #if FFT in operations:
    #   operations_manager
    #if PLOT in operations:
    #   operations_manager.plot()
    #operations_manager = OperationsManager(shot_data=corrected_data_dict[shot], operations=[])
    #operations_manager.run()


    


if __name__ == "__main__":
    main()