import logging
logger = logging.getLogger(__name__)
import numpy as np

from utils.loadmanager.probeloadmanager import ProbeLoadManager
from utils.runmanager.runmanager import RunManager
from utils.opmanager.operationsmanager import OperationsManager
from utils.opmanager.probeoperationsmanager import ProbeOperationsManager

from utils.stats.stats import probe_arrays_stats


class ProbeRunManager(RunManager):

    def __init__(self, input, data_paths_dict):
        super().__init__(input, data_paths_dict)
        self.probe_manager_key : dict[str, type[OperationsManager]]= {
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
        raw_data_dict, corrected_data_dict, std_bkg = load_manager.load()

        ##############################
        # OPERATION MANAGER MATERIAL #
        ##############################

        logger.info("Selecting appropriate data dictionary ... \n")
        data_dict = raw_data_dict if self.input["BACKGROUND_STATUS"] == "RAW" else corrected_data_dict
        LABEL = f"Bkg status: {self.input['BACKGROUND_STATUS']}"
        

        # Depending on whether we are displaying the background itself or the experimental shot numbers,
        # we need to make sure that the shot numbers are correct.
        shot_nos = self.input["EXP_SHOT_NOS"]

        
        # SINGLE-SHOT PROCESSING- go one-by-one through the shots
        if self.operations["SHOW_SINGLESHOT_PLOTS"]:
            for shot_no in shot_nos:
                self._call_operations_manager(
                    shot_no=shot_no,
                    shot_data=data_dict[shot_no],
                    std_data=data_dict[shot_no]["ERROR"],
                    LABEL=LABEL
                )

        # CHECK TO SEE WHETHER WE WANT AVERAGE SHOT PROCESSING
        if self.operations["SHOW_AVERAGE_SHOTS"]:

            raw_data_dict_list = [shot_dict for shot_dict in raw_data_dict.values()]
            std_raw = probe_arrays_stats(raw_data_dict_list)[1]

            # ERROR PROPAGATION
            if self.background_status == "SUBTRACT":
                channel_nos = std_raw["DATA"]["VOLTAGES"].keys()
                std_data = {"DATA":{"VOLTAGES":{channel_no:None for channel_no in channel_nos}}}
                
                for channel_no in channel_nos:
                    raw_sigma = std_raw["DATA"]["VOLTAGES"][channel_no]
                    bkg_sigma = std_bkg["DATA"]["VOLTAGES"][channel_no]
                    std_data["DATA"]["VOLTAGES"][channel_no] = np.sqrt(np.power(raw_sigma, 2) + np.power(bkg_sigma, 2))
                
                
                data_dict_list = [shot_dict for shot_dict in corrected_data_dict.values()]

            if self.background_status == "RAW":
                std_data = std_raw
                data_dict_list = [shot_dict for shot_dict in raw_data_dict.values()]

            mean_data = probe_arrays_stats(data_dict_list=data_dict_list)[0]
            self._call_operations_manager(
                shot_no=f"Avg. Over Shots {shot_nos}",
                shot_data=mean_data,
                std_data=std_data,
                LABEL=LABEL
            )
    
    
    def _call_operations_manager(self, shot_no, shot_data, LABEL=None, std_data=None):
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
            input=self.input,
            cache_path=self.input["SCOPECACHE_PATH"]
        ) 

        # PLOTTING        
        logger.info("Plot ... \n")
        operations_manager.plot(norm=self.input["NORM_PLOT"])

        


