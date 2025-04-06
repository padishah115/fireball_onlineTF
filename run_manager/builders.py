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
    differene names."""

    def __init__(self, shots:List[int], device_name:str, data_paths_dict:Dict[int, str]):
        """
        Parameters
        ----------
            shots : List[int]
                List of all the shot numbers that we are interested in collecting data from.
            device_name : str
                Name of the device itself.
            data_paths_dict : Dict[int, str]
                Dictionary containing paths to all data, indexed (key'd) by shot number.
        
        """
        self.shots = shots
        self.device_name = device_name
        self.data_paths_dict = data_paths_dict

        self.Devices = {}

    def _build(self, data_path, shot_no)->Device:
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
                data_path = self.data_paths_dict[shot]
            except:
                KeyError(f"Error: specified shot number {shot} for {self.device_name}, but no data exists for this shot.")

            # ADD DEVICE OBJECT TO DEVICES DICTIONARY, WHERE THE KEY IS GIVEN BY THE SHOT NUMBER
            self.Devices[shot] = self._build(data_path=data_path, shot_no=shot)

        # RETURN DEVICES DICTIONARY, WHICH IS OF FORM {SHOT NO : DEVICE OBJECT}
        return self.Devices

##############################
# FARADAY/BDOT PROBE BUILDER #
##############################

class ProbeBuilder(Builder):
    """Class responsible for building Faraday or Bdot Probe device objects for the desired shot numbers at run time."""

    def __init__(self, shots:List[int], device_name:str, data_paths_dict:Dict[int, str]):
        """
        Parameters
        ----------
            shots : List[int]
                List of the shots that we are interested in Probe data for.
            device_name : str
                Name of the device as a string. There are both Bdot Probes and Faraday Probes on the experiment,
                which we will need to differentiate between.
            data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT_NO : PATH} containing paths to all E field oscilloscope data for each shot.
        
        """
        
        # INITIALIZE PARENT BUILDER CLASS
        super().__init__(shots=shots, device_name=device_name, data_paths_dict=data_paths_dict)

        # OVERRIDE PARENT BUILDER CLASS' _build() METHOD
        self._build = self._build_probe

        self.Probes = {}


    def _build_probe(self, data_path:str, shot_no:int)->Device:
        """Builds a single Probe at a specified shot number.
    
        Parameters
        ----------
            data_path : str
                The path where the relevant data (for the specified shot!) of the Electric Field is stored.
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

        # INITIALIZE EMPTY OUTPUTS LIST- WE WILL LATER APPEND OUTPUTS TO THIS FOR EACH OBJECT 
        outputs = []

        # INTIALIZE EFIELD OUTPUT   
        efield = eField(device_name=device_name_with_shot, data_path=data_path)
        outputs.append(efield)

        Probe = Device(
            device_name=device_name_with_shot,
            shot_no=shot_no,
            outputs=outputs
        )

        return Probe
    

##################
# CAMERA BUILDER #
##################

#  Generic camerabuilder class- can be reused for anything that produces data that we want to visualise as
# an image. Idea is to use this for all four cameras (3-6).

class CamBuilder(Builder):
    """Builder class for cameras, which produce image outputs."""
    
    def __init__(self, shots:List[int], device_name:str, data_paths_dict:Dict[int, str]):
        """
        Parameters
        ----------
            shots : List[int]
            device_name : str
            image_data_paths : Dict[int, str]
        
        """

        # INITIALIZE PARENT BUILDER CLASS
        super().__init__(shots = shots, device_name=device_name, data_paths_dict=data_paths_dict)

        # OVERRIDE EMPTY ._build() METHOD FROM PARENT BUILDER CLASS
        self._build = self._build_camera

        # EMPTY CAMERAS DICTIONARY- WILL EVENTUALLY BE OF FORM {SHOT NO : CAMERA OBJECT}
        self.Cameras = {}


    def _build_camera(self, data_path:str, shot_no:int)->Device:
        """Builds a single camera object at the specified shot number.
        
        Parameters
        ----------
            image_data_path : str
                Path to where the image data for the shot is stored.
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
        
        # INITIALIZE EMPTY OUTPUTS LIST FOR EACH CAMERA OBJECT
        outputs = []
        
        # IMAGE OUTPUT
        image_out = Image(
            device_name=device_name_with_shot,
            output_name=f"Image",
            data_path=data_path
        )
        # APPEND IMAGE OUTPUT TO THE DEVICE OBJECT'S OUTPUTS LIST
        outputs.append(image_out)

        # CREATE THE DEVICE OBJECT USING THE OUTPUT LIST CONSTRUCTED ABOVE
        camera = Device(
            device_name=device_name_with_shot,
            shot_no=shot_no,
            outputs=outputs,
        )

        return camera
    

        