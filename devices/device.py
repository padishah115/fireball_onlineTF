#Module imports
from typing import Dict, List
import numpy as np

#Homebrew output class
from devices.output import Output

#################################
# DIAGNOSTIC DEVICES BASE CLASS #
#################################

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
        get_output()
            Tells us the type of output produced by the device.
        
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
            
            output : Output
                Output produced by the device.

        """
        
        #####################################
        # INTIALIZE BASIC DEVICE PARAMETERS #
        #####################################

        # NAME AND SHOT NUMBER OF DEVICE. 
        self.device_name = device_name
        # RECALL THAT WE ARE CREATING SEPARATE DEVICE OBJECTS FOR EACH SHOT
        self.shot_no = shot_no
        
        # OUTPUT FOR THE SHOT
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

class SpectrometerCamera(Camera):
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

class Spectrometer(Camera):
    """Spectrometer device object responsible for giving us information about the synchrotron emission, which
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


