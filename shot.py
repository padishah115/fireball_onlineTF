
#####################
# SHOT PARENT CLASS #
#####################

class Shot:
    """
    
    Attributes
    ----------
        device_name : str
            Name of the parent device for which the shot has been taken
        shot_index : str
            The index or 'label' telling us what exactly the shot is. E.g. "1" or "DARKFIELD"
        raw_data : device_dependent
            The shot's raw data. This could be voltage vs time, or could be an NDarray encoding image data.

    Methods
    -------
        raw()
            Performs raw data extraction for the shot.
    """

    def __init__(self, device_name, shot_index):
        """
        
        Parameters
        ----------
            shot_index : str
                The index or 'label' telling us what exactly the shot is. E.g. "1" or "DARKFIELD"
            
        """

        # FOR EASE OF LABELLING, TELLS US WHAT THE NAME OF THE DEVICE IS
        self.device_name = device_name

        # INITIALIZE THE SHOT'S INDEX SO THAT WE KNOW HOW TO LABEL THE SHOW
        self.shot_index = shot_index

        # GET THE RAW DATA FOR THE SHOT
        self.raw_data = self.raw()

    def __repr__(self,):
        return f"SHOT NO. : {self.shot_index} | DEVICE: {self.device_name}"
    
    def raw():
        """Returns raw data for the shot"""
        raise NotImplementedError(f"Error: no raw() function implemented for shot")

##########################
# IMAGE SHOT CHILD CLASS #
##########################

class ImageShot(Shot):
    pass

class VoltShot(Shot):
    pass