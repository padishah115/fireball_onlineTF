#External imports
import logging
logger=logging.getLogger(__name__)

# pathmanager imports
from utils.pathmanager.pathmanager import PathManager

# runmanager imports
from utils.runmanager.runmanager import RunManager
from utils.runmanager.camrunmanager import CamRunManager 
from utils.runmanager.proberunmanager import ProbeRunManager
from utils.runmanager.temprunmanager import TempRunManager
from utils.runmanager.ldvrunmanager import LDVRunManager


def main(input):
    """Main function that executes the run.
    
    Parameters
    ----------
        input : dict
            Input configuration information, passed as a dictionary.
    """

    ################
    # PATH LOADING #
    ################
    path_manager = PathManager(input=input)
    paths_dict = path_manager.get_paths_dict()

    #######
    # RUN #
    #######
    logger.info("Starting runs...") 
    # Initialise the runmanager as appropriate for each device.
    runmanagerdict : dict[str, type[RunManager]]= {
        "PROBE":ProbeRunManager, 
        "CAMERA": CamRunManager,
        "PT100": TempRunManager,
        "LDV": LDVRunManager,
    }
    
    # INITIALIZE THE APPROPRIATE RUN MANAGER
    run_manager = runmanagerdict[input["DEVICE_TYPE"]](
        input=input, # input configuration
        #data_paths_dict=data_paths_dict # select appropriate dictionary from the dict_of_dicts variable.
        data_paths_dict=paths_dict
    )

    #Execute the run.
    run_manager.run()
    logger.info("Run terminated successfully without errors. \n")