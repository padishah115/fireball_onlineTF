from utils.opmanager.operationsmanager import OperationsManager
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import median_filter
import logging
from skimage.transform import ProjectiveTransform, warp
logger = logging.getLogger(__name__)

import pandas as pd

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

    def __init__(self, DEVICE_NAME:str, shot_no:str, label:str, shot_data:dict, input:dict):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input)
        
        self.N = self.shot_data["N"]

        self.data_list = []
        for i in range(self.N):
            self.data_list.append(self.shot_data[i]["DATA"])
        
        self.empty_exemplar = np.empty_like(self.shot_data[0]["DATA"])

        self._set_average_and_std_image()


    def plot(self):
        """Plotting method for the Chromox cameras. We will display the raw image with or without centroid fitting,
        as well as lineouts across both axes.
        """
    
        H = self.input["OPERATIONS"]["WARP_SPECS"]["H"][self.DEVICE_NAME]
        W = self.input["OPERATIONS"]["WARP_SPECS"]["W"][self.DEVICE_NAME]
        dest = np.array([[0,0], [W,0], [W,H], [0,H]])
        corners = self.input["OPERATIONS"]["WARP_SPECS"]["CORNERS"][self.DEVICE_NAME]

        tform = ProjectiveTransform()
        ok = tform.estimate(corners, dest)
        if not ok:
            raise RuntimeError("Homography estimation failed")

        # Peform warping operations
        self.average_img = warp(
            self.average_img,
            inverse_map=tform.inverse,
            output_shape = (H, W),
            preserve_range = True 
        )

        self.std_img = warp(
        self.std_img,
        inverse_map=tform.inverse,
        output_shape = (H, W),
        preserve_range = True 
        )

        # Lineouts
        lineout_avg = np.sum(self.average_img, axis=0)
        lineout_std = np.sum(self.std_img, axis=0)
        upper_lineout = np.add(lineout_avg, lineout_std)
        lower_lineout = np.subtract(lineout_avg, lineout_std)

        # Saving data
        data = {
            "LINEOUT AVG":pd.Series(lineout_avg),
            "LINEOUT STD":pd.Series(lineout_std)
        }
        df = pd.DataFrame(data)
        df.to_csv(f'./spectrometer-data/{self.input["NAME"]}_{self.input["DEVICE_NAME"]}.csv')

            
        
        #initialize figure
        fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(8, 10))


        #########
        # IMAGE #
        #########
        axs[0].imshow(self.average_img, aspect='auto', vmax=self.input["OPERATIONS"]["VMAX"])
        axs[0].set_xlabel("x / mm")
        axs[0].set_ylabel("y / mm")

        #################
        # LINEOUT PLOTS #
        #################
        X = np.arange(W)
        axs[1].plot(X, lineout_avg)
        axs[1].fill_between(X, lower_lineout, upper_lineout, alpha=0.2)
        axs[1].set_xlabel("x / mm")
        axs[1].set_ylabel("Intensity")

        # SHOW THE FIGURE
        fig.suptitle(f"Image from {self.DEVICE_NAME}, \n{self.shot_no} \n ({self.input['NAME']})")
        
        fig.canvas.manager.set_window_title(f"{self.DEVICE_NAME}")
        fig.tight_layout()
        plt.show(block=False)


    def _set_average_and_std_image(self):
        """Method for setting average composite image and 'error' image for the class."""

        average_img = self.empty_exemplar
        var_img = self.empty_exemplar
        for img in self.data_list:
            filtered_img = self._apply_median_filter(img)
            average_img = np.add(average_img, filtered_img)
        
        self.average_img = np.multiply(average_img, 1/self.N) # divide sum by total image number

        for img in self.data_list:
            filtered_img = self._apply_median_filter(img)
            var_img = np.add(var_img, np.pow(np.subtract(filtered_img, self.average_img), 2))
        
        var_img = np.multiply(var_img, 1/(self.N-1+1e-5)) # divide by N-1 to get variance image
        self.std_img = np.multiply(np.pow(var_img, 0.5), 1/np.sqrt(self.N)) # square root the variance to get the std deviation



    def _apply_median_filter(self, img:np.ndarray, kernel_size:int=3)->np.ndarray:
        """Applies a median filter to a supplied image.
        
        Parameters
        ----------
            img : np.ArrayLike
                The input image to whom median filtering will be applied.
            kernel_size
                The dimension of the square filter kernel.

        Returns
        -------
            filtered_img : np.ArrayLike
                The image after a median filter has been applied.
        """
        footprint=np.ones((kernel_size, kernel_size))
        filtered_img = median_filter(img, footprint=footprint)
        return filtered_img
        

class AndorImageManager(ImageOperationsManager):
    pass

class OrcaImageManager(ImageOperationsManager):
    pass