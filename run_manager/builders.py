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

    def __init__(self, shots:List[int]):
        self.shots = shots

    def _build(self):
        """Placeholder _build function to be overriden in derivative classes."""
        pass

    def builds(self)->Dict[int, Device]:
        pass

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
            efield_data_paths : Dict[int, str]
                Dictionary of form {SHOT_NO : PATH} containing paths to all E field oscilloscope data for each shot.
        
        """
        
        # INITIALIZE PARENT BUILDER CLASS
        super().__init__(shots=shots)

        # SPECIFY WHETHER IT IS A BDOT OR FARADAY PROBE
        self.device_name = device_name

        # ASSIGN DATA PATH- HERE, THIS WILL BE E_FIELD DATA
        self.efield_data_paths = data_paths_dict

        # OVERRIDE PARENT BUILDER CLASS' _build() METHOD
        self._build = self._build_probe
        self.builds = self.build_probes

        self.Probes = {}


    def _build_probe(self, efield_data_path, shot_no)->Device:
        """Builds a single Probe at a specified shot number.
    
        Parameters
        ----------
            efield_data_path : str
                The path where the relevant data (for the specified shot!) of the Electric Field is stored.
            shot_no : int
                The shot number for which we want to build the probe.


        Returns
        -------
            Probe : Device
                Single probe device object at the specified shot number.
        
        """

        #INITIALIZE THE FARADAY PROBE'S NAME, REFERENCING THE SHOT NUMBER
        device_name = f"{self.device_name} (SHOT {shot_no})"

        outputs = []

        #INTIALIZE EFIELD OUTPUT   
        efield = eField(shot_no=shot_no, device_name=device_name, data_path=efield_data_path)
        outputs.append(efield)

        Probe = Device(
            device_name=device_name,
            shot_no=shot_no,
            outputs=outputs
        )

        return Probe

    def build_probes(self, )->Dict[int, Device]:
        """Builds probe objects for the specified shot numbers, returning a dictionary of such objects, where the keys are
        the shot numbers, and the values are probe objects for that shot number.
        
        Returns
        -------
            self.Probes : Dict[int, Device]
                Dictionary of form {SHOT_NO : Probe Object} containing all of the constructed probe objects for the specified shot numbers.
        """
        
        for shot in self.shots:
            try:
                efield_data_path = self.efield_data_paths[shot]
            except:
                KeyError(f"Error: specified shot number {shot} for {self.device_name}, but no data exists for this shot.")

            self.Probes[shot] = self._build(efield_data_path=efield_data_path, shot_no=shot)

        return self.Probes
    

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
        super().__init__(shots = shots)

        # MULTIPLE CAMERAS EXIST ON THE EXPERIMENT, SO WE NEED TO SPECIFY THE CAMERA NAME RIGHT OFF THE BAT
        self.camera_name = device_name

        # ASSIGN DATA PATHS- HERE, THESE ARE PATHS TO IMAGES
        self.image_data_paths = data_paths_dict

        # OVERRIDE EMPTY ._build() METHOD FROM PARENT BUILDER CLASS
        self._build = self._build_camera
        self.builds = self.build_cameras

        self.Cameras = {}

    def _build_camera(self, image_data_path:str, shot_no:int)->Device:
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

        device_name = f"{self.camera_name} (SHOT {shot_no})"
        outputs = []
        image_out = Image(
            shot_no=shot_no,
            device_name=device_name,
            output_name="Image",
            data_path=image_data_path
        )
        outputs.append(image_out)

        camera = Device(
            device_name=device_name,
            shot_no=shot_no,
            outputs=outputs,
        )

        return camera
    
    def build_cameras(self)->Dict[int, Device]:
        """Builds multiple camera objects, one for each specified shot, and adds to the class dictionary of form {Shot no: Camera}, then
        returns the dictionary.
        
        Returns
        -------
            self.Cameras : Dict[int, Device]
                Dictionary of devices, where the key number is the shot number, and the value is the Device object.
        
        """

        # ITERATE OVER ALL SPECIFIED SHOTS IN CLASS' SHOT LIST
        for shot in self.shots:
            try:
                image_data_path = self.image_data_paths[shot]
            except:
                KeyError(f"Error: specified shot number {shot} for device {self.camera_name}, but no data exists for this shot.")
            
            # BUILD SINGLE CAMERA AND ADD TO DICTIONARY 
            cam = self._build(image_data_path, shot)
            self.Cameras[shot] = cam

        return self.Cameras

        