#Module imports
import os

#Homebrew output 
from output import Output

##########################
# DIAGNOSTICS BASE CLASS #
##########################

#Sample device_outputs

Temp1 = Output(
    name="Temp1",
    data_path="/path/to/temp1/data",
    save_extension=".csv"
)

Temp2 = Output(
    name="Temp2",
    data_path="/path/to/temp2/data",
    save_extension=".csv"
)

device_outputs = {
    "Temperature_1" : Temp1,
    "Temperature_2" : Temp2
}

class Device:
    """Parent class for all diagnostic devices on FIREBALL-III.
    
    Attributes
    ----------
        name : str
            The name of the device.
        device_outputs : dict[Output]
            Dictionary of all diagnostics output by the device.
        data_source_path : str
            Path where we want to 
        analysis_save_path : str

    
    """

    def __init__(self, name:str, data_path:str):
        """
        Parameters
        ----------
            name : str
                The name of the diagnostic
                    """
        
        self.name = name
        self.device_outputs = {}

    def analyze(self, save_bool=True):
        for output in self.device_outputs:
            output_save_path = os.path.join(self.analysis_save_path, output, output.extension)
            output.analyze()

            if save_bool:
                output.save_analysis(output_save_path)

    def _scrape(self):
        """Locates data at the specified path"""





class FaradayProbe(Device):
    """Class for """

    def __init__(self, name, data_path:str, ):
        super.__init__(name)