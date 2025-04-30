from typing import Dict, Type, List
import numpy as np

from utils.loadmanager.loadmanager import LoadManager
from utils.opmanager.operationsmanager import OperationsManager
from utils.opmanager.im_op import *
from utils.opmanager.probe_op import *
from utils.stats.stats import img_arrays_stats

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
        # EXTRACT THE SUB-DICTIONARY FROM THE INPUT DICTIONARY, WHICH SPECIFIES THE TYPES
        # OF OPERATIONS WHICH WE WANT TO PERFORM.
        self.operations = self.input["OPERATIONS"]

        self.background_status = self.input["BACKGROUND_STATUS"]

        #DICTIONARY OF FORM {SHOT NO : /PATH/TO/DATA}
        self.data_paths_dict = data_paths_dict

        # BELOW, ALLOWS US TO CALL ARBITRARY "OPERATIONS MANAGER", AND THEN
        # HAVE THE PROGRAM SELECT THE APPROPRIATE SUBCLASS FOR US WITHOUT
        # HAVING TO LOOK UNDER-THE-HOOD
        self.manager_key : Dict[str, Type[OperationsManager]] = {
            "CAMERA": {"DIGICAM": DigicamImageManager, "ANDOR": AndorImageManager, "ORCA": OrcaImageManager}, 
            "PROBE": {"PROBE": ProbeManager}
        }
    
    def run(self):
        """Executes the run for the RunManager, which encapsulates much of the ugliness of the process."""

        #############################
        # RUN/LOAD MANAGER MATERIAL #
        #############################

        # INTIALIZE THE STARTUP MANAGER, WHICH IS RESPONSIBLE FOR ESSENTIALLY CONVERTING THE
        # DATA_PATHS_DICTIONARY TO DATA_DICTIONARY
        startup_manager = LoadManager(input=self.input, 
                                        data_paths_dict=self.data_paths_dict)
        
        # CALL THE RUNMANAGER.LOAD() METHOD, WHICH RETURNS
        # DICTIONARIES OF FORM {SHOT NO : {"DATA": [], "X": [], "Y": []}} FOR IMAGES
        # AND OF FORM {SHOT NO : { "DATA": { "VOLTAGES":[], "TIMES":[] } } } FOR PROBES
        raw_data_dict, bkg_data_dict, corrected_data_dict = startup_manager.load()

        ##############################
        # OPERATION MANAGER MATERIAL #
        ##############################

        #DICTIONARY THAT CAN HELP US CLEAN UP THE RUNMANAGER CODE
        data_type_key : Dict[str, Dict] = {
            "SUBTRACT":corrected_data_dict,
            "RAW": raw_data_dict,
            "SHOW": bkg_data_dict
        }


        print("selecting appropriate data dictionary ... \n")
        data_dict = data_type_key[self.input["BACKGROUND_STATUS"]] \
            if self.input["DEVICE_TYPE"] == "CAMERA"\
            else raw_data_dict
        
        print(data_dict)

        # Depending on whether we are displaying the background itself or the experimental shot numbers,
        # we need to make sure that the shot numbers are correct.
        shot_nos = self.input["BKG_SHOT_NOS"] if self.input["BACKGROUND_STATUS"] == "SHOW" else self.input["EXP_SHOT_NOS"]

        # Labels for cameras
        #SUBTRACT BACKGROUND
        if self.input["DEVICE_TYPE"] == "CAMERA":
            if self.background_status == "SUBTRACT":
                LABEL = f"{self.input['BKG_NAME']}-SUBTRACTED"
            
            #PLOT RAW IMAGE ONLY (NO BACKGROUND SUBTRACTION)
            elif self.background_status == "RAW":
                LABEL = f"Raw (no background correction)"
            
            #SHOW BACKGROUND IMAGE ITSELF
            elif self.background_status == "SHOW":
                LABEL = f"{self.input['BKG_NAME']} BACKGROUND"
            
            else:
                raise ValueError(f"Warning: {self.input['BACKGROUND_STATUS']} is invalid input for\
                                \"BACKGROUND_STATUS\" in input.json file.")
            
        # If probe, labels are unimportant
        else:
            LABEL = None

        
        # SINGLE-SHOT PROCESSING- go one-by-one through the shots
        if self.operations["SHOW_SINGLESHOT_PLOTS"]:
            for shot_no in shot_nos:
                self._call_operations_manager(
                    shot_no=shot_no,
                    shot_data=data_dict[shot_no],
                    LABEL=LABEL,
                )


        # CHECK TO SEE WHETHER WE WANT AVERAGE SHOT PROCESSING
        if self.operations["SHOW_AVERAGE_SHOTS"]:
            
            # CAMERA IMAGES AVERAGING
            if self.input["DEVICE_TYPE"] == "CAMERA":
                data_dict_list =[array for array in data_dict.values()]
                #print("First data_dict_list entry", data_dict_list[0])

                #Returns two dictionarys of form {"DATA":, "X":, "Y":,}
                mean_data, std_data = img_arrays_stats(data_dict_list=data_dict_list)
                #print("Mean data shape", mean_data["DATA"].shape)
                self._call_operations_manager(
                    shot_no=f"Avg. Over Shots {shot_nos}",
                    shot_data=mean_data,
                    LABEL=LABEL,
                    std_data=std_data,
                )
                pass

            # PROBE AVERAGING
            if self.input["DEVICE_TYPE"] == "PROBE":
                #average_data = probemanager.get_averages(shot_nos, shot_data)
                pass

    
    
    def _call_operations_manager(self, shot_no, shot_data, LABEL, std_data=None):
        """Helper function to wrap up the operations manager clauses in the .run() method for 
        processing shots one at a time.
        
        Parameters
        ----------
            shot_no : int
                The shot number whose data we are processing
            shot_data : Dict[np.ndarray]
                The shot data itself in processed form.
            LABEL : str
                Extra detail about the nature of processing which the data has undergone.
            input : Dict
                Input configuration dictionary
            std_data : Dict[np.ndarray]
                By default, none- useful for ensembles.
        """
        
        # INITIALIZE THE CORRECT OPERATIONS MANAGER USING THE MANAGER_KEY DICTIONARY
        operations_manager = self.manager_key[self.input["DEVICE_TYPE"]][self.input["DEVICE_SPECIES"]](
            DEVICE_NAME=self.input["DEVICE_NAME"],
            shot_no=shot_no,
            label=LABEL,
            shot_data=shot_data,
            std_data=std_data,
            input=self.input
        ) 

        
        # PLOTTING        
        print("Plot ... \n")
        operations_manager.plot(norm=self.input["NORM_PLOT"])
        # CHROMOX FITTING, IF THE CAMERA IS IMAGING CHROMOX
        

    def _call_operations_manager_avgshot():
        pass
        
            
        