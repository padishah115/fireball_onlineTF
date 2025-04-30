import os
import pandas as pd
from typing import Dict, List

###################################################################
# FUNCTIONS WHICH CREATE DATA PATH DICTIONARIES FROM THE SHOT LOG #
###################################################################

class DictManager:
    """Class handling the creation of data path dictionaries from the shot log."""
    
    def __init__(self, 
                 shot_nos:List[int],
                 data_path:str, 
                 device_folders:List[str], 
                 template_fnames:Dict[str, str], 
                 shotlog_path:str):
        """
        
        Parameters
        ----------
        shot_nos : List[int]
            List of (integer) shot numbers whose data we are interested in.
        data_path : str
            Path to the master directory holding all of the data. Folders inside of this directory should look like "SCOPE 1",
            "PLASMA_CAMS" etc.
        device_folders : Dict[str, str]
            Dictionary of folder names, format {Device : Foldername}, where the folder is significant as it contains
            the raw data files for each device in question.
        template_fnames : Dict[str, str]
            Dictionary of template filenames for the data, whose blank spaces we will replace as appropriate.
        shotlog_path : str
            Path to the shotlog _AS A .CSV_ !!!
                
        """
        
        # INITIALIZE SHOT NOS
        self.shot_nos = shot_nos

        # INITIALIZE THE PATH TO THE DATA DIRECTORY
        self.data_path = data_path

        # FOLDERS
        self.device_folders = device_folders

        # Initiate the template filenames dictionary
        self.template_fnames = template_fnames

        # Initialize the path to the shotlog
        self.shotlog_path = shotlog_path

    def run(self)->Dict[Dict[str, str]]:

        ##################
        # ERROR HANDLING #
        ##################

        # Check to make sure that the parent data path actually exists.
        if not os.path.exists(self.data_path):
            raise NotImplementedError("Error: parent data_path doesn't exist.")

        if not os.path.exists(self.shotlog_path):
            raise NotImplementedError("Error: path to shot log not found.")

        # Make sure all of the folders actually exist.
        for folder in self.device_folders:
            new_path = os.path.join(self.data_path, folder)
            if not os.path.exists(new_path):
                raise NotImplementedError(f"Path {new_path} to folder {folder} does not exist.\n")
        
        ############
        # DIGICAMS #
        ############
        digicam3_paths_dict = self._get_HRM_datapaths_dict(
            cam_no=3, 
            gain=, 
            parent_directory=os.path.join(self.data_path, self.device_folders["HRM3"]))
        
        digicam4_paths_dict = self._get_HRM_datapaths_dict(
            cam_no=4,
            gain=,
            parent_directory=os.path.join(self.data_path, self.device_folders["HRM4"])
        )
        
        digicam5_paths_dict = self._get_HRM_datapaths_dict(
            cam_no=5,
            gain=,
            parent_directory=os.path.join(self.data_path, self.device_folders["HRM5"])
        )
        
        digicam6_paths_dict = self._get_HRM_datapaths_dict(
            cam_no=6,
            gain=,
            parent_directory=os.path.join(self.data_path, self.device_folders["HRM6"])
        )
       
        ################
        # SPECTROMETER #
        ################
        andor_paths_dict = self._get_ANDOR_datapaths_dict(
            parent_dir=os.path.join(self.data_path, self.device_folders["ANDOR"])
        )

        #################
        # STREAK CAMERA #
        #################
        orca_paths_dict = self._get_ORCA_datapaths_dict(
            parent_dir=os.path.join(self.data_path, self.device_folders["ORCA"])
        )
        
        ###########################
        # BDOT AND FARADAY PROBES #
        ###########################
        bdot1_paths_dict = self._get_scope_datapaths_dict(
            scope_no=,
            parent_dir=os.path.join(self.data_path, self.device_folders["BDOT1"])

        )
        bdot2_paths_dict = self._get_scope_datapaths_dict(
            scope_no=,
            parent_dir=os.path.join(self.data_path, self.device_folders["BDOT2"])
        )
        fp_paths_dict = self._get_scope_datapaths_dict(
            scope_no=,
            parent_dir=os.path.join(self.data_path, self.device_folders["FARADAY PROBE"])
        )

        # MASTER DICTIONARY
        dict_of_dicts = {
            "HRM3":digicam3_paths_dict,
            "HRM4":digicam4_paths_dict,
            "HRM5":digicam5_paths_dict,
            "HRM6":digicam6_paths_dict,
            "BDOT1":bdot1_paths_dict,
            "BDOT2":bdot2_paths_dict,
            "FARADAY PROBE":fp_paths_dict,
            "ANDOR":andor_paths_dict,
            "ORCA":orca_paths_dict,
        } 
        
        return dict_of_dicts

    ###########
    # CAMERAS #
    ###########

    def _get_HRM_datapaths_dict(self,
                            cam_no:int, 
                            gain:int,
                            parent_directory:str)->Dict[int, str]:
        
        """Creates a dictionary of data paths for the HRMX camera, indexed by shot number- i.e. a dictionary of form
        {SHOT NO : "/path/"}. This is done when the user supplies a list of shot numbers which they're interested in, as well
        as the gain/camera number.
        
        Parameters
        ----------
            shot_nos : List[int]
                List of integer shot numbers whose data we are interested in.
            cam_no : int
                The camera number- this replaces the X in HRMX.
            parent_directory : str
                Parent directory containing all of the .csv files for the device, e.g. parent_dir/Plasma_Cams.

        Returns
        -------
            data_path_dict : Dict[int, str]
                Dictionary of form {shot no : /path/to/data}, containing paths to all of the .csv files
                for the specified shots.

        """

        template_fname : str=self.template_fnames["DIGICAM"]
        shotlog_path : str = self.shotlog_path

        # Check that the path exists
        if not os.path.exists(shotlog_path):
            raise NotImplementedError(f"Shotlog path {shotlog_path} doesn\'t exist.")
        # Check that the path to the shotlog ends in a .csv
        if not shotlog_path.endswith('.csv'):
            raise ValueError(f"Error: shotlog_path should end in .csv, but path provided was {shotlog_path}")

        # Initialize empty data path dictionary
        data_path_dict = {}

        # Open the .csv as a pandas dataframe
        df = pd.read_csv(shotlog_path, delimiter=',')

        #Iterate through the dataframe looking for data corresponding to the specified shot numbers.
        for i, no in enumerate(df["Shot number"]):
            if no in self.shot_nos:
                timestamp = str(df["Global UNIX Timestamp (UTC timezone) of HiRadMat cycle"][i])
                acq_cycle = str(df["Acquisition UNIX Timestamp of HiRadMat cycle (UTC timezone)"][i])

                # INITIALIZE THE NAME OF THE FILE
                fname = template_fname.format(cam_no, gain, timestamp, acq_cycle)

                # CREATE THE NAME OF THE PATH
                path = os.path.join(parent_directory, fname)
                
                data_path_dict[no] = path # add the appropriate data path to the data path dictionary
                # using the shot number as the key.
            
        # Return the path dictionary
        return data_path_dict

    def _get_ANDOR_datapaths_dict(self, 
                                  parent_dir:str,
                                  ):
        pass

    def _get_ORCA_datapaths_dict(self,
                                 parent_dir:str,
                                 ):
        pass

    ##########
    # PROBES #
    ##########

    def _get_scope_datapaths_dict(self,
                                scope_no:str,
                                parent_dir:str)->Dict[int, str]:
        """Creates a datapath dictionary for scopes, taking the scope number as input.
        
        Parameters
        ----------
            scope_no : int
                The scope number- this replaces the X in CX_SCOPE_X.
            parent_directory : str
                Parent directory containing all of the .csv files for the device, e.g. parent_dir/Plasma_Cams.

        Returns
        -------
            data_path_dict : Dict[int, str]
                Dictionary of form {shot no : /path/to/data}, containing paths to all of the .csv files
                for the specified shots.
        """

        template_fname:str=self.template_fnames["PROBE"],
        shotlog_path:str=self.shotlog_path

        # Check that the shotlog path exists.
        if not os.path.exists(shotlog_path):
            raise NotImplementedError(f"Shotlog path {shotlog_path} doesn\'t exist.")
        # Check that the path to the shotlog ends in a .csv
        if not shotlog_path.endswith('.csv'):
            raise ValueError(f"Error: shotlog_path should end in .csv, but path provided was {shotlog_path}")
        
        # Initialize data path dictionary
        data_path_dict = {}

        # Open the .csv as a pandas dataframe
        df = pd.read_csv(shotlog_path, delimiter=',')

        #Iterate through the dataframe looking for data corresponding to the specified shot numbers.
        for no in enumerate(df["Shot number"]):
            if no in self.shot_nos:
                acquisition_no = df["Scope1 Trace"]

                # INITIALIZE THE FILE NAME FROM THE TEMPLATE
                fname = template_fname.format(scope_no, scope_no, acquisition_no)

                # CREATE PATH TO FILE
                path = os.path.join(parent_dir, fname)

                data_path_dict[no] = path # add the path to the data path dictionary, using the shot number as the key.

        # Return the path dictionary.
        return data_path_dict