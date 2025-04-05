##################################################################################################
# CLASS CONTROLLING THE RUN- IDEA IS TO WRAP ALL DATA COLLECTION INTO A SINGLE RUN_MANAGER CLASS #
##################################################################################################

# MODULE IMPORTS
import sys
import os
from typing import List, Dict

# Add . to path so that the interpreter can find the devices modules.
sys.path.append(os.path.abspath("."))

#Import device and output classes for device object construction
from devices.device import Device
from devices.output import *

#Import builder classes that construct multiple instances of an object for different shots
from run_manager.builders import *

#Import information from configuration file, paths.py, containing the location of all paths to all data.
from run_manager.paths import *

#####################
# RUN MANAGER CLASS #
#####################

class RunManager:
    """Manages the run during data collection."""

    def __init__(self, devices:List[Device], shots, plots):
        """
        
        Parameters
        ----------
            devices : list[Device]
                List of devices that we want to gather diagnostic information from.
            shots : list[int]
                List of shots that we are interested in collecting data for.
            plots : bool
                Boolean determining whether we are interested in plotting/visualizing data during analysis.
        
        """

        # INITIALIZE LIST OF DEVICES WE WANT TO SCRAPE DATA FROM
        self.devices = devices

        # INITIALIZE LIST OF SHOTS FOR WHICH WE ARE INTERESTED IN DATA FROM THESE DEVICES
        self.shots = shots

        # PLOT BOOLEAN- DO WE WANT TO ACTUALLY VISUALIZE THE DATA?
        self.plots = plots

        #  The following might be a bit difficult to understand at first, so take a look at the self.run() function of the RunManager class below,
        # and then come back here to get a better feel for why we need these dictionaries. Broadly, these dictionaries allow us to significantly
        # clean up the self.run() function by allowing us to mostly ignore which specific device is being called as the self.run() function
        # iterates through the self.devices list. Therefore, we don't have to specify whether we need CamBuilder or Probebuilder etc., as these
        # dictionaries below will take a look at the device name at the beginning of self.run(), and then provide us with the appropriate Builder OR 
        # the appropriate paths_dictionary.
        # Remember that the paths_dictionary is the dictionary containing the paths to all data for a specific device across all shots.

        # BUILDER DICTIONARY: 
        self.builder_key : Dict[str, Builder]= {
            "Faraday Probe" : ProbeBuilder,
            "HRM3" : CamBuilder
        }

        # DICTIONARY OF PATHS DICTIONARIES (dictionary squared)
        self.paths_key : Dict[str, Dict[int, str]] = {
            "Faraday Probe" : FP1_efield_data_paths,
            "HRM3" : HRM3_image_data_paths
        }

    
    def run(self):
        """Controls the actions of the RunManager at run time, building appropriate dictionaries of  objects for devices of interest at 
        specified shot numbers."""

        #  ITERATE OVER ALL SPECIFIED DEVICES, AND THEN CALL BUILDER FUNCTIONS TO CONSTRUCT DEVICE OBJECTS AT THE CORRECT
        # SHOT NUMBERS
        for device in self.devices:

            # GET DEVICE NAME AS STRING
            device_name = device

            # CREATE ALIAS "device_builder" FOR THE SPECIFIC DEVICE BUILDER CLASS- this could be CamBuilder or ProbeBuilder, etc.
            device_builder = self.builder_key[device]

            # GET THE DATA PATHS DICTIONARY FOR THE DEVICE- this is the dictionary of the form {SHOT NO : /path/to/device/data/for/shot_no}
            data_paths_dict = self.paths_key[device]

            # CONSTRUCT INSTANCE OF THE DEVICE BUILDER CLASS, e.g. builder_instance = CamBuilder(shots=...)
            builder_instance = device_builder(shots=self.shots, device_name=device_name, data_paths_dict=data_paths_dict)
            
            #  RECEIVE DICTIONARY OF THE DEVICE OBJECTS FOR ALL SPECIFIED SHOTS, FORM {SHOT NO : DEVICE}
            devices_objs = builder_instance.builds() #THIS COULD BE A DICTIONARY OF PROBES AT DIFFERENT SHOTS, OR OF HRM3 CAMS AT DIFFERENT SHOTS

            # IF PLOTS=TRUE, ITERATE OVER DEVICE OBJECTS IN THE devices_obj DICTIONARY AND CALL THE ANALYSIS METHOD
            if self.plots:
                for _, device in devices_objs.items():
                    device.call_analysis()
        


        

        


