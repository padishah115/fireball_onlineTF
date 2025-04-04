# OUTPUT CLASS THAT KEEPS TRACK OF WHAT TYPE OF EXTENSION IS NEEDED BY EACH MEASUREMENT ETC

# MODULE IMPORTS
import matplotlib.pyplot as plt
import pandas as pd

################
# PARENT CLASS #
################

class Output:

    def __init__(self, device_name, name):
        """
        Parameters 
        ----------
            
            name : str
                Name of the output measurement
        """
        
        self.device_name = device_name
        self.name = name

    def __repr__(self):
        return f"{self.name} (Output) from {self.device_name}"

    def analyze(self):
        """Empty placeholder function defining the method by which data is analyzed from a certain device_name's output."""
        pass


##########
# IMAGES #
##########

class Image(Output):
    def __init__(self, device_name, name, data_path):
        super().__init__(device_name, name)
        self.data_path = data_path


##################
# ELECTRIC FIELD #
##################

class eField(Output):
    """Class for electric field/voltage readouts from an oscilloscope trace."""

    def __init__(self, device_name:str, data_path:str, name:str="E Field", t_units:str="s", e_units:str="V", t_key:str='Time', e_key:str='Ampl'):
        """

        Parameters
        ----------
            device_name : str
                The parent device_name string.
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
        """

        #CALL INIT FUNCTION ON OUTPUT BASE CLASS
        super().__init__(device_name, name)

        #PATH TO DATA
        self.data_path = data_path
        
        #SPECIFY UNITS IN WHICH TIME AND ELECTRIC FIELD ARE MEASURED BY THE device_name
        self.t_units = t_units
        self.e_units = e_units
        
        #SPECIFY THE KEYS USED FOR TIME AND ELECTRIC FIELD DATA IN THE .CSV FILE
        self.t_key = t_key
        self.e_key = e_key

        #OVERRIDE ANALYZE FUNCTION WITH PLOT TRACE FUNCTION
        self.analyze = self.plot_trace

    def __repr__(self):
        return super().__repr__() #MAINTAIN SAME REPRESENTATION AS OUTPUT BASE CLASS
    
    def plot_trace(self):
        """Plots the trace from an oscilloscope.
        """

        if not self.data_path.endswith('.csv'):
            raise ValueError(f"Error: expected .csv file for eField data for {self}, but got {self.data_path}")

        scope_data = pd.read_csv(self.data_path)
        t = scope_data[self.t_key]
        v = scope_data[self.e_key]

        plt.title(f'Electric Field from {self.device_name}')
        plt.ylabel(f'Electric Field / {self.e_units}')
        plt.xlabel(f'Time / {self.t_units}')
        plt.plot(t, v)
        plt.show()
