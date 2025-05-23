from typing import Dict, Type

from utils.loadmanager.probeloadmanager import ProbeLoadManager
from utils.runmanager.runmanager import RunManager
from utils.opmanager.operationsmanager import OperationsManager
from utils.opmanager.probeoperationsmanager import ProbeOperationsManager

from utils.stats.stats import probe_arrays_stats


class ProbeRunManager(RunManager):

    def __init__(self, input, data_paths_dict):
        super().__init__(input, data_paths_dict)
        self.probe_manager_key : Dict[str, Type[OperationsManager]]= {
            "PROBE":ProbeOperationsManager
        }
    
    def run(self):
        """Executes the run for the RunManager, which encapsulates much of the ugliness of the process."""

        #############################
        # RUN/LOAD MANAGER MATERIAL #
        #############################

        # INTIALIZE THE STARTUP MANAGER, WHICH IS RESPONSIBLE FOR ESSENTIALLY CONVERTING THE
        # DATA_PATHS_DICTIONARY TO DATA_DICTIONARY
        load_manager = ProbeLoadManager(input=self.input, 
                                        data_paths_dict=self.data_paths_dict)
        
        # CALL THE RUNMANAGER.LOAD() METHOD, WHICH RETURNS
        # DICTIONARIES OF FORM {SHOT NO : {"DATA": [], "X": [], "Y": []}} FOR IMAGES
        # AND OF FORM {SHOT NO : { "DATA": { "VOLTAGES":[], "TIMES":[] } } } FOR PROBES
        raw_data_dict, bkg_data_dict, corrected_data_dict = load_manager.load()

        ##############################
        # OPERATION MANAGER MATERIAL #
        ##############################

        print("selecting appropriate data dictionary ... \n")
        data_dict = raw_data_dict

        # Depending on whether we are displaying the background itself or the experimental shot numbers,
        # we need to make sure that the shot numbers are correct.
        shot_nos = self.input["BKG_SHOT_NOS"] if self.input["BACKGROUND_STATUS"] == "SHOW" else self.input["EXP_SHOT_NOS"]
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

            # Assemble list of shot data dictionaries for each of the shots specified.
            data_dict_list = [shot_dict for shot_dict in data_dict.values()]

            mean_data, std_data = probe_arrays_stats(data_dict_list=data_dict_list)
            self._call_operations_manager(
                shot_no=f"Avg. Over Shots {shot_nos}",
                shot_data = mean_data,
                LABEL=LABEL,
                std_data=std_data
            )

    
    
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
        operations_manager = ProbeOperationsManager(
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