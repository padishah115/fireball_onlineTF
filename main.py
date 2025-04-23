#MODULE IMPORTS
import os
import sys
sys.path.append(".")

from runmanagers import *

def main():

    #################
    # JSON MATERIAL #
    #################

    #user-specified device name and device type
    DEVICE_NAME = ""
    device_type = "IMAGE" #note must be IMAGE or PROBE

    #User-specified input lists raw shots and background shots
    raw_shot_nos = [] #shots who we are interested in
    bkg_shot_nos = [] #background(s) to subtract. can be one or several over which we average.
    bkg_name = ""

    operations = [] #list of operations which we would like to perform in order to pass to OpManager.

    # SOMEHOW BUILD THE DATA PATHS DICT
    data_paths_dict = {}

    #############################
    # RUN/LOAD MANAGER MATERIAL #
    #############################

    #Function loads all of the specified shots from combined list
    # replace if/else clause with similar architecture to what I used for the "builders" before
    if device_type == "IMAGE":
        raw_data_dict = IMAGE_load_shots(raw_shot_nos, data_paths_dict=)
        bkg_data_dict = IMAGE_load_shots(bkg_shot_nos, data_paths_dict=)
        #Take average of background data to produce single background
        averaged_bkg = arrays_stats(bkg_data_dict.values())[0]
    elif device_type == "PROBE":
        raw_data_dict = PROBE_load_all_shots(raw_shot_nos, data_paths_dict=)
        bkg_data_dict = PROBE_load_all_shots(raw_shot_nos, data_paths_dict=)
        bkg_voltages = [datum["VOLTAGES"] for datum in bkg_data_dict.values()]
        #Take average of background data to produce single background
        averaged_bkg = arrays_stats(bkg_data_dict.values())[0]
    else:
        raise ValueError(f"Warning: device type '{device_type}' not valid.")
    
    #use subtraction function to create appropriate (corrected) images
    corrected_data_dict = {}
    for shot_no in raw_shot_nos:
        corrected_data = bkg_subtraction(raw_arr=raw_data_dict[shot_no], bkg_arr=averaged_bkg)
        corrected_data_dict[shot_no] = corrected_data

    ##############################
    # OPERATION MANAGER MATERIAL #
    ##############################

    #SO BY THIS POINT WE HAVE:
        # a dictionary of raw shot data: {SHOT NO : RAW DATA}
        # a dictionary of corrected shot data: {SHOT NO : CORRECTED DATA}
        # a single, averaged background datum which was used to make the corrected shot data

    #display or plot as required
    # use the high-level functions to perform analysis that we want.

    #operations_manager = OperationsManager(shot_data=raw_data_dict[shot], operations=[]) 
    #operations_manager = OperationsManager(shot_data=corrected_data_dict[shot], operations=[])
    #operations_manager.run()


    


if __name__ == "__main__":
    main()