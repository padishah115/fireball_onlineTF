# module imports
import json

# homebrew imports
from run_manager import RunManager

def main(input_json_path='./input.json'):
      
    # LOAD USER-INPUTTED CONFIGURATION FILE
    with open(input_json_path) as js:
        config = json.load(js)
      
    # LOAD CONFIGUARATION INFORMATION FROM .JSON OBJECT
    device = config['DEVICE'] #DEVICES WE ARE INTERESTED IN
    shots = config['SHOTS'] #SHOTS WE ARE INTERESTED IN
    operation = config['OPERATION'] #OPERATIONS WHICH WE WANT TO PERFORM ON DATA

    #GENERATE SHOT_DATA_PATH_DICT FROM DEVICE NAME AND SHOT NUMBERS

    # EXECUTE THE RUN! ('press play')
    myRunManager = RunManager(
        device_name=device,
        shot_data_path_dict={1:"./example_data/data/BG_HRM3.DigiCam_OD0_1714407435191489_1714407428535000.csv"},
        operation=operation
    )
    myRunManager.run()


if __name__ == "__main__":
    main()