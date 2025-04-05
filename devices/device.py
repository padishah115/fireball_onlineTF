#Module imports
import os
import sys
from typing import Dict, List

#Homebrew output class
from devices.output import Output

##########################
# DIAGNOSTICS BASE CLASS #
##########################

class Device:
    """Parent class for all diagnostic devices on FIREBALL-III.
    
    Attributes
    ----------
        name : str
            The name of the device.
        device_outputs : list[Output]
            List of all diagnostics outputs from the device.

    Methods
    -------
        get_outputs()
            Prints a list of all the outputs associated with the device.
        call_analysis()
            Iterates through all outputs assigned to the device, and calls the .analyze() methods
            on each of those outputs.
    
    """

    def __init__(self, device_name:str, shot_no:int, outputs:List[Output]):
        """
        Parameters
        ----------
            device_name : str
                The name of the diagnostic device.
            shot_no : int
                The shot number for which we have built the device.
            outputs : List[Outputs]

        """
        
        #####################################
        # INTIALIZE BASIC DEVICE PARAMETERS #
        #####################################

        # NAME AND SHOT NUMBER OF DEVICE. 
        self.device_name = device_name
        # RECALL THAT WE ARE CREATING SEPARATE DEVICE OBJECTS FOR EACH SHOT
        self.shot_no = shot_no
        
        # OUTPUTS FOR THE SHOT
        self.outputs = outputs


    def __repr__(self):
        return f"{self.device_name} (Device Object)"

    def get_outputs(self):
        """Returns list of outputs from the device for the shot."""

        print(f"Outputs from {self.device_name} (SHOT {self.shot_no}):", self.outputs)

    def call_analysis(self):
        """Calls all relevant analysis on the device outputs."""

        # Loop through all of the device's outputs and call their analyze functions one-by-one
        for output in self.outputs:
            print(f"Calling analysis for {output} from {self.device_name}...")
            output.analyze() # CALL .analyze() METHOD ON ALL OUTPUTS



