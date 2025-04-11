# MODULE IMPORTS
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import pandas as pd

from typing import List, Dict

################
# PARENT CLASS #
################
#  Generic parent class for all outputs from all diagnostics. These outputs could be images, electric fields,
# temperatures, anything. Each Output class comes with a name, the name of the associated Device, and the shot number
# from which the Output is being taken. This allows us to develop single derivative Output classes (e.g. "image") for
# a wide variety of devices that all produce images.

#  The Output parent class also comes with an empty "analyze" function, which must be overwritten by definitions of child 
# classes. This is so that, when working with a Device object containing many Output objects, we can do things such as
# call Devices.output.analyze() for output in Device.outputs, without having to worry about what exactly the analyze()
# function is doing.

class Output:

    def __init__(self, device_name:str, output_name:str, raw_data_path:str, background_paths_dict:Dict[str, str]=None):
        """
        Parameters 
        ----------
            shot_no : int
                The shot number during which the output measurement was taken.
            device_name : str
                The name of the parent device from which the output is being read (e.g. PROBE1)
            output_name : str
                The name of the output itself (e.g. TEMPERATURE1)
            raw_data_path : str
                Path to where the relevant RAW data for the output was dumped during beamtime.
            background_paths_dict : Dict[str, str]
                Paths to different background images (e.g. darkfield, etc.), where the key is the name of the background as a string.
            
        """
        
        self.device_name = device_name
        self.output_name = output_name
        self.raw_data_path = raw_data_path
        self.background_paths_dict = background_paths_dict

        self.raw_data = {}
        self.bkg_data = {}
        

    def __repr__(self):
        return f"{self.output_name} (Output) from {self.device_name}"

    def analyze(self, background_corrections, plots):
        """Call analysis on the image, first getting the RAW data (no background subtraction), followed by the corrected data (with various types of background subtraction).
        
        Parameters
        ----------
            background_corrections : List[str]
                List of the different type of background corrections we want to do.
            plots : bool
                Plotting boolean determining whether data is plotted "on-the-fly" while analysis is being performed.

        Returns
        -------
            self.raw_data : Dict
            self.bkg_data : Dict
        """
        
        # UPDATE THE RAW AND CORRECTED DATA DICTIONARIES
        self.raw(plots=plots) 
        self.corrected(background_corrections=background_corrections, plots=plots)
        
        return self.raw_data, self.bkg_data

    def raw(self, plots):
        """Empty placeholder function which plots the raw data without background subtraction."""
        raise NotImplementedError(f"Error: no raw() method provided for {self}")
    
    def corrected(self, background_corrections, plots):
        """Iterates over all the supplied species of background, and performs relevant background subtraction.
        
        Parameters
        ----------
            background_corrections : List[str]
                List of the different types of background corrections which we want to perform.
            plots : bool
                Plotting boolean determining whether data is plotted "on-the-fly" while analysis is being performed.
        """

        if not self.background_paths_dict == None: #Check to see whether we were actually passed any background images.
            for background_path_key in self.background_paths_dict.keys():
                if background_path_key in background_corrections:
                    bkg_name = background_path_key
                    bkg_path = self.background_paths_dict[bkg_name]
                    self.bkg_data[bkg_name] = self._background_subtracted(bkg_name=bkg_name, bkg_path=bkg_path, plots=plots)

        
        # for bkg_name, bkg_path in self.background_paths_dict.items():
        #     self._background_subtracted(bkg_name=bkg_name, bkg_path=bkg_path)
        #     bkg_subtracted

    def _background_subtracted(self, bkg_name, bkg_path, plots):
        """Empty placeholder function for background subtraction."""
        raise NotImplementedError(f"Error: no background_subtracted() method provided for {self}")


#########
# IMAGE #
#########
#  Derivative of the Output class for IMAGES, i.e. relevant for all cameras who produce a bitmap image
# during beamtime. This will be relevant for cameras 3&4, which image the upstream and downstream chromox
# screens (e+/e- number estimations), and cameras 5&6, which image the chromox screens placed after the dipole
# magnet (e+/e- energy estimations).

class Image(Output):
    """Class for outputs that take the form of images."""

    def __init__(self, device_name:str, output_name:str, raw_data_path:str, background_paths_dict:Dict[str, str]=None, lognorm=True):
        """
            device_name : str
                The name of the parent device that the image output is being passed to. Note
                that, due to the fact that multiple instruments pass images as outputs, it's necessary to 
                specify the camera name.
            output_name : str
                The name of the image output- what exactly are we looking at?
            raw_data_path : str
                Path to the raw image data.
            background_paths_dict : Dict[str, str]
                Paths to different background images (e.g. darkfield, etc.), where the key is the name of the background as a string.
            lognorm : bool
                Determines whether we want to use logarithmic normalisation when depicting the image data.
        
        """

        # INITIALIZE BASE CLASS
        super().__init__(device_name, output_name, raw_data_path, background_paths_dict)

        # INITIALIZE RAW IMAGE DATA, CONVERTING FROM .CSV TO NUMPY ARRAY
        self.raw_image_array = np.nan_to_num(np.genfromtxt(self.raw_data_path, delimiter=','), nan=0)
        
        # FIND MIN AND MAX PIXEL VALUES FOR NORMALIZATION
        self.raw_pmax = np.nanmax(self.raw_image_array) # RAW pixel intensity maximum
        self.raw_pmin = np.nanmin(self.raw_image_array) # RAW pixel intensity minimum
        
        # BOOLEAN DETERMINING WHETHER THE IMAGES ARE PLOTTED WITH LOGARITHMIC NORMALIZATION
        self.lognorm = lognorm

    def __repr__(self):
        """Representation dunder method."""
        return super().__repr__() # MAINTAIN SAME __repr__ AS BASE CLASS
    
    def raw(self, plots):
        """Returns raw data without any background subtraction.
        
        Parameters
        ----------
            plots : bool
                Boolean governing whether we want the raw data to be plotted.

        Returns
        -------
            raw : Dict
        """
    
        if plots:
            # Plot the bitmap of the captured image.
            plt.title(f"Raw Image Capture from {self.device_name}\n (No Background Subtraction)")
            
            # Check whether we are using logarithmic normalization, and plot image appropriately.
            if self.lognorm:
                print(f'pmax: {self.raw_pmax}, pmin: {self.raw_pmin}')
                normalization = LogNorm()
                plt.imshow(self.raw_image_array, norm=normalization)
            else:
                plt.imshow(self.raw_image_array)
            
            plt.show()

        self.raw_data = {
            "RAW_IMAGE" : self.raw_image_array
        }


    def _background_subtracted(self, bkg_name:str, bkg_path:str, plots:bool):
        """Subtracts the background image from the raw image.
        
        Parameters
        ----------
            bkg_name : str
                The name of the type of background that is being subtracted (i.e. "BEAM OFF", "DARKFIELD", etc.)

            bkg_path : str
                Path to the specified background image data.

            plots : bool
                Boolean determining whether we want to plot the background-subtracted images "on-the-fly" as analysis is being performed.

        Returns
        -------
        """
        
        # LOAD THE BACKGROUND IMAGE FROM .CSV AND SUBTRACT FROM RAW IMAGE.
        background_array = np.nan_to_num(np.genfromtxt(bkg_path, delimiter=','), nan=0.0)

        if self.raw_image_array.shape == background_array.shape:
            corrected_image = np.subtract(self.raw_image_array, background_array)
            
            #Produce new pixel minima and maxima from the corrected image.
            corr_pmax = np.nanmax(corrected_image)
            corr_pmin = np.nanmin(corrected_image)

            if plots:
                # Plot the bitmap of the captured image.
                plt.title(f"Image Capture from {self.device_name}\n ({bkg_name}-Subtracted)")
                
                # Check whether we are using logarithmic normalization, and plot image appropriately.
                if self.lognorm:
                    print(f'pmax: {corr_pmax}, pmin: {corr_pmin}')
                    normalization = LogNorm()
                    plt.imshow(corrected_image, norm=normalization)
                else:
                    plt.imshow(corrected_image)
                
                plt.show()

            return corrected_image

        else:
            print(f"Warning: for {self.device_name}, {bkg_name} background image and raw image do not have matching dimensions. Correction NOT performed.")
            return None
        


##################
# ELECTRIC FIELD #
##################
#  This is the derivative of the Output class for the Electric Field read by an oscilloscope trace.
# This will be relevant for the bdot probes, as well as for the faraday probes.

class eField(Output):
    """Class for electric field/voltage readouts from an oscilloscope trace."""

    def __init__(self, 
                 device_name:str, 
                 output_name:str="E Field", 
                 raw_data_path:str="", 
                 background_paths_dict:Dict[str, str]=None,
                 time_units:str="s", 
                 voltage_units:str="V", 
                 time_key:str='Time', 
                 voltage_key:str='Ampl',
                 skiprows:int = 4,
                 ):
        """

        Parameters
        ----------
            device_name : str
                The name of the parent device from which the output is being read (e.g. PROBE1)
            output_name : str
                The name of the output itself (e.g. E Field)
            raw_data_path : str
                The path to the location containing RAW data for the electric field.
            background_paths_dict : Dict[str, str]
                Paths to different background images (e.g. darkfield, etc.), where the key is the name of the background as a string.
            time_units : str
                Units in which time is measured by the device_name.
            voltage_units : str
                Units in which the electric field is measured.
            time_key : str
                The key used to label time information in the .csv. Default is 'Time'.
            voltage_key : str
                The key used to label electric field information in the .csv. Default is 'Ampl'.
            skiprows : int
                Due to the ugly nature of the LECROY oscilloscope outputs, we have to skip over some of the initial lines.
        """

        # CALL INIT FUNCTION ON OUTPUT BASE CLASS
        super().__init__(device_name=device_name, output_name=output_name, raw_data_path=raw_data_path, background_paths_dict=background_paths_dict)
        
        # SPECIFY UNITS IN WHICH TIME AND ELECTRIC FIELD ARE MEASURED BY THE device_name
        self.time_units = time_units
        self.voltage_units = voltage_units
        
        # SPECIFY THE KEYS USED FOR TIME AND ELECTRIC FIELD DATA IN THE .CSV FILE
        self.time_key = time_key
        self.voltage_key = voltage_key

        # HOW MANY ROWS IN THE .CSV DO WE NEED TO SKIP IN ORDER TO ACCOMMODATE THE WEIRD LECROY OUTPUT
        self.skiprows = skiprows

        self.raw_scope_data = pd.read_csv(self.raw_data_path, skiprows=self.skiprows)
        self.time = self.raw_scope_data[self.time_key] # time data from .csv
        self.raw_voltage = self.raw_scope_data[self.voltage_key] # electric field 

        #INITIALIZE DATA DICTIONARIES
        self.raw_data = {
            f"TIME/{self.time_units}" : self.time
        }
        self.bkg_data = {
            f"TIME/{self.time_units}" : self.time
        }


    def __repr__(self):
        """Representation dunder method."""
        return super().__repr__() #MAINTAIN SAME REPRESENTATION AS OUTPUT BASE CLASS
    
    def raw(self, plots:bool):
        """Returns the trace from an oscilloscope, without any background corrections.

        Parameters
        ----------
            plots : bool
                Boolean determining whether we want the raw oscilloscope trace to be plotted "on-the-fly" as analysis is performed.

        Returns
        -------
            raw : Dict[str, array]
                Raw data dictionary containing both the time and voltage information
        """

        if not self.raw_data_path.endswith('.csv'):
            raise ValueError(f"Error: expected .csv file for eField data for {self}, but got {self.raw_data_path}")

        if plots:
            plt.title(f'Oscilloscope trace from {self.device_name}')
            plt.ylabel(f'Voltage / {self.voltage_units}')
            plt.xlabel(f'Time / {self.time_units}')
            plt.plot(self.time, self.raw_voltage)
            plt.show()

        self.raw_data[f"VOLTAGE/{self.voltage_units}"] = self.voltage_units


    def _background_subtracted(self, bkg_name:str, bkg_path:str, plots:bool):

        # LOAD BACKGROUND SCOPE TRACE AND RECOVER VOLTAGE DATA
        print(f"BACKGROUND PATH : {bkg_path}")
        bkg_scope_data = pd.read_csv(bkg_path, skiprows=self.skiprows)
        bkg_voltage = bkg_scope_data[self.voltage_key]

        # PERFORM BACKGROUND SUBTRACTION
        corrected_voltage = np.subtract(self.raw_voltage, bkg_voltage)

        if plots:
            plt.title(f'Electric Field from {self.device_name}\n ({bkg_name}-SUBTRACTED)')
            plt.ylabel(f'Electric Field / {self.voltage_units}')
            plt.xlabel(f'Time / {self.time_units}')
            plt.plot(self.time, corrected_voltage)
            plt.show()
        
        return corrected_voltage

        

