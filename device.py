#Module imports
from typing import Dict, List
import numpy as np

#Homebrew output class
from shot import *

#################################
# DIAGNOSTIC DEVICES BASE CLASS #
#################################

class Device:
    """Parent class for all diagnostic devices on FIREBALL-III.
    
    Attributes
    ----------
        name : str
            The name of the device.
        
        shots : list[Shot]
            List of all shot objects attributed to the device.
    
    """

    def __init__(self, device_name:str, shot_data_path_dict:Dict[str, str]):
        """
        Parameters
        ----------
            device_name : str
                The name of the diagnostic device.
            
            shot_data_path_dict : Dict[str, str]
                Dictionary of form {"INDEX" : "/PATH/TO/DATA"} from which we can iteratively
                create new shot objects for our device
            

        """
        
        #####################################
        # INTIALIZE BASIC DEVICE PARAMETERS #
        #####################################

        # NAME AND SHOT NUMBER OF DEVICE. 
        self.device_name = device_name

        # INITIALIZE DICTIONARY OF SHOT DATA PATHS
        self.shot_data_path_dict = shot_data_path_dict
        
        # INVENTORY OF SHOT OBJECTS FOR THE DEVICE
        self.shots = []
        self.make_shot_list()


    def __repr__(self):
        return f"{self.device_name} (DEVICE)"

    def show_shots(self):
        """Displays all shots stored in the device object. This will ultimately be chosen
        via user input into the .JSON file."""

        print(f"\nSHOT LIST FOR {self}")
        for shot in self.shots:
            print(shot)
        print("-----------")

    def make_shot_list()->List:
        """Create and return a list of shot objects for the device."""
        raise NotImplementedError("Error: no method for creating shot dictionary has been specified.")
        
    
##################
# CAMERA CLASSES #
################## 

class Camera(Device):
    """Parent class for camera devices.
    
    Things all camera subclasses must do:
        -Get (and plot) raw image data 
        -Get (and plot) background-subtracted image data. Some of this subtraction must be performed from multiple images.
        -Get (and plot) lineouts across specified dimensions.
            -Lineouts can be produced with MEAN and ERROR over 5 shots, say.
    """

    def __init__(self, device_name, shots):
        super().__init__(device_name, shots)

    def make_shot_list(self):
        """Creates a list of shot objects and stores this list in the device."""

        # ITERATE THROUGH THE DATA PATHS DICTIONARY TO INITIALIZE
        #  AND STORE SHOT OBJECTS
        for shot_key in self.shot_data_path_dict.keys():
            # create shot object with the correct key, and which bears the device's name.
            shot_obj = ImageShot(
                device_name=self.device_name,
                shot_key=shot_key,
                shot_data_path=self.shot_data_path_dict[shot_key]
                )
            
            #add shot object to the device's shot list
            self.shots.append(shot_obj)
        
    
    def get_lineout(img:np.ndarray, axis)->np.ndarray:
        """Performs integration along one axis of the image, thus producing image lineouts.
        
        Parameters
        ----------
            img : np.ndarray
                The image for which we want to perform the integration along some axis.
            axis : int
                The axis along which we want to perform integration.

        Returns
        -------
            lineout : np.array
                Reduced-dimensionality image which has been lineout-integrated
        """

    def get_avg_img(imgs:List[np.ndarray])->np.ndarray:
        """Takes a list of images as argument and returns some averaged image.
        
        Parameters
        ----------
            imgs : List[np.ndarray]
                List of images over which we want to perform averages.

        Returns
        -------
            avg_img : np.ndarray
        """

    def get_fft_img(img:np.ndarray)->np.ndarray:
        """Performs Fast Fourier Transform on an image (which could be an averaged image or raw image), 
        returning a 2D Fourier Spectrum.
        
        Parameters
        ----------
            img : np.ndarray
                Image tensor for which we want to produce a Fourier transform.

        Returns
        -------
            fft_img : np.ndarray
                Fourier-Transformed image tensor.
        """

    

# CHROMOX CAMERAS (HRM3+4) FOR MONITORING TRANSVERSE INSTABILITIES AT THE CHROMOX SCREEN

class ChromoxCamera(Camera):
    """Class for the Chromox cameras, who track transverse instabilities by monitoring up- and down-stream profiles of the beam,
    which are measured using luminescence of a chromox screen.
    
    Things the device must do in addition to the Camera class:
        -Fit a 2D Gaussian to the Chromox spot and calculate the std. of the spot in both dimensions.
        -Plot of centroid std. across shots to observe whether the beam is focused by plasma.
        
    """
    
    def get_gaussian_fit():
        """Fits a Gaussian to a spot on a Chromox screen."""


# STREAK CAMERA (OTR)- MEASUREMENT OF LONGITUDINAL INSTABILITIES IN THE PLASMA

class StreakCamera(Camera):
    """Streak unit device class. This is distinct from any camera class, as instead of getting any sort of 2D
    image, we are instead passed a 3D array of [time, x, counts]. 
    
    Things the device must do in addition to the Camera class:
        -Get (and plot) lineouts produced by integrating along the Y (time) dimension
        -Plot modulation scale length (from FFT)
        -Calculate density fluctuations (max - min) / (max + min)
    """

    def get_intensity_vs_time():
        """Produces data which stores intensity as a function of time."""


# SPECTROMETER CAMERA- IMAGES ADDITIONAL CHROMOX SCREENS TO GET INFORMATION ABOUT ELECTRON ENERGIES. 
# ANGLE OF DEFLECTION CAN BE CONVERTED INTO INFORMATION ABOUT ELECTRON ENERGY.

class PairSpecCamera(Camera):
    """Device class for the spectrometer cameras, which image the chromox screens placed after the deflection of the emergent
    electron beams from the electromagnet. Differing divergence information for positrons and electrons can give
    us valuable information about behaviour inside of the plasma.
    
    Things the device must do in addition to the camera class:
        -Convert the image data into information about the beam divergence and energy.
            -Integrate over x (to get divergence vs charge)
            -Integrate over y (to get energy vs charge)
            -Compute std. divergence of the beam across some number of shots.
            -Plot spectrum vs counts on camera (proportional to charge)  (electrons & positrons):  (single shot and averaged over n shots with error)
            -Plot divergence counts on camera (proportional to charge) )  (electrons & positrons):  (single shot and averaged over n shots with error)
            -Plot std of beam divergence for single shot and/or averaged over n shots with error.


    """

# DATA FROM SYNCHROTRON EMISSION

class SynchroCamera(Camera):
    """Synchrotron spectrometer device object responsible for giving us information about the synchrotron emission, which
    produces a 2D image of wavelength vs space. 
    
    Things the device must do:
        -Account for different filters on different runs

    """





#################
# PROBE CLASSES #
#################

class Probe(Device):
    """Probe parent device class for dealing with field data as a function of time. This is relevant for the BDot and Faraday Probes.
    
    Things the probe parent class must do:
        -Subtract background data (multiple background images)
        -Show voltage v time traces
        -Average traces over multiple shots and get mean/std. information
    """

    def __init__(self, device_name, shot_data_path_dict):
        super().__init__(device_name, shot_data_path_dict)

    def make_shot_list(self):
        """Creates a list of shot objects and stores this list in the device."""

        # ITERATE THROUGH THE DATA PATHS DICTIONARY TO INITIALIZE
        #  AND STORE SHOT OBJECTS
        for shot_key in self.shot_data_path_dict.keys():
            # create shot object with the correct key, and which bears the device's name.
            shot_obj = VoltShot(
                device_name=self.device_name,
                shot_key=shot_key,
                shot_data_path=self.shot_data_path_dict[shot_key]
                )
            
            #add shot object to the device's shot list
            self.shots.append(shot_obj)


