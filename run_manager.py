from typing import Dict, Type

from startupmanager import StartupManager
from operationsmanager import OperationsManager, AndorImageManager, DigicamImageManager, OrcaImageManager, ProbeManager

class RunManager:
    """Class responsible for the first (and essentially highest) level of encapsulation during execution of the code.
    This allows us to wrap all of the ugly details of the run into a single funtion, the .run() method of the RunManager class."""

    def __init__(self, input:Dict, data_paths_dict):
        """
        Parameters
        ----------
            input : Dict
                Dictionary of input settings, which was previously supplied from a .json configuration file and converted
                into a Python dictionary before being passed here.
            data_paths_dict : Dict[int, str]
                Data paths dictionary, where the keys are the shot numbers, and the values are the paths to the data for that shot.
        """

        #INPUT DICTIONARY FROM .JSON FILE
        self.input = input

        #DICTIONARY OF FORM {SHOT NO : /PATH/TO/DATA}
        self.data_paths_dict = data_paths_dict
    
    def run(self):
        #############################
        # RUN/LOAD MANAGER MATERIAL #
        #############################

        # INTIALIZE THE STARTUP MANAGER, WHICH IS RESPONSIBLE FOR ESSENTIALLY CONVERTING THE
        # DATA_PATHS_DICTIONARY TO DATA_DICTIONARY
        startup_manager = StartupManager(input=self.input, 
                                        data_paths_dict=self.data_paths_dict)
        
        # CALL THE RUNMANAGER.LOAD() METHOD, WHICH RETURNS
        # DICTIONARIES OF FORM {SHOT NO : {"DATA": [], "X": [], "Y": []}} FOR IMAGES
        # AND OF FORM {SHOT NO : { "DATA": { "VOLTAGES":[], "TIMES":[] } } } FOR PROBES
        raw_data_dict, bkg_data_dict, corrected_data_dict = startup_manager.load()

        ##############################
        # OPERATION MANAGER MATERIAL #
        ##############################
        
        # BELOW, ALLOWS US TO CALL ARBITRARY "OPERATIONS MANAGER", AND THEN
        # HAVE THE PROGRAM SELECT THE APPROPRIATE SUBCLASS FOR US WITHOUT
        # HAVING TO LOOK UNDER-THE-HOOD
        manager_key : Dict[str, Type[OperationsManager]] = {
            "CAMERA": {"DIGICAM": DigicamImageManager, "ANDOR": AndorImageManager, "ORCA": OrcaImageManager}, 
            "PROBE": {"PROBE": ProbeManager}
        }

        # EXTRACT THE SUB-DICTIONARY FROM THE INPUT DICTIONARY, WHICH SPECIFIES THE TYPES
        # OF OPERATIONS WHICH WE WANT TO PERFORM.
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
            operations_manager = manager_key[self.input["DEVICE_TYPE"]][self.input["DEVICE_SPECIES"]](
                DEVICE_NAME=self.input["DEVICE_NAME"],
                shot_no=shot_no,
                label=LABEL,
                shot_data=data_dict[shot_no]) 
            if operations["LINEOUT"]:
                if self.input["DEVICE_TYPE"] == "CAMERA":
                    operations_manager.lineouts(axis=operations["LINEOUT_AXIS"], ft_interp=operations["LINEOUT_FT_INTERP"])
                else:
                    raise NotImplementedError("Warning: no lineout method provided for probes!")
            if operations["PLOT"]:
                operations_manager.plot()

            if operations["CHROMOX_FIT"]:
                operations_manager.chromox_fit()
        
        # SHOT AVERAGING
        if operations["AVERAGE_SHOTS"]:
             shot_data_list = [data for data in data_dict.values()]
             averaged_shot_data = operations_manager.average_shots(shot_data_list, shot_nos)

        for shot_no in shot_nos:
            operations_manager = manager_key[self.input["DEVICE_TYPE"]][self.input["DEVICE_SPECIES"]](
                DEVICE_NAME=self.input["DEVICE_NAME"],
                shot_no=f"Average Over {shot_data_list}",
                label=LABEL,
                shot_data=averaged_shot_data) 
            if operations["LINEOUT"]:
                if self.input["DEVICE_TYPE"] == "CAMERA":
                    operations_manager.lineouts(axis=operations["LINEOUT_AXIS"], ft_interp=operations["LINEOUT_FT_INTERP"])
                else:
                    raise NotImplementedError("Warning: no lineout method provided for probes!")
            if operations["PLOT"]:
                operations_manager.plot()

            if operations["CHROMOX_FIT"]:
                operations_manager.chromox_fit()
            
        