from utils.opmanager.operationsmanager import OperationsManager
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Tuple
from scipy.fft import rfftfreq, rfft
import logging
from skimage.transform import ProjectiveTransform, warp
logger = logging.getLogger(__name__)

############################
# IMAGE OPERATIONS MANAGER #
############################

class ImageOperationsManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data=None):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)
    
###########
# CHROMOX #
###########

class DigicamImageManager(ImageOperationsManager):
    """Specialized ImageManager for Chromox camaeras."""

    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data=None):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)


    def plot(self, norm:bool=False):
        """Plotting method for the Chromox cameras. We will display the raw image with or without centroid fitting,
        as well as lineouts across both axes.
        
        Parameters
        ----------
            norm:bool
                Whether or not we want to normalize the image to maximum pixel intensity.
        """

        self.image = self.shot_data["DATA"]
        
        # Check whether we want to normalize
        logger.info(f"Normalise image: {norm}")
        normalization_factor = np.max(self.image) if norm else 1
        
        self.image /= normalization_factor
        vmax = self.input["OPERATIONS"]["VMAX"]
        
        if self.input["OPERATIONS"]["WARP"][self.DEVICE_NAME]:
    
            H = self.input["OPERATIONS"]["WARP_SPECS"]["H"][self.DEVICE_NAME]
            W = self.input["OPERATIONS"]["WARP_SPECS"]["W"][self.DEVICE_NAME]
            dest = np.array([[0,0], [W,0], [W,H], [0,H]])
            corners = self.input["OPERATIONS"]["WARP_SPECS"]["CORNERS"][self.DEVICE_NAME]

            #if self.DEVICE_NAME == "HRM6":
            #    corners = [[0, 0], [self.image.shape[1],0], [self.image.shape[1], self.image.shape[0]], [0, self.image.shape[0]]]

            tform = ProjectiveTransform()
            ok = tform.estimate(corners, dest)
            if not ok:
                raise RuntimeError("Homography estimation failed")

            self.image = warp(
                self.image,
                inverse_map=tform.inverse,
                output_shape = (H, W),
                preserve_range = True 
            )
        else:
            raise RuntimeError("Must allow warping on this branch due to Hayden's inability to make things work properly (yet)")

        # WRAP THE CALCULATIONS BELOW IN CASE WE JUST WANT TO SPEED THINGS UP AND JUST PLOT THE IMAGES
        if not self.input["PLOT_ONLY"]:
            # GET LINEOUTS
            lineout_x = np.sum(self.image, axis=0) # x lineout

            # CHECK WHETHER WE HAVE STD DEVIATION INFORMATION
            if self.std_data is not None:

                if self.input["OPERATIONS"]["WARP"][self.DEVICE_NAME]:
                    self.std_image = warp(
                    self.std_data["DATA"],
                    inverse_map=tform.inverse,
                    output_shape = (H, W),
                    preserve_range = True 
                    )
                else:
                    self.std_image = self.std_data["DATA"]

                self.std_image /= normalization_factor
                upper_image = np.add(self.image, self.std_image)
                lower_image = np.subtract(self.image, self.std_image)

                ###################################
                # Lineouts for stddev information #
                ###################################
        
                # Upper bound 
                upper_lineout_x = np.sum(upper_image, axis=0)

                # Lower bound
                lower_lineout_x = np.sum(lower_image, axis=0)
                
            
            #initialize figure
            fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(8, 10))


    
            #########
            # IMAGE #
            #########
            axs[0].imshow(self.image, aspect='auto', vmax=self.input["OPERATIONS"]["VMAX"])
            axs[0].set_xlabel("x / mm")
            axs[0].set_ylabel("y / mm")
    
            
            ##############
            # X lineouts #
            ##############
            axs[1].plot(np.arange(W), lineout_x, label="X Marginal")

            if self.std_data is not None:
                axs[1].fill_between(np.arange(W), lower_lineout_x, upper_lineout_x, alpha=0.2, label='± 1σ')
            
            axs[1].set_ylabel("Intensity")
            axs[1].set_xmargin(0)
            axs[1].legend()
    
            # SHOW THE FIGURE
            if norm:
                fig.suptitle(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}\n Normalized to Max Pixel Intensity")
            else:
                fig.suptitle(f"Image from {self.DEVICE_NAME}, \n{self.shot_no} \n ({self.input['NAME']})")
            
            fig.canvas.manager.set_window_title(f"{self.DEVICE_NAME}")
            fig.tight_layout()
            plt.show(block=False)


        else:
            fig, axs = plt.subplots(figsize=(16, 9))
            axs.imshow(self.image, aspect='auto', vmax=vmax)
            # SHOW THE FIGURE
            if norm:
                fig.suptitle(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}\n Normalized to Max Pixel Intensity")
            else:
                fig.suptitle(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
            fig.canvas.manager.set_window_title(f"{self.DEVICE_NAME}")
            plt.show(block=False)
        

class AndorImageManager(ImageOperationsManager):
    pass

class OrcaImageManager(ImageOperationsManager):
    pass