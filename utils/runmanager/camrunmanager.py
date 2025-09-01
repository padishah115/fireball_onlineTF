from typing import Dict, Type

from utils.runmanager.runmanager import RunManager
from utils.loadmanager.camloadmanager import CamLoadManager
from utils.opmanager.operationsmanager import OperationsManager
from utils.opmanager.imageoperationsmanager import *
from utils.stats.stats import img_arrays_stats
import logging
logger = logging.getLogger(__name__)

class CamRunManager(RunManager):
    
    def __init__(self, input, data_paths_dict):
        super().__init__(input, data_paths_dict)
        
        # BELOW, ALLOWS US TO CALL ARBITRARY "OPERATIONS MANAGER", AND THEN
        # HAVE THE PROGRAM SELECT THE APPROPRIATE SUBCLASS FOR US 
        self.cam_manager_key : Dict[str, Type[OperationsManager]] = {
            "DIGICAM": DigicamImageManager, "ANDOR": AndorImageManager, "ORCA": OrcaImageManager, 
        }

    def run(self):
        """Executes the run for the RunManager, which encapsulates much of the ugliness of the process."""

        #############################
        # RUN/LOAD MANAGER MATERIAL #
        #############################

        # INTIALIZE THE STARTUP MANAGER, WHICH IS RESPONSIBLE FOR ESSENTIALLY CONVERTING THE
        # DATA_PATHS_DICTIONARY TO DATA_DICTIONARY
        load_manager = CamLoadManager(input=self.input, 
                                        data_paths_dict=self.data_paths_dict)

        # Labels for cameras
        #SUBTRACT BACKGROUND
        if self.background_status == "SUBTRACT":
            if not self.input["BKG_SHOT_NOS"]:
                raise ValueError("Error: requested background-subtraction, but did not specify any background shots.")
            LABEL = f"{self.input['BKG_NAME']}-SUBTRACTED"
        
        #PLOT RAW IMAGE ONLY (NO BACKGROUND SUBTRACTION)
        elif self.background_status == "RAW":
            if not self.input["EXP_SHOT_NOS"]:
                raise ValueError("Error: no experimental shots provided for raw data plotting.")
            LABEL = f"Raw (no background correction)"
        
        
        else:
            raise ValueError(f"Warning: {self.input['BACKGROUND_STATUS']} is invalid input for\
                            \"BACKGROUND_STATUS\" in input.json file.")
        
        
        raw_data_dict, corrected_data_dict, std_bkg = load_manager.load()

        ##############################
        # OPERATION MANAGER MATERIAL #
        ##############################

        #DICTIONARY THAT CAN HELP US CLEAN UP THE RUNMANAGER CODE
        data_type_key : Dict[str, Dict] = {
            "SUBTRACT":corrected_data_dict,
            "RAW": raw_data_dict,
        }

        #  SELECT CORRECT DICTIONARY BASED ON SPECIFIED BACKGROUND REMOVAL STATUS
        logger.info("Selecting appropriate data dictionary ... \n")
        data_dict = data_type_key[self.input["BACKGROUND_STATUS"]]

        # Depending on whether we are displaying the background itself or the experimental shot numbers,
        # we need to make sure that the shot numbers are correct.
        shot_nos = self.input["EXP_SHOT_NOS"]

        
        ##########################
        # SINGLE-SHOT PROCESSING #
        ##########################
        if self.operations["SHOW_SINGLESHOT_PLOTS"]:
            for shot_no in shot_nos:
                shot_data = {0:None}
                shot_data[0] = data_dict[shot_no]
                shot_data["N"] = 1
                self._call_operations_manager(
                    shot_no=shot_no,
                    shot_data=shot_data,
                    LABEL=LABEL,
                )


        ###########################
        # AVERAGE SHOT PROCESSING #
        ###########################
        # CHECK TO SEE WHETHER WE WANT AVERAGE SHOT PROCESSING
        if self.operations["SHOW_AVERAGE_SHOTS"]:

            N = len(raw_data_dict.values())
            shot_data = {i:array for i, (_, array) in enumerate(raw_data_dict.items())}
            shot_data["N"] = N

            self._call_operations_manager(
                shot_no=f"Avg. Over Shots {shot_nos}",
                shot_data=shot_data,
                LABEL=LABEL,
            )
    
    def _call_operations_manager(self, shot_no, shot_data, LABEL):
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
        """
        
        # INITIALIZE THE CORRECT OPERATIONS MANAGER USING THE MANAGER_KEY DICTIONARY
        operations_manager = self.cam_manager_key[self.input["DEVICE_SPECIES"]](
            DEVICE_NAME=self.input["DEVICE_NAME"],
            shot_no=shot_no,
            label=LABEL,
            shot_data=shot_data,
            input=self.input
        ) 

        # PLOTTING        
        logger.info("Plot ... \n")
        operations_manager.plot()