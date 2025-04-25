import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict
from scipy.fft import fft, fftfreq
from stats import arrays_stats

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

    def lineouts(self, axis:int, ft_interp:str):
        """Computes the lineout of the data, and plots."""
        if axis + axis == axis:
            pixels_1D = np.arange(0, self.shot_data["DATA"].shape[1], 1)
        else:
            pixels_1D = np.arange(0, self.shot_data["DATA"].shape[0], 1)
        
        lineout = np.sum(self.shot_data["DATA"], axis=axis)
        lineout_fft_y = np.abs(fft(lineout))
        freqs = fftfreq(len(lineout), d=1)
        #lineout_fft_x = fft(pixels_1D)


        fig, axs = plt.subplots(nrows=1, ncols=2)

        #real-space plot
        axs[0].plot(pixels_1D, lineout)
        axs[0].set_title("Real Domain")
        
        #fourier-space plot
        axs[1].plot(freqs, lineout_fft_y)
        axs[1].set_title(f"Fourier Domain \n {ft_interp}")
        
        fig.suptitle(f"Axis {axis} Lineout from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        plt.show()
        
    

# IMAGE MANAGER

class ImageManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)
    
    def average_shots(data_list:List[Dict[str, np.ndarray]], shot_nos:List[int]):
        """Performs statistical average (mean) over a supplied list of shots. Note
        that the data list of shots is now a list of dictionaries, which for images
        will look like {"DATA": []}, and for probes will look like {"DATA": {"X":[], "Y":[]}}.
        
        Parameters
        ----------
            data_list : List[Dict[str, np.ndarray]]
                List containing the data which we want to average over. 
            shot_nos : List[int]
                List of the shots over which the average has been performed.
        
        """
        
        # INITIALIZE A STACK OF IMAGE DATA IN ARRAY FORMAT
        array_stack = data_list[0]["DATA"]

        #STACK SUCCESSIVE SHOT IMAGE DATA ALONG THE 0 AXIS
        for dict in data_list[1:]:
            array_stack = np.stack([array_stack, dict["DATA"]], axis=0)
        
        #PERFORM SUM AND THEN AVERAGE OVER SHOTS (I.E. OVER 0 AXIS)
        sum_arr = np.sum(array_stack, axis=0)
        mean_arr = np.multiply(sum_arr, 1/len(data_list))

        plt.imshow(mean_arr)
        plt.title(f"Averaged Image Over Shots {shot_nos}")
        plt.show()

        return mean_arr
    


class DigicamImageManager(ImageManager):
    """Specialized ImageManager for Chromox camaeras."""

    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)


    def plot(self):
        x = self.shot_data["X"]
        y= self.shot_data["Y"]
        extent = [x[0], x[-1], y[0], y[-1]]

        fig, ax = plt.subplots()
        im = ax.imshow(self.shot_data["DATA"], extent=extent)
        ax.set_xlabel("x / mm")
        ax.set_ylabel("y / mm")
        ax.set_title("Chromox Image")
        ax.set_title(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        plt.show()
        

    def chromox_fit(self):
        x = self.shot_data["X"]
        y = self.shot_data["Y"]
        image = self.shot_data["DATA"]
        extent = [x[0], x[-1], y[0], y[-1]]

        mu, sigma = self._get_moments(image, pixels_x=x, pixels_y=y)

        y0 = mu + [0, sigma[1]]
        y1 = mu - [0, sigma[1]]
        x0 = mu + [sigma[0], 0]
        x1 = mu - [sigma[0], 0]

        fig, ax = plt.subplots()
        im = ax.imshow(image, extent=extent, aspect="auto")
        ax.set_xlabel("x / mm")
        ax.set_ylabel("y / mm")
        ax.set_title(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        ax.scatter(mu[0], mu[1], label=f'mu=[{mu[0]:.2f}, {mu[1]:.2f}]', color='m')

        ax.plot([x0[0], x1[0]], [x0[1], x1[1]], color='m', linestyle='--', label=f'sigma_x: {sigma[0]:.2f}')
        ax.plot([y0[0], y1[0]], [y0[1], y1[1]], color='m', linestyle='--', label=f'sigma_y: {sigma[1]:.2f}')

        plt.legend()
        plt.show()

    
    def _get_moments(self, img, pixels_x, pixels_y):
            """Calculates the first and second moments"""

            thresh = 0.2
            max_intensity = np.max(img)
            mu = [0, 0]
            var = [0, 0]

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

    def plot_andor_image(self, step:int=200):
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

        fig, axs = plt.subplots(nrows=1, ncols=2)
        
        # PHYSICAL IMAGE
        axs[0].imshow(img, aspect='auto')
        axs[0].set_yticks(y_tick_loc)
        axs[0].set_yticklabels(pixels_y_rounded[::step])
        axs[0].set_xlabel("Pixel no.")
        axs[0].set_ylabel("Wavelength / nm")

        #INTEGRATED IMAGE
        intensities = np.sum(img, axis=1)
        axs[1].plot(np.arange(0, img.shape[0]), intensities)
        axs[1].set_xticks(y_tick_loc)
        axs[1].set_xticklabels(pixels_y_rounded[::step], rotation='vertical')
        axs[1].set_yticks([])
        axs[1].set_ylabel("Intensity")
        axs[1].set_xlabel("Wavelength / nm")
        
        fig.suptitle(f"Image from {self.DEVICE_NAME}, Shot {self.shot_no} \n {self.label}")
        fig.tight_layout()
        plt.show()


class OrcaImageManager(ImageManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)

    def plot(self):
        img = self.shot_data["DATA"]
        space_mm_x = self.shot_data["X"]
        time_ns_y = self.shot_data["Y"]

        fig, axs = plt.su

# PROBE MANAGER

class ProbeManager(OperationsManager):
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data)

    def plot(self):
        time = self.shot_data["DATA"]["TIMES"]
        voltages = self.shot_data["DATA"]["VOLTAGES"]

        #fft_time = fftfreq(time)
        fft_time = fftfreq(len(voltages), d=1)
        fft_voltages = np.abs(fft(voltages))

        fig, axs = plt.subplots(nrows=1, ncols=2)


        axs[0].plot(time, voltages)
        axs[0].set_ylabel("Voltage")
        axs[0].set_xlabel("Time")
        axs[0].set_title("Real Domain")

        axs[1].plot(fft_time, fft_voltages)
        axs[1].set_ylabel("Amplitude")
        axs[1].set_xlabel("Frequency")
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
