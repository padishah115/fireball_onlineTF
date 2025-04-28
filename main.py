#MODULE IMPORTS
import sys
import json
sys.path.append(".")

from run_manager import RunManager

def main(json_path="./input.json"):
    
    with open(json_path) as jsfile:
        input = json.load(jsfile)


    # SOMEHOW BUILD THE DATA PATHS DICT
    # FOR NOW HARDCODED
    digicam3_paths_dict = {
        1:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
        2:"./example_data/data/HRM3.DigiCam_OD0_1714383312791697_1714383306135000.csv",
        3:"./example_data/data/HRM3.DigiCam_OD1_1714604587992043_1714604581335000.csv",
        4:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv",
    }

    andor_paths_dict = {
        1:'./example_data/data/andor.asc'
    }

    orca_paths_dict = {
        1:'./example_data/data/1ns_test.dac'
    }

    probe_paths_dict = {
        1:"./example_data/data/C1--XX_SCOPE2--00081.csv"
    }

    print("Starting run manager ... \n")
    run_manager = RunManager(
        input=input,
        data_paths_dict=orca_paths_dict
    )

    run_manager.run()
        


if __name__ == "__main__":
    main()