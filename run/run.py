from config.device_info import device_info
# build a logger! you know you want to!
import logging
logging.basicConfig(filename="log.log", level=logging.INFO)
logger = logging.getLogger(__name__)

#External imports
import logging
logger=logging.getLogger(__name__)

# pathmanager imports
from utils.pathmanager.pathmanager import PathManager

# runmanager imports
from utils.runmanager.runmanager import RunManager
from utils.runmanager.camrunmanager import CamRunManager 
from utils.runmanager.proberunmanager import ProbeRunManager


class run():

    def __init__(self, device_name, input):
        """Initialisation function for the run class.
        
        Parameters
        ----------
            device_name : str
                The name of the device, passed as a string, for whom we want to call analysis.
            input : dict
                Input configuration settings, passed as a dictionary.
        """
        
        self.device_name = device_name
        self.input = input
        


    def display_device(self):
        """Function for displaying analysis from a single device."""
    
        ##################################################################################
        # Device-specific information to be added to the input configuration dictionary. #
        ##################################################################################
        self.input["DEVICE_NAME"] = self.device_name
        self.input["DEVICE_TYPE"] = device_info["TYPE"][self.device_name]
        self.input["DEVICE_SPECIES"] = device_info["SPECIES"][self.device_name]
    
        logger.info("Starting runtime ... \n")
        self.device_run()
        logger.info("Ending runtime ...\n")

    
    def device_run(self):
        """Main function that executes the run."""

        ################
        # PATH LOADING #
        ################
        path_manager = PathManager(input=self.input)
        paths_dict = path_manager.get_paths_dict()
    
        #######
        # RUN #
        #######
        logger.info("Starting runs...") 
        # Initialise the runmanager as appropriate for each device.
        runmanagerdict : dict[str, type[RunManager]]= {
            "PROBE":ProbeRunManager, 
            "CAMERA": CamRunManager,
        }
        
        # INITIALIZE THE APPROPRIATE RUN MANAGER
        run_manager = runmanagerdict[self.input["DEVICE_TYPE"]](
            input=self.input, # input configuration
            #data_paths_dict=data_paths_dict # select appropriate dictionary from the dict_of_dicts variable.
            data_paths_dict=paths_dict
        )
    
        #Execute the run.
        run_manager.run()
        logger.info("Run terminated successfully without errors. \n")