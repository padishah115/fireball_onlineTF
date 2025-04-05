#################################################################################################
# CONSTRUCTOR CLASSES- Classes which iteratively build device objects at specified shot numbers #
#   during runtime. I created this file in order to prevent the run_manager file from being     #
#   cluttered with lots of different "builder" definitions.                                     #
#################################################################################################

#Module imports
from typing import List, Dict

#Imports from homebrew device and output files
from devices.device import Device
from devices.output import *

#########################
# FARADAY PROBE BUILDER #
#########################

class ProbeBuilder:
    """Class responsible for building Faraday Probe device objects for the desired shot numbers at run time."""

    def __init__(self, shots:List[int], efield_data_paths:Dict[int, str]):
        """
        Parameters
        ----------
            shots : List[int]
                List of the shots that we are interested in Faraday Probe data for.
        
        """
        self.shots = shots
        self.efield_data_paths = efield_data_paths

        self.FaradayProbes = {}


    def _build_probe(self, efield_data_path, shot_no)->Device:
        """Builds a single Faraday Probe at a specified shots number.
    
        Parameters
        ----------
            efield_data_path : str
                The path where the relevant data (for the specified shot!) of the Electric Field is stored.
            shot_no : int
                The shot number for which we want to build the probe.
        
        """

        #INITIALIZE THE FARADAY PROBE'S NAME, REFERENCING THE SHOT NUMBER
        device_name = f"Faraday Probe (SHOT {shot_no})"

        outputs = []

        #INTIALIZE EFIELD OUTPUT   
        efield = eField(shot_no=shot_no, device_name=device_name, data_path=efield_data_path)
        outputs.append(efield)

        FaradayProbe = Device(
            device_name=device_name,
            shot_no=shot_no,
            outputs=outputs
        )

        return FaradayProbe

    def build_probes(self, )->Dict[int, Device]:
        """Builds faraday probe objects for the specified shot numbers, returning a dictionary of such objects, where the keys are
        the shot numbers, and the values are faraday probe objects for that shot number."""
        
        for shot in self.shots:
            efield_data_path = self.efield_data_paths[shot]
            self.FaradayProbes[shot] = self._build_probe(efield_data_path=efield_data_path, shot_no=shot)

        return self.FaradayProbes