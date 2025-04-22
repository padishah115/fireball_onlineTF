#################################################################################################
#  BUILDER CLASSES- Classes which iteratively build device objects at specified shot numbers    #
# during runtime. I created this file in order to prevent the run_manager file from being       #
# cluttered with lots of different "builder" definitions.                                       #
#################################################################################################

#Module imports
from typing import List, Dict

#Imports from homebrew device and output files
from devices.device import Device
from devices.output import *

################################
# GENERIC BUILDER PARENT CLASS #
################################

class Builder():
    """Parent class for all runtime builders. At runtime, each builder is responsible for initialising a dictionary of 
    a certain species of device at certain shot numbers. Each device has a separate constructor to account for the fact that we want
    different names."""

    def __init__(self, shots:List[int], device_name:str, RAW_data_paths_dict:Dict[int, str], BKG_paths_dict:Dict[str, str]):
        """
        Parameters
        ----------
            shots : List[int]
                List of all the shot numbers that we are interested in collecting data from.
            
            device_name : str
                Name of the device itself.
            
            RAW_data_paths_dict : Dict[int, str]
                Dictionary containing paths to all data (NOT BACKGROUND SUBTRACTED), indexed (key'd) by shot number.
            
            BKG_paths_dict : Dict[str, str]
                Paths to different background images (e.g. darkfield, etc.), where the key is the name of the background as a string.
        
        """
        self.shots = shots
        self.device_name = device_name
        self.RAW_data_paths_dict = RAW_data_paths_dict
        self.BKG_paths_dict = BKG_paths_dict

        self.Devices = {}

    def _build(self, raw_data_path, shot_no)->Device:
        """Placeholder _build function to be overriden in derivative classes."""
        raise NotImplementedError(f"Error: no _build() method supplied fo r")

    def build_devices(self)->Dict[int, Device]:
        """Builds probe objects for the specified shot numbers, returning a dictionary of such objects, where the keys are
        the shot numbers, and the values are probe objects for that shot number. Can be seen as building devices ACROSS TIME....... sp00ky
        
        Returns
        -------
            self.Devices : Dict[int, Device]
                Dictionary of form {SHOT_NO : Device Object} containing all of the constructed objects for the specified shot numbers.
        """
        
        # ITERATE OVER EACH OF THE SPECIFIED SHOT NUMBERS
        for shot in self.shots:
            # MAKE SURE DATA FOR THE RELEVANT SHOT ACTUALLY EXISTS FOR THE OBJECT 
            try:
                RAW_data_path = self.RAW_data_paths_dict[shot]
            except:
                KeyError(f"Error: specified shot number {shot} for {self.device_name}, but no data exists for this shot.")

            # ADD DEVICE OBJECT TO DEVICES DICTIONARY, WHERE THE KEY IS GIVEN BY THE SHOT NUMBER
            self.Devices[shot] = self._build(raw_data_path=RAW_data_path, shot_no=shot)

        # RETURN DEVICES DICTIONARY, WHICH IS OF FORM {SHOT NO : DEVICE OBJECT}
        return self.Devices

##############################
# FARADAY/BDOT PROBE BUILDER #
##############################

class ProbeBuilder(Builder):
    """Class responsible for building Faraday or Bdot Probe device objects for the desired shot numbers at run time."""

    def __init__(self, shots:List[int], device_name:str, RAW_data_paths_dict:Dict[int, str], BKG_paths_dict:Dict[str, str]):
        """
        Parameters
        ----------
            shots : List[int]
                List of the shots that we are interested in Probe data for.
            
            device_name : str
                Name of the device as a string. There are both Bdot Probes and Faraday Probes on the experiment,
                which we will need to differentiate between.
            
            RAW_data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT_NO : PATH} containing paths to all raw (not background-subtracted) E field oscilloscope data for each shot.
            
            BKG_paths_dict : Dict[str, str]
                Paths to different background data (e.g. darkfield, etc.), where the key is the name of the background as a string.
        
        """
        
        # INITIALIZE PARENT BUILDER CLASS
        super().__init__(shots=shots, device_name=device_name, RAW_data_paths_dict=RAW_data_paths_dict, BKG_paths_dict=BKG_paths_dict)

        # OVERRIDE PARENT BUILDER CLASS' _build() METHOD
        self._build = self._build_probe

        self.Probes = {}


    def _build_probe(self, raw_data_path:str, shot_no:int)->Device:
        """Builds a single Probe at a specified shot number.
    
        Parameters
        ----------
            raw_data_path : str
                The path where the relevant (RAW) data (for the specified shot!) of the Electric Field is stored.
            
            shot_no : int
                The shot number for which we want to build the probe.


        Returns
        -------
            Probe : Device
                Single probe device object at the specified shot number.
        
        """

        # INITIALIZE THE FARADAY PROBE'S NAME, REFERENCING THE SHOT NUMBER
        device_name_with_shot = f"{self.device_name} (SHOT {shot_no})" 
        #  note that it is important to add shot information to the self.device_name belonging to the Builder class- 
        # the self.device_name from the builder class will tell us (e.g.) whether it's HRM3 or HRM4, but WON'T tell us what shot
        # we are looking at.

        # INTIALIZE EFIELD OUTPUT   
        efield = eField(device_name=device_name_with_shot, raw_data_path=raw_data_path, background_paths_dict=self.BKG_paths_dict)
        output = efield

        Probe = Device(
            device_name=device_name_with_shot,
            shot_no=shot_no,
            output=output,
        )

        return Probe
    

##################
# CAMERA BUILDER #
##################

#  Generic camerabuilder class- can be reused for anything that produces data that we want to visualise as
# an image. Idea is to use this for all four cameras (3-6).

class CamBuilder(Builder):
    """Builder class for cameras, which produce image outputs."""
    
    def __init__(self, shots:List[int], device_name:str, RAW_data_paths_dict:Dict[int, str], BKG_paths_dict:Dict[str, str]):
        """
        Parameters
        ----------
            shots : List[int]
                List of the shots that we are interested in Probe data for.
            
            device_name : str
                Name of the device as a string. There are both Bdot Probes and Faraday Probes on the experiment,
                which we will need to differentiate between.
            
            RAW_data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT_NO : PATH} containing paths to all raw image data (NOT background-subtracted) for each shot.
            
            BKG_paths_dict : Dict[str, str]
                Paths to different background data (e.g. darkfield, etc.), where the key is the name of the background as a string.
        
        """

        # INITIALIZE PARENT BUILDER CLASS
        super().__init__(shots = shots, device_name=device_name, RAW_data_paths_dict=RAW_data_paths_dict, BKG_paths_dict=BKG_paths_dict)

        # OVERRIDE EMPTY ._build() METHOD FROM PARENT BUILDER CLASS
        self._build = self._build_camera

        # EMPTY CAMERAS DICTIONARY- WILL EVENTUALLY BE OF FORM {SHOT NO : CAMERA OBJECT}
        self.Cameras = {}


    def _build_camera(self, raw_data_path:str, shot_no:int)->Device:
        """Builds a single camera object at the specified shot number.
        
        Parameters
        ----------
            raw_data_path : str
                Path to where the raw image data for the shot is stored.
            
            shot_no : int
                The shot number for which we want to build the camera.

        Returns
        -------
            camera : Device
                A single camera object constructed at the specified shot number.
        
        """

        # INTIALIZE CAMERA NAME- MULTIPLE CAMERAS IN THE EXPERIMENT, SO NEED TO SPECIFY CAMERA NAME
        device_name_with_shot = f"{self.device_name} (SHOT {shot_no})"
        #  note that it is important to add shot information to the self.device_name belonging to the Builder class- 
        # the self.device_name from the builder class will tell us (e.g.) whether it's HRM3 or HRM4, but WON'T tell us what shot
        # we are looking at.
        
        # IMAGE OUTPUT
        image_out = Image(
            device_name=device_name_with_shot,
            output_name=f"Image",
            raw_data_path=raw_data_path,
            background_paths_dict=self.BKG_paths_dict
        )
        
        output = image_out

        # CREATE THE DEVICE OBJECT USING THE OUTPUT LIST CONSTRUCTED ABOVE
        camera = Device(
            device_name=device_name_with_shot,
            shot_no=shot_no,
            output=output,
        )

        return camera
    

        