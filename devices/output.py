# MODULE IMPORTS
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

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

    def __init__(self, shot_no:int, device_name:str, output_name:str, data_path:str):
        """
        Parameters 
        ----------
            shot_no : int
                The shot number during which the output measurement was taken.
            device_name : str
                The name of the parent device from which the output is being read (e.g. PROBE1)
            output_name : str
                The name of the output itself (e.g. TEMPERATURE1)
            data_path : str
                Path to where the relevant data for the output was dumped during beamtime.
            
        """
        
        self.shot_no = shot_no
        self.device_name = device_name
        self.output_name = output_name
        self.data_path = data_path
        

    def __repr__(self):
        return f"{self.output_name} (Output) from {self.device_name}"

    def analyze(self):
        """Empty placeholder function defining the method by which data is analyzed from a certain device_name's output."""
        pass


#########
# IMAGE #
#########
#  Derivative of the Output class for IMAGES, i.e. relevant for all cameras who produce a bitmap image
# during beamtime. This will be relevant for cameras 3&4, which image the upstream and downstream chromox
# screens (e+/e- number estimations), and cameras 5&6, which image the chromox screens placed after the dipole
# magnet (e+/e- energy estimations).

class Image(Output):
    """Class for outputs that take the form of images."""

    def __init__(self, shot_no:int, device_name:str, output_name:str, data_path:str):
        """
            shot_no : int
                The shot number corresponding to the image output- which shot is the image coming from?
            device_name : str
                The name of the parent device that the image output is being passed to. Note
                that, due to the fact that multiple instruments pass images as outputs, it's necessary to 
                specify the camera name.
            output_name : str
                The name of the image output- what exactly are we looking at?
            data_path : str
                Path to the raw image data.
        
        """

        # INITIALIZE BASE CLASS
        super().__init__(shot_no, device_name, output_name, data_path)

        # OVERRIDE BASE CLASS ANALYZE METHOD
        self.analyze = self.plot_image

    def __repr__(self):
        """Representation dunder method."""
        return super().__repr__() # MAINTAIN SAME __repr__ AS BASE CLASS
    
    def plot_image(self):
        """Plots image data."""
        
        # CONVERT IMAGE FROM .CSV FORMAT TO NUMPY ARRAY
        image_array = np.genfromtxt(self.data_path, delimiter=',')

        #Plot the bitmap of the captured image.
        plt.title(f"Image Capture from {self.device_name}")
        plt.imshow(image_array)
        plt.show()


##################
# ELECTRIC FIELD #
##################
#  This is the derivative of the Output class for the Electric Field read by an oscilloscope trace.
# This will be relevant for the bdot probes, as well as for the faraday probes.

class eField(Output):
    """Class for electric field/voltage readouts from an oscilloscope trace."""

    def __init__(self, 
                 shot_no, 
                 device_name:str, 
                 output_name:str="E Field", 
                 data_path:str="", 
                 t_units:str="s", 
                 e_units:str="V", 
                 t_key:str='Time', 
                 e_key:str='Ampl',
                 skiprows:int = 4,
                 ):
        """

        Parameters
        ----------
            shot_no : int
                The shot number during which the output measurement was taken.
            device_name : str
                The name of the parent device from which the output is being read (e.g. PROBE1)
            output_name : str
                The name of the output itself (e.g. E Field)
            data_path : str
                The path to the location containing data for the electric field.
            t_units : str
                Units in which time is measured by the device_name.
            e_units : str
                Units in which the electric field is measured.
            t_key : str
                The key used to label time information in the .csv. Default is 'Time'.
            e_key : str
                The key used to label electric field information in the .csv. Default is 'Ampl'.
            skiprows : int
                Due to the ugly nature of the LECROY oscilloscope outputs, we have to skip over some of the initial lines.
        """

        # CALL INIT FUNCTION ON OUTPUT BASE CLASS
        super().__init__(shot_no=shot_no, device_name=device_name, output_name=output_name, data_path=data_path)
        
        # SPECIFY UNITS IN WHICH TIME AND ELECTRIC FIELD ARE MEASURED BY THE device_name
        self.t_units = t_units
        self.e_units = e_units
        
        # SPECIFY THE KEYS USED FOR TIME AND ELECTRIC FIELD DATA IN THE .CSV FILE
        self.t_key = t_key
        self.e_key = e_key

        # HOW MANY ROWS IN THE .CSV DO WE NEED TO SKIP IN ORDER TO ACCOMMODATE THE WEIRD LECROY OUTPUT
        self.skiprows = skiprows

        # OVERRIDE ANALYZE FUNCTION WITH PLOT TRACE FUNCTION
        self.analyze = self.plot_trace

    def __repr__(self):
        """Representation dunder method."""
        return super().__repr__() #MAINTAIN SAME REPRESENTATION AS OUTPUT BASE CLASS
    
    def plot_trace(self):
        """Plots the trace from an oscilloscope.
        """

        if not self.data_path.endswith('.csv'):
            raise ValueError(f"Error: expected .csv file for eField data for {self}, but got {self.data_path}")

        scope_data = pd.read_csv(self.data_path, skiprows=self.skiprows)
        t = scope_data[self.t_key]
        v = scope_data[self.e_key]

        plt.title(f'Electric Field from {self.device_name}')
        plt.ylabel(f'Electric Field / {self.e_units}')
        plt.xlabel(f'Time / {self.t_units}')
        plt.plot(t, v)
        plt.show()
