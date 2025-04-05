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

        # INITIALIZE LIST OF SHOTS FOR WHICH WE ARE INTERESTED IN FOR THESE DEVICES
        self.shots = shots

        # PLOT BOOLEAN- DO WE WANT TO ACTUALLY VISUALIZE THE DATA?
        self.plots = plots
    
    
    def run(self,):
        """Controls the actions of the RunManager at run time, building appropriate device objects for devices of interest at specified shot numbers."""
        
        if "Faraday Probe" in self.devices:
            
            device_name = "Faraday Probe"

            #! WARNING- THIS HARDCODED DICTIONARY _MUST_ BE REMOVED AT SOME POINT !
            
            # INITIALIZE PROBEBUILDER OBJECT, WHICH CONTROLS CONSTRUCTION OF FARADAY PROBE OBJECTS
            probe_builder = ProbeBuilder(shots=self.shots, device_name=device_name, efield_data_paths=FP1_efield_data_paths)
            
            # GET A DICTIONARY OF FARADAY PROBES OF FORM {SHOT_NO : PROBE OBJECT}
            self.faraday_probes = probe_builder.builds()

            if self.plots:
                for _, faraday_probe in self.faraday_probes.items():
                    faraday_probe.call_analysis()

        if "HRM3" in self.devices:

            # CAM NAME
            camera_name = "HRM3"

            #INITIALIZE CAMERABUILDER OBJECT, WHICH CONTROLS CONSTRUCTION OF HRM3 OBJECTS
            hrm3_builder = CamBuilder(shots=self.shots, camera_name=camera_name, image_data_paths=HRM3_image_data_paths)

            # GET A DICTIONARY OF CAMERAS OF FORM {SHOT_NO : CAMERA OBJECT}
            self.hrm3_cams = hrm3_builder.builds()

            if self.plots:
                for _, hrm3_cam in self.hrm3_cams.items():
                    hrm3_cam.call_analysis()


        

        


