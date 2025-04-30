from utils.opmanager.operationsmanager import OperationsManager
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict, Tuple
from scipy.fft import rfftfreq, rfft

############################
# IMAGE OPERATIONS MANAGER #
############################

class ImageManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data=None):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)
    

class DigicamImageManager(ImageManager):
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

        #INITIALIZE THE X AND Y AXES CORRECTLY.
        X = self.shot_data["X"]
        Y = self.shot_data["Y"]
        print(f"Shot no: {self.shot_no}")
        print(f"Y : {Y}\n")
        image = self.shot_data["DATA"]
        
        # Check whether we want to normalize
        print(f"Normalise image: {norm}")
        normalization_factor = np.max(image) if norm else 1
        
        image /= normalization_factor
        
        extent = [X[0], X[-1], Y[0], Y[-1]]
        
        # GET LINEOUTS
        lineout_x = np.sum(image, axis=0) # x lineout
        lineout_y = np.sum(image, axis=1) # y lineout
        # Get polar lineouts. These are dictionaries whose keys are the polar coordinates,
        # and whose values are the sum over the other dimension. I.e. r_dict is of form
        # {rval : intensity_summed_across_2pi}
        r_dict, theta_dict = self._get_polar_lineouts(image)

        # CHECK WHETHER WE HAVE STD DEVIATION INFORMATION
        if self.std_data is not None:
            upper_image = np.multiply(np.add(self.shot_data["DATA"],self.std_data["DATA"]), normalization_factor**-1)
            lower_image = np.multiply(np.subtract(self.shot_data["DATA"],self.std_data["DATA"]), normalization_factor**-1)

        ###################################
        # Lineouts for stddev information #
        ###################################

        # Upper bound 
        upper_lineout_x = np.sum(upper_image, axis=0) if self.std_data is not None else lineout_x
        upper_lineout_y = np.sum(upper_image, axis=1) if self.std_data is not None else lineout_y
        upper_r_dict, upper_theta_dict = (
            self._get_polar_lineouts(upper_image) 
            if self.std_data is not None
            else (r_dict, theta_dict)
        )

        # Lower bound
        lower_lineout_x = np.sum(lower_image, axis=0) if self.std_data is not None else lineout_x
        lower_lineout_y = np.sum(lower_image, axis=1) if self.std_data is not None else lineout_y
        lower_r_dict, lower_theta_dict = (
            self._get_polar_lineouts(lower_image)
            if self.std_data is not None
            else (r_dict, theta_dict)
        )


        # GET MOMENTS OF THE IMAGE
        mu, sigma = self._get_moments()
        
        
        #initialize figure
        fig = plt.figure(figsize=(16,8))

        gs = gridspec.GridSpec(nrows=3, ncols=2, wspace=0.3, hspace=0.5, 
                               #width_ratios=[1,1], 
                               #height_ratios=[1, aspect, 1]
                               )

        ########
        # DATA #
        ########
        ax_data = fig.add_subplot(gs[0,1])
        ax_data.axis("off")
        text = f'mu=[x̄={mu[0]:.2f}mm, ȳ={mu[1]:.2f}mm]. \nσ=[σ_x={sigma[0]:.2f}mm, σ_y={sigma[1]:.2f}mm]'
        ax_data.text(x=0.05, y=0.95, s=text, fontsize=20)

        #########
        # IMAGE #
        #########
        #ax1 = fig.add_axes(rect=[0., 0.05, 0.5, 0.5])
        ax1 = fig.add_subplot(gs[1,0])
        im = ax1.imshow(image, extent=extent, aspect='auto')
        #ax1.set_aspect(image.shape[0]/image.shape[1])
        
        # Get position of ax1 for colorbar placement
        bbox = ax_data.get_position()
        # Create colorbar axis above ax1
        cbar_ax = fig.add_axes([
            bbox.x0,          # left
            bbox.y0-0.001,   # bottom (just below ax1)
            bbox.width,       # same width as ax1
            0.02              # height of colorbar
        ])
        cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
        #cbar_label = "Rel. Pixel Intensity" if norm else "Abs. Pixel Intensity"
        #cbar.set_label(cbar_label, labelpad=5)
        
        ax1.set_xlabel("x / mm")
        ax1.xaxis.tick_top()
        ax1.xaxis.set_label_position("top")
        ax1.set_ylabel("y / mm")

        
        ##############
        # X lineouts #
        ##############
        #ax2 = fig.add_axes(rect=[0., 0., 0.5, 0.08])
        ax2 = fig.add_subplot(gs[0,0], sharex=ax1)
        ax2.plot(X, lineout_x, label="X Marginal")
        ax2.fill_between(X, lower_lineout_x, upper_lineout_x, alpha=0.2)
        #ax2.set_title("X Lineout")
        ax2.set_ylabel("Intensity")
        #ax2.set_xlabel("x / mm")
        ax2.legend()
        
        ##############
        # Y lineouts #
        ##############
        #ax3 = fig.add_axes(rect=[0.52, 0.1, 0.08, 0.4])
        ax3 = fig.add_subplot(gs[1,1], sharey=ax1)
        ax3.plot(lineout_y[::-1], Y, label="Y Marginal")
        ax3.fill_betweenx(Y, lower_lineout_y[::-1], upper_lineout_y[::-1], alpha=0.2)
        #ax3.set_title("Y Lineout")
        ax3.set_xlabel("Intensity")
        ax3.xaxis.tick_top()
        ax3.xaxis.set_label_position("top")
        #ax3.set_ylabel("y / mm")
        ax3.legend()

        ##############
        # R LINEOUTS #
        ##############
        ax4 = fig.add_subplot(gs[2,0])
        ax4.plot(r_dict.keys(), r_dict.values(), 
                 label="Radial Marginal"
                 )
        ax4.fill_between(r_dict.keys(), lower_r_dict.values(), upper_r_dict.values(), alpha=0.2)
        #ax4.set_title("Radial Lineout")
        ax4.set_xlabel("r / mm")
        ax4.set_ylabel("Intensity")
        ax4.legend()

        ##################
        # THETA LINEOUTS #
        ##################
        ax5 = fig.add_subplot(gs[2,1])
        thetas = [theta_val for theta_val in theta_dict.keys()]
        theta_intensities = [theta_intensity for theta_intensity in theta_dict.values()]
        lower_theta_intensities = [theta_intensity for theta_intensity in lower_theta_dict.values()]
        upper_theta_intensities = [theta_intensity for theta_intensity in upper_theta_dict.values()]
        
        ax5.plot(thetas[:-1], theta_intensities[:-1], label="Azimuthal Marginal")
        ax5.fill_between(thetas, lower_theta_intensities, upper_theta_intensities, alpha=0.2)
        #ax5.set_title("Azimuthal Lineout")
        ax5.set_xlabel("θ / radians")
        ax4.set_ylabel("Intensity")
        ax5.legend()

        # SHOW THE FIGURE
        if norm:
            fig.suptitle(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}\n Normalized to Max Pixel Intensity")
        else:
            fig.suptitle(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        plt.show()
        

    
    def _get_moments(self):
            """Calculates the first and second moments"""

            thresh = 0.2
            max_intensity = np.max(self.shot_data["DATA"])
            img = self.shot_data["DATA"]
            pixels_x = self.shot_data["X"]
            pixels_y = self.shot_data["Y"]
            mu = [0., 0.]
            var = [0., 0.]

            total_counts = 0
            
            # FIRST MOMENT CALCULATION
            for i in range(img.shape[1]):
                for j in range(img.shape[0]):
                    x = pixels_x[i]
                    y = -1*pixels_y[j]
                    coords = np.array([x, y])

                    if img[j, i]>thresh*max_intensity:
                        val = img[j, i]
                    else: 
                        val = 0
                    
                    weighted_coord = np.multiply(val, coords)
                    mu += weighted_coord
                    total_counts+=val

            mu = np.multiply(mu, 1/total_counts)

            total_counts = 0
            #SECOND MOMENT CALCULATION
            for i in range(img.shape[1]):
                for j in range(img.shape[0]):
                    x = pixels_x[i]
                    y = -1*pixels_y[j]
                    coords = [x, y]

                    if img[j, i]>thresh*max_intensity:
                        val = img[j, i]
                    else:
                        val = 0
                    
                    squared_displacement = np.pow(np.subtract(mu, coords),2)
                    var += np.multiply(squared_displacement, val)
                    total_counts += val

            var = np.multiply(var, 1/total_counts)
            sigma = np.pow(var, 0.5)


            return mu, sigma
        

    def _get_polar_lineouts(self, img)->Tuple[Dict, Dict]:

        # Number of bins for quantization during radial and azimuthal lineout
        bin_no = self.input["OPERATIONS"]["LINEOUT_BIN_NO"]
        
        x_interval = self.shot_data["X"][1] - self.shot_data["X"][0]
        y_interval = self.shot_data["Y"][1] - self.shot_data["Y"][0]

        #CENTROID WHICH WE TREAT AS ORIGIN
        im_length = img.shape[1]*x_interval
        im_height = img.shape[0]*y_interval

        x0 = (im_length+1)/2 if im_length % 2 == 1 else im_length/2
        y0 = (im_height+1)/2 if im_height % 2 == 1 else im_height/2 

        #BINNING
        r_max = np.ceil(np.sqrt(im_length**2 + im_height**2) / 2)
        r_bins = bin_no
        r_bin_length = r_max / r_bins

        theta_max = 2*np.pi
        theta_bins = bin_no
        theta_bin_length = theta_max / theta_bins

        #INITIALIZE EMPTY R, THETA ARRAYS
        r_dict = {r_val : 0 for r_val in np.multiply(r_bin_length, np.arange(0, r_bins+1))}
        theta_dict = {theta_val : 0 for theta_val in np.multiply(theta_bin_length, np.arange(0, theta_bins+1))}

        for i in range(img.shape[1]):
            for j in range(img.shape[0]):
                dx=i*x_interval-x0
                dy=(img.shape[0] -1 - j)*y_interval-y0

                if dx==0 and dy==0:
                    r = 0
                    theta = 0
                else:
                    r = np.sqrt(dx**2 + dy**2)
                    theta = self._get_theta(dx, dy)

                #ROUND TO QUANTIZED BINS
                r_key = min(int(np.floor(r/r_bin_length)), r_bins)*r_bin_length
                theta_key = min(int(np.floor(theta/theta_bin_length)), theta_bins)*theta_bin_length

                #print(r_max, r)

                # SUM PIXEL INTENSITY
                r_dict[r_key] += img[j][i] #/ (2*np.pi*r)
                theta_dict[theta_key] += img[j][i]

        return r_dict, theta_dict
    

    def _get_theta(self, x, y)->float:
        """Returns the cylindrical polar azimuthal coordinate of a coordinate, given its x and y values.
        
        Parameters
        ----------
            x : int
                The x coordinate of the point as an integer
            y : int
                The y coordinate of the point as an integer

        Returns
        -------
            theta : float
                The cylindrical azimuthal coordinate in radians.
        """
        
        theta = np.arctan2(y, x)
        if theta<0:
            theta += 2*np.pi
        return theta


class AndorImageManager(ImageManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, std_data=None):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, std_data)

    def plot(self, step:int=200):
        """Plots the image from the Andor camera attached to the synchrotron spectrometer,
        which is already a fourier transform. This image is then summed along the pixel axis, producing
        a 1D fourier transform, which is plotted alongside the raw image.
        
        Parameters
        ----------
            step : int = 200
                Stepsize between ticks on the wavelength axis in order to ease readability after plotting.
        """
    
        img = self.shot_data["DATA"]
        pixels_y = self.shot_data["Y"]


        y_tick_loc = np.arange(0, len(pixels_y), step=step)
        pixels_y_rounded = [f"{pixel:.2f}" for pixel in pixels_y] 

        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16,8))
        
        # PHYSICAL IMAGE
        axs[0].imshow(img, aspect='auto')
        axs[0].set_yticks(y_tick_loc)
        axs[0].set_yticklabels(pixels_y_rounded[::step])
        axs[0].set_xlabel("Pixel no.")
        axs[0].set_ylabel("Wavelength / nm")

        #INTEGRATED IMAGE
        intensities = np.sum(img, axis=1)
        axs[1].plot(intensities, np.arange(0, img.shape[0]))
        #axs[1].set_yticks(y_tick_loc)
        #axs[1].set_yticklabels(pixels_y_rounded[::step], rotation='vertical')
        #axs[1].set_yticks([])
        axs[1].invert_yaxis()
        axs[1].set_xlabel("Intensity")
        axs[1].set_ylabel("Wavelength / nm")
        
        fig.suptitle(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        fig.tight_layout()
        plt.show()


class OrcaImageManager(ImageManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, std_data=None):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, std_data)

    def plot(self, step:int=100):
        
        # INITIALIZE IMAGE AND AXES FROM DATA
        img = self.shot_data["DATA"]
        space_mm_x = self.shot_data["X"]
        time_ns_y = self.shot_data["Y"]
        
        # ROUND THE TIME VALUES FOR CLEANER PLOTTING
        time_ns_y_rounded = [f"{time:.2f}" for time in time_ns_y]

        fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(16,8))
        
        x_ticks_pos = np.arange(0, len(space_mm_x), step=step)
        y_ticks_pos = np.arange(0, len(time_ns_y), step=step)
        x_ticks = space_mm_x[::step]
        y_ticks = time_ns_y_rounded[::step]

        ######################
        # PLOT THE RAW IMAGE #
        ######################
        axs[0].imshow(img, aspect='auto')
        axs[0].set_xlabel("Distance / mm")
        axs[0].set_ylabel("Time / ns")
        axs[0].set_yticks(y_ticks_pos)
        axs[0].set_yticklabels(y_ticks)
        axs[0].set_xticks(x_ticks_pos)
        axs[0].set_xticklabels(x_ticks, rotation=90)
        axs[0].set_title("Raw Image")

        ###########
        # LINEOUT #
        ###########
        lineout_y = np.sum(img, axis=1)
        axs[1].plot(lineout_y, time_ns_y)
        axs[1].set_ylabel("Time / ns")
        axs[1].set_xlabel("Summed intensity")
        axs[1].set_title("Lineout (Sum Along Spatial Coords)")
        axs[1].invert_yaxis()

        ################################
        # FOURIER TRANSFORM OF LINEOUT #
        ################################ 
        N = len(lineout_y)
        dt = time_ns_y[1] - time_ns_y[0]
        freq = rfftfreq(N, d=dt)
        intensity = np.abs(rfft(lineout_y))
        axs[2].plot(intensity, freq)
        axs[2].set_ylabel("Freq / GHz")
        axs[2].set_xlabel("Intensity")
        axs[2].set_title("Fourier Transform of Lineout")
        axs[2].invert_yaxis()
        
        fig.suptitle(f"Data from {self.DEVICE_NAME}, Shot No {self.shot_no}, \n{self.label}")
        fig.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space at the top (5%)
        plt.show()