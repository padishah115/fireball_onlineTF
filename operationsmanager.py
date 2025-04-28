import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import List, Dict
from scipy.fft import rfft, rfftfreq
#from stats import arrays_stats

class OperationsManager:
    """Class responsible for performing more advanced analysis and arithmetic on the shot data, including
    but not limited to fourier transforms and lineout calculations."""

    def __init__(self, DEVICE_NAME, shot_no, label, shot_data:np.ndarray):
        """
        Parameters
        ----------
            DEVICE_NAME : str
                The name of the device (e.g. "Synchro" etc.), which is used only for producing labelled plotting
                information.
            shot_no : int
                The shot number corresponding to the data on which the operations are being performed. This
                is used again for clarity in the plot labels.
            label : str
                Additional information, provided by user, about the shot.
            shot_data : np.ndarray
                The shot data, array form, on which we want to perform some specified
                operations
        """

        # INITIALIZE INFORMATION WHICH WE BE USEFUL FOR DISPLAYING THE DATA TO THE USER.
        self.DEVICE_NAME = DEVICE_NAME
        self.shot_no = shot_no
        self.label = label

        # THE RAW DATA ITSELF IN NP.NDARRAY FORMAT
        self.shot_data = shot_data

    def plot(self):
        raise NotImplementedError(f"Warning: no plotting method implemented for {self}")
    
    def average_shots(self, data_list):
        raise NotImplementedError(f"Warning: no averaging method implemented for {self}")
    
    def chromox_fit(self):
        raise NotImplementedError(f"Warning: no chromox_fit method implemented for {self}")
        
    

# IMAGE MANAGER

class ImageManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)
    
    def average_shots(data_list:List[Dict[str, np.ndarray]]):
        """Performs statistical average (mean) over a supplied list of shots. Note
        that the data list of shots is now a list of dictionaries, which for images
        will look like {"DATA": []}, and for probes will look like {"DATA": {"X":[], "Y":[]}}.
        
        Parameters
        ----------
            data_list : List[Dict[str, np.ndarray]]
                List containing the data which we want to average over. 

        Returns
        -------
            mean_arr : np.ndarray
                The averaged array ALONE (no x or y data)
        
        """
        
        # INITIALIZE A STACK OF IMAGE DATA IN ARRAY FORMAT
        array_stack = data_list[0]["DATA"]

        #STACK SUCCESSIVE SHOT IMAGE DATA ALONG THE 0 AXIS
        for dict in data_list[1:]:
            array_stack = np.stack([array_stack, dict["DATA"]], axis=0)
        
        #PERFORM SUM AND THEN AVERAGE OVER SHOTS (I.E. OVER 0 AXIS)
        sum_arr = np.sum(array_stack, axis=0)
        mean_arr = np.multiply(sum_arr, 1/len(data_list))

        return mean_arr
    


class DigicamImageManager(ImageManager):
    """Specialized ImageManager for Chromox camaeras."""

    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)


    def plot(self):
        """Plotting method for the Chromox cameras. We will display the raw image with or without centroid fitting,
        as well as lineouts across both axes."""

        #INITIALIZE THE X AND Y AXES CORRECTLY.
        X = self.shot_data["X"]
        Y = self.shot_data["Y"]
        image = self.shot_data["DATA"]
        extent = [X[0], X[-1], Y[0], Y[-1]]
        
        # GET LINEOUTS
        lineout_x = np.sum(image, axis=0) # x lineout
        lineout_y = np.sum(image, axis=1) # y lineout

        # GET MOMENTS OF THE IMAGE
        mu, sigma = self._get_moments(image, pixels_x=X, pixels_y=Y)
        
        
        #initialize figure
        fig = plt.figure(figsize=(16,8))

        gs = gridspec.GridSpec(nrows=2, ncols=2, wspace=0.3, hspace=0.3, 
                               #width_ratios=[], 
                               #height_ratios=[]
                               )

        #########
        # IMAGE #
        #########
        #ax1 = fig.add_axes(rect=[0., 0.05, 0.5, 0.5])
        ax1 = fig.add_subplot(gs[1,0])
        ax1.imshow(image, extent=extent, aspect='auto')
        ax1.set_xlabel("x / mm")
        ax1.set_ylabel("y / mm")
        
        #PLOT CENTROID AS A DOT
        ax1.scatter(mu[0], mu[1], label=f'mu=[{mu[0]:.2f}, {mu[1]:.2f}]', color='m')
        
        # PLOT STD LINES IN BOTH DIMENSIONS
        y0 = mu + [0, sigma[1]]
        y1 = mu - [0, sigma[1]]
        x0 = mu + [sigma[0], 0]
        x1 = mu - [sigma[0], 0]
        ax1.plot([x0[0], x1[0]], [x0[1], x1[1]], color='m', linestyle='--', label=f'sigma_x: {sigma[0]:.2f}')
        ax1.plot([y0[0], y1[0]], [y0[1], y1[1]], color='m', linestyle='--', label=f'sigma_y: {sigma[1]:.2f}')
        ax1.legend()
        
        ##############
        # X lineouts #
        ##############
        #ax2 = fig.add_axes(rect=[0., 0., 0.5, 0.08])
        ax2 = fig.add_subplot(gs[0,0], sharex=ax1)
        ax2.plot(X, lineout_x)
        ax2.set_title("X Lineout")
        ax2.set_ylabel("Intensity")
        ax2.set_xlabel("x / mm")
        
        ##############
        # Y lineouts #
        ##############
        #ax3 = fig.add_axes(rect=[0.52, 0.1, 0.08, 0.4])
        ax3 = fig.add_subplot(gs[1,1], sharey=ax1)
        ax3.plot(lineout_y[::-1], Y)
        ax3.set_title("Y Lineout")
        ax3.set_xlabel("Intensity")
        ax3.set_ylabel("y / mm")

        # SHOW THE FIGURE
        fig.suptitle(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        fig.tight_layout()
        plt.show()
        

    
    def _get_moments(self, img, pixels_x, pixels_y):
            """Calculates the first and second moments"""

            thresh = 0.2
            max_intensity = np.max(img)
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
        


class AndorImageManager(ImageManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)

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
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)

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


# PROBE MANAGER

class ProbeManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)

    def plot(self):
        time = self.shot_data["DATA"]["TIMES"]
        voltages = self.shot_data["DATA"]["VOLTAGES"]

        #Calculate number of bin centres, and the time spacing of the 'scope
        N = len(voltages)
        dt = time[1]-time[0]

        # FREQ AND INTENSITY
        fft_time = rfftfreq(N, d=dt)
        fft_voltages = np.abs(rfft(voltages))

        fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16,9))

        # REAL DOMAIN
        axs[0].plot(time, voltages)
        axs[0].set_ylabel("Voltage / V")
        axs[0].set_xlabel("Time / s")
        axs[0].set_title("Real Domain")

        #FREQUENCY DOMAIN
        axs[1].plot(fft_time, fft_voltages)
        axs[1].set_ylabel("Amplitude")
        axs[1].set_xlabel("Frequency / Hz")
        axs[1].set_title("Fourier Domain")

        fig.suptitle(f"Oscilloscope Trace from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        plt.show()

    def average_shots(self, shot_data_list, shot_nos):
        
        times = shot_data_list[0]["DATA"]["TIMES"]
        voltage_stack = shot_data_list[0]["DATA"]["VOLTAGES"]

        for data in shot_data_list[1:]:
            voltage_stack = np.stack([voltage_stack, data["VOLTAGES"]], axis=0)

        voltage_sum = np.sum(voltage_stack, axis=0)
        voltage_avg = np.multiply(voltage_sum, 1/len(shot_data_list))

        plt.plot(times, voltage_avg)
        plt.title(f"Oscilloscope Averaged Over Shots {shot_nos}")
        plt.show()
