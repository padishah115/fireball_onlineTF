#Module imports
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

    def __init__(self, device_name:str, shot_no:int, output:Output):
        """
        Parameters
        ----------
            device_name : str
                The name of the diagnostic device.
            
            shot_no : int
                The shot number for which we have built the device.
            
            output : Outputs
                Output produced by the device.

        """
        
        #####################################
        # INTIALIZE BASIC DEVICE PARAMETERS #
        #####################################

        # NAME AND SHOT NUMBER OF DEVICE. 
        self.device_name = device_name
        # RECALL THAT WE ARE CREATING SEPARATE DEVICE OBJECTS FOR EACH SHOT
        self.shot_no = shot_no
        
        # OUTPUTS FOR THE SHOT
        self.output = output


    def __repr__(self):
        return f"{self.device_name} (Device Object)"

    def get_output(self):
        """Returns output from the device for the shot."""

        print(f"Outputs from {self.device_name} (SHOT {self.shot_no}):", self.output)

    def call_data(self, background_corrections, plots):
        """Calls all relevant analysis on the device outputs.
        
        Parameters
        ----------
            background_corrections : List[str]
                List of the type of background corrections we would like to perform on the data.
            plots : bool
                Boolean governing whether or not we want the data to be plotted "on-the-fly" as analysis is performed.

        Returns 
        -------
            data : Dict
                Raw and background-corrected data from the devices
        """

        data = {}

        # Loop through all of the device's outputs and call their analyze functions one-by-one
        print(f"Calling analysis for {self.output} ...")
        raw_data, bkg_data = self.output.analyze(background_corrections=background_corrections, plots=plots) # CALL .analyze() METHOD ON ALL OUTPUTS
        data[f"RAW"] = raw_data
        data[f"BKG_CORRECTED"] = bkg_data

        return data




