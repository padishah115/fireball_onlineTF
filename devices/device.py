#Module imports
import os
import sys

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
    
    """

    def __init__(self, device_name:str, outputs:list[Output]):
        """
        Parameters
        ----------
            device_name : str
                The name of the diagnostic device.
            outputs : list
                List of all device outputs

        """
        
        self.device_name = device_name
        self.outputs = outputs

    def __repr__(self):
        return f"{self.name} (Device Object)"

    def get_outputs(self):
        """Returns list of outputs from the device"""
        print(f"Outputs from {self.device_name}", self.outputs)

    def call_analysis(self):
        """Calls all relevant analysis on the device outputs"""
        
        #Loop through all of the device's outputs and call their analyze functions one-by-one
        for output in self.outputs:
            print(f"Calling analysis for {output} from {self.device_name}...")
            output.analyze()



