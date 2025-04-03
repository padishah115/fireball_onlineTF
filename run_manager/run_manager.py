##################################################################################################
# CLASS CONTROLLING THE RUN- IDEA IS TO WRAP ALL DATA COLLECTION INTO A SINGLE RUN_MANAGER CLASS #
##################################################################################################

from devices.device import Device

class RunManager:
    """Manages the run during data collection."""

    def __init__(self, devices:list[Device]):
        """
        
        Parameters
        ----------
            devices : list[Device]
                List of devices that we want to gather diagnostic information from.
        
        """

        self.devices = devices
        return 0
    
    def run(self,):
        
        for device in self.devices:
            device.analyse()

