#import homebrewed packages
from device import *

#################################################################
# RUN MANAGER CLASS WHICH CONTROLS THE EXECUTION OF THE PROGRAM #
#################################################################

class RunManager:
    """RunManager Class which encapsulates the nitty-grittiness of the program's execution, allowing a large 
    amount of encapsulation."""

    def __init__(self, device_name:str, shot_data_path_dict:Dict[str, str], operation:List[str]):
        """
        
        Parameters
        ----------
            device_name : str
                Device whose data we are interested in.
            shot_data_path_dict : Dict[str:str]
                Dictionary containing shot numbers as keys and data paths as values.
            operation : str
                Which operation we would like to perform on the data.
        """
        
        # NAMES OF DEVICE WHOSE DATA WE WANT TO SCRAPE THROUGH
        self.device_name = device_name

        # WHICH SHOT NUMBERS WE ARE INTERESTED IN
        self.shot_data_path_dict = shot_data_path_dict

        # WHICH OPERATIONS WE WOULD LIKE TO PERFORM WITH THE SHOT DATA
        self.operation = operation

        # UPDATED FORM OF "BUILDER" DICTIONARY
        # !!!HARDCODED!!!
        # AT RUNTIME, SET A KEY TELLING US WHICH TYPE OF DEVICE
        #  SUBCLASS TO BUILD FOR EACH DIAGNOSTIC
        self.device_dict : Dict[str, Device] = {

            # E AND B FIELD DIAGNOSTICS
            "BDOT PROBE 1": Probe,
            "BDOT PROBE 2": Probe,
            "FARADAY PROBE": Probe,

            # UP AND DOWNSTREAM CAMERAS
            "CAM3": ChromoxCamera,
            "CAM4": ChromoxCamera,

            # STREAK CAMERA
            "STREAK CAMERA": StreakCamera,

            # SYNCHROTRON CAMERA
            "SYNCHROTRON CAMERA": SynchroCamera,

            #SPECTROMETER CAMERAS
            "CAM5": PairSpecCamera,
            "CAM6": PairSpecCamera


        }
        
        pass

    def run(self):
        """Function responsible for executing the program run, encapsulating much of the 
        grim details."""

        # GENERATE PATHS TO ALL RELEVANT SHOTS FOR THE DEVICE NAME

        # USE THE DEVICE_DICT TO FIND THE APPROPRIATE DEVICE OBJECT THAT WE WANT TO BUILD
        device_class = self.device_dict[self.device_name]

        # CREATE INSTANCE OF THE DEVICE
        device_instance : Device = device_class(
            device_name = self.device_name,
            shot_data_path_dict = self.shot_data_path_dict
        )

        device_instance.run_operation(operation=self.operation)