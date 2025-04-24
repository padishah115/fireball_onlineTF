from typing import Dict, Type

from startupmanager import StartupManager
from operationsmanager import OperationsManager, ImageManager, ProbeManager

class RunManager:

    def __init__(self, input, data_paths_dict):
        self.input = input
        self.data_paths_dict = data_paths_dict
    
    def run(self):
        #############################
        # RUN/LOAD MANAGER MATERIAL #
        #############################

        startup_manager = StartupManager(device_type=self.input["DEVICE_TYPE"], 
                                        exp_shot_nos=self.input["EXP_SHOT_NOS"], 
                                        bkg_shot_nos=self.input["BKG_SHOT_NOS"], 
                                        data_paths_dict=self.data_paths_dict)
        
        raw_data_dict, bkg_data_dict, corrected_data_dict = startup_manager.load()

        ##############################
        # OPERATION MANAGER MATERIAL #
        ##############################
        manager_key : Dict[str, Type[OperationsManager]] = {
            "CAMERA": ImageManager, 
            "PROBE": ProbeManager
        }

        operations = self.input["OPERATIONS"]

        #SUBTRACT BACKGROUND
        if self.input["BACKGROUND_STATUS"] == "SUBTRACT":
            LABEL = f"{self.input['BKG_NAME']}-SUBTRACTED"
            data_dict = corrected_data_dict
            shot_nos = self.input["EXP_SHOT_NOS"]
        
        #PLOT RAW IMAGE ONLY (NO BACKGROUND SUBTRACTION)
        elif self.input["BACKGROUND_STATUS"] == "RAW":
            LABEL = f"Raw (no background correction)"
            data_dict = raw_data_dict
            shot_nos = self.input["EXP_SHOT_NOS"]
        
        #SHOW BACKGROUND IMAGE ITSELF
        elif self.input["BACKGROUND_STATUS"] == "SHOW":
            LABEL = f"{self.input['BKG_NAME']} BACKGROUND"
            data_dict = bkg_data_dict
            shot_nos = self.input["BKG_SHOT_NOS"]
        
        else:
            raise ValueError(f"Warning: {self.input['BACKGROUND_STATUS']} is invalid input for\
                              \"BACKGROUND_STATUS\" in input.json file.")

        for shot_no in shot_nos:
            operations_manager = manager_key[self.input["DEVICE_TYPE"]](
                DEVICE_NAME=self.input["DEVICE_NAME"],
                shot_no=shot_no,
                label=LABEL,
                shot_data=data_dict[shot_no]) 
            if operations["LINEOUT"]:
                if self.input["DEVICE_TYPE"] == "CAMERA":
                    operations_manager.lineouts(axis=operations["LINEOUT_AXIS"], ft_interp=operations["LINEOUT_FT_INTERP"])
                else:
                    raise NotImplementedError("Warning: no lineout method provided for probes!")
            if self.input["OPERATIONS"]["PLOT"]:
                operations_manager.plot()
        
        if operations["AVERAGE_SHOTS"]:
             shot_data_list = [data for data in data_dict.values()]
             operations_manager.average_shots(shot_data_list, shot_nos)