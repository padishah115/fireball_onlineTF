from typing import Dict

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
    
    def run(self):
        """Executes the run for the RunManager, which encapsulates much of the ugliness of the process."""
        raise NotImplementedError(f"Error: no run method implemented for {self}")
    

