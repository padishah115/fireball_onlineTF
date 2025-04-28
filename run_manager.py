from typing import Dict, Type, List
import numpy as np

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

        #DICTIONARY THAT CAN HELP US CLEAN UP THE RUNMANAGER CODE
        data_type_key : Dict[str, Dict] = {
            "SUBTRACT":corrected_data_dict,
            "RAW": raw_data_dict,
            "SHOW": bkg_data_dict
        }


        print("selecting appropriate data dictionary ... \n")
        data_dict = data_type_key[self.input["BACKGROUND_STATUS"]]
        shot_nos = self.input["BKG_SHOT_NOS"] if self.input["BACKGROUND_STATUS"] == "SHOW" else self.input["EXP_SHOT_NOS"]

        #SUBTRACT BACKGROUND
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

        # SINGLE-SHOT PROCESSING
        for shot_no in shot_nos:
            self._call_operations_manager(
                shot_no=shot_no,
                shot_data=data_dict[shot_no],
                LABEL=LABEL
            )
        
        # SHOT AVERAGING
        if self.operations["AVERAGE_SHOTS"]:

            # COPY X AND Y AXES FROM ONE OF THE CONSTITUENT SHOTS' DATA
            # TO ENSURE CORRECT FORMATTING
            X = data_dict[shot_no]["X"]
            Y = data_dict[shot_no]["Y"]

            # PERFORM THE AVERAGING OPERATION OVER THE SHOTS, GETTING A DICTIONARY OF SHOT DATA
            averaged_shot_data = self._get_shot_averaged_data(data_dict=data_dict, X=X, Y=Y)
            
            # CALL AN OPERATIONS MANAGER ON THE AVERAGED DATA.
            self._call_operations_manager(shot_no=f"Average over {shot_nos}",
                                            shot_data=averaged_shot_data,
                                            LABEL=LABEL)

    
    def _call_operations_manager(self, shot_no, shot_data, LABEL):
        """Helper function to wrap up the operations manager clauses in the .run() method.
        
        Parameters
        ----------
            shot_no : int
                The shot number whose data we are processing
            shot_data : np.ndarray
                The shot data itself in processed form.
            LABEL : str
                Extra detail about the nature of processing which the data has undergone.
        """
        
        # INITIALIZE THE CORRECT OPERATIONS MANAGER USING THE MANAGER_KEY DICTIONARY
        operations_manager = self.manager_key[self.input["DEVICE_TYPE"]][self.input["DEVICE_SPECIES"]](
            DEVICE_NAME=self.input["DEVICE_NAME"],
            shot_no=shot_no,
            label=LABEL,
            shot_data=shot_data) 
        
        # CHECK TO SEE WHICH OPERATIONS WE WANT TO GET THE OPERATIONS MANAGER TO PERFORM
        # LINEOUTS
        
        if self.operations["LINEOUT"]:
                print("Lineout ... \n")
                if self.input["DEVICE_TYPE"] == "CAMERA":
                    operations_manager.lineouts(axis=self.operations["LINEOUT_AXIS"], ft_interp=self.operations["LINEOUT_FT_INTERP"])
                else:
                    raise NotImplementedError("Warning: no lineout method provided for probes!")
        # PLOTTING
        
        if self.operations["PLOT"]:
            print("Plot .. \n")
            operations_manager.plot()
        # CHROMOX FITTING, IF THE CAMERA IS IMAGING CHROMOX
        
        if self.input["DEVICE_SPECIES"] == "DIGICAM":
            if self.operations["CHROMOX_FIT"]:
                print("CHROMOX fit ... \n")
                operations_manager.chromox_fit()

        
    
    def _get_shot_averaged_data(self, data_dict:Dict, X:np.ndarray, Y:np.ndarray):
        """Returns a dictionary of form {"DATA" : [], "X" : [], "Y" : []} for the averaged shot data.
        
        Parameters
        ----------
            data_dict : Dict
                Dictionary of data over which the average is to be performed. The dictionary will
                be of form {SHOT NO : {"DATA": [], "X":[], "Y":[]}}
            X : np.ndarray
                X axis array formatted in correct units.
            Y : np.ndarray
                Y axis array formatted in correct units.

        Returns
        -------
            averaged_shot_data : Dict
                Dictionary of form {"DATA":[], "X":[], "Y":[]} for the averaged shot data.
        """

        averaged_shot_data = {}
        shot_data_list = [data for data in data_dict.values()]

        #GET THE AVERAGED DATA ITSELF
        averaged_shot_data["DATA"] =\
            self.manager_key[self.input["DEVICE_TYPE"]][self.input["DEVICE_SPECIES"]].average_shots(shot_data_list)
        
        # COPY X AND Y AXES FROM INDIVIDUAL SHOTS
        averaged_shot_data["X"] = X
        averaged_shot_data["Y"] = Y

        return averaged_shot_data
            
        