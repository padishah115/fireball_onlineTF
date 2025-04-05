##################################################################################################
# CLASS CONTROLLING THE RUN- IDEA IS TO WRAP ALL DATA COLLECTION INTO A SINGLE RUN_MANAGER CLASS #
##################################################################################################

# MODULE IMPORTS
import sys
import os

# Add devices module to path
sys.path.append(os.path.abspath("."))

from typing import List, Dict

from run_manager.constructors import *

from devices.device import Device
from devices.output import *

#####################
# RUN MANAGER CLASS #
#####################

class RunManager:
    """Manages the run during data collection."""

    def __init__(self, devices:list[Device], shots, plots):
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
            
            #! WARNING- THIS HARDCODED DICTIONARY _MUST_ BE REMOVED AT SOME POINT !
            efield_data_paths = {
                1:"./example_data/C1--XX_SCOPE2--00081.csv",
                2:"./example_data/C1--XX_SCOPE2--00081.csv",
                4:"./example_data/C1--XX_SCOPE2--00081.csv"
            }
            # INITIALIZE PROBEBUILDER OBJECT, WHICH CONTROLS CONSTRUCTION OF FARADAY PROBE OBJECTS
            pbuilder = ProbeBuilder(shots=self.shots, efield_data_paths=efield_data_paths)
            
            # GET A DICTIONARY OF FARADAY PROBES OF FORM {SHOT_NO : PROBE OBJECT}
            self.FaradayProbes = pbuilder.build_probes()

            if self.plots:
                for _, FaradayProbe in self.FaradayProbes.items():
                    FaradayProbe.call_analysis()

        

        


