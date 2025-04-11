##################################################################################################
# CLASS CONTROLLING THE RUN- IDEA IS TO WRAP ALL DATA COLLECTION INTO A SINGLE RUN_MANAGER CLASS #
##################################################################################################

# MODULE IMPORTS
import sys
import os
from typing import List, Dict, TYPE_CHECKING

from utils.pathfinder import PathFinder
from utils.builders import Builder

# Add . to path so that the interpreter can find the devices modules.
sys.path.append(os.path.abspath("."))

#####################
# RUN MANAGER CLASS #
#####################

class RunManager:
    """Manages the run during data collection."""

    def __init__(self, devices:List[str], 
                 shots:List[int], 
                 rm_builder_key:Dict[str, Builder], 
                 plots:bool=False):
        """
        
        Parameters
        ----------
            devices : List[str]
                List of names of devices which we want to gather diagnostic information from.
            
            shots : List[int]
                List of shots that we are interested in collecting data for.
            
            rm_builder_key : Dict[Builder, str]
                Dictionary that tells our run manager what builder species to use for each device, format {Device Name : Builder Species}. 
                This is the dictionary that encodes information such as "HRM3 is a camera, and needs a CameraBuilder", or "the Faraday Probe is 
                a type of field probe, and needs a ProbeBuilder".
            
            rm_raw_data_paths_key : Dict[str, Dict[int, str]]
                Dictionary that tells us where the raw data for each shot is 
            
            rm_background_data_paths_key : Dict[str, Dict[int, str]]
            
            plots : bool
                Boolean determining whether we are interested in plotting/visualizing data during analysis.
        
        """

        # INITIALIZE LIST OF DEVICES WE WANT TO SCRAPE DATA FROM
        self.devices = [device.upper() for device in devices]

        # INITIALIZE LIST OF SHOTS FOR WHICH WE ARE INTERESTED IN DATA FROM THESE DEVICES
        self.shots = shots

        # PLOT BOOLEAN- DO WE WANT TO ACTUALLY VISUALIZE THE DATA?
        self.plots = plots

        # Conversion between device name and builder class (i.e. HRM3 and HRM4 both require CamBuilder, Faraday Probe requires ProbeBuilder)
        self.builder_key = rm_builder_key

    
    def configure(self, master_timestamps_path_dict, shot_key):
        """
        Configures the runmanager to have appropriate dictionaries for the background data paths and raw data paths for each device.

        Parameters
        ----------
            master_timestamps_path_dict : Dict
                Dictionary of dictionaries, where the "key" is the device name, and the value is a dictionary containing paths to the
                timestamps .csvs for the raw and background image data.

            shot_key : str 
                Name of the column header (in correct case/spelling) which denotes the shot number in each .csv

        """

        ######################################
        # DATA PATH DICTIONARY CONFIGURATION #
        ######################################

        master_path_dict = {device_name : {} for device_name in self.devices}
        print("Master path dictionary: ", master_path_dict)

        for device_name in self.devices:

            device_name = device_name

            RAW_csv_path = master_timestamps_path_dict[device_name]["RAW_csv_path"]
            BKG_csv_path = master_timestamps_path_dict[device_name]["BKG_csv_path"]

            pathfinder = PathFinder(
                RAW_timestamp_csv_path=RAW_csv_path,
                BKG_timestamp_csv_path=BKG_csv_path,
                device_name=device_name,
                shot_key=shot_key,
                desired_shots=self.shots
            )

            master_path_dict[device_name]["RAW_data_path"] = pathfinder.get_RAW_data_paths_dict()
            master_path_dict[device_name]["BKG_data_path"] = pathfinder.get_BKG_data_paths_dict()

        self.RAW_data_paths_key : Dict[str, Dict[int, str]] = {
            device_name : master_path_dict[device_name]["RAW_data_path"] for device_name in self.devices
        }

        self.BKG_data_paths_key : Dict[str, Dict[int, str]] = {
            device_name : master_path_dict[device_name]["BKG_data_path"] for device_name in self.devices
        }
 

    
    def run(self):
        """Controls the actions of the RunManager at run time, building appropriate dictionaries of  objects for devices of interest at 
        specified shot numbers."""

        #  ITERATE OVER ALL SPECIFIED DEVICES, AND THEN CALL BUILDER FUNCTIONS TO CONSTRUCT DEVICE OBJECTS AT THE CORRECT
        # SHOT NUMBERS
        for device in self.devices:

            # GET DEVICE NAME AS STRING
            device_name = device.upper()

            # CREATE ALIAS "device_builder" FOR THE SPECIFIC DEVICE BUILDER CLASS- this could be CamBuilder or ProbeBuilder, etc.
            device_builder = self.builder_key[device_name]

            # GET THE DATA PATHS DICTIONARY FOR THE DEVICE- this is the dictionary of the form {SHOT NO : /path/to/device/data/for/shot_no}
            RAW_data_paths_dict = self.RAW_data_paths_key[device_name]

            # GET THE DICTIONARY INDEXING THE DIFFERENT TYPES OF BACKGROUND IMAGE FOR THE DEVICE
            BKG_paths_dict = self.BKG_data_paths_key[device_name]

            # CONSTRUCT INSTANCE OF THE DEVICE BUILDER CLASS, e.g. builder_instance = CamBuilder(shots=...)
            builder_instance = device_builder(shots=self.shots, 
                                              device_name=device_name, 
                                              RAW_data_paths_dict=RAW_data_paths_dict, 
                                              BKG_paths_dict=BKG_paths_dict)
            
            #  RECEIVE DICTIONARY OF THE DEVICE OBJECTS FOR ALL SPECIFIED SHOTS, FORM {SHOT NO : DEVICE}
            devices_objs = builder_instance.build_devices() #THIS COULD BE A DICTIONARY OF PROBES AT DIFFERENT SHOTS, OR OF HRM3 CAMS AT DIFFERENT SHOTS

            # IF PLOTS=TRUE, ITERATE OVER DEVICE OBJECTS IN THE devices_obj DICTIONARY AND CALL THE ANALYSIS METHOD
            if self.plots:
                for _, device in devices_objs.items():
                    device.call_analysis()
        


        

        


