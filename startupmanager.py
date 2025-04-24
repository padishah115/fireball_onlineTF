from typing import List, Dict, Tuple
import numpy as np
import pandas as pd

from device_methods import *
from stats import arrays_stats

class StartupManager:
    """Class responsible for loading data for specified shots at runtime. This is responsible,
    in the main function, for producing dictionaries of experimental shot data, background shot data, and
    background-corrected shot data."""

    def __init__(self, 
                 device_type:str, 
                 exp_shot_nos:List[int], 
                 bkg_shot_nos:List[int], 
                 data_paths_dict:Dict[int, str]):
        """
        Parameters
        ----------
            device_type : str
                The type of device (either "IMAGE" or "PROBE") for which we are handling data. This allows
                the runmanager to deal both with 2D arrays (images) and oscilloscope data.
            exp_shot_nos : List[int]
                List of integers denoting the "experimental" shot numbers which we are interested in. The name
                "experimental" is meant to distinguish between these shots and the background shots.
            bkg_shot_nos : List[int]
                List of integers denoting the shot numbers corresponding to the "background" shot data. This allows 
                the StartupManager to process the background differently from the experimental shot data (i.e. average)
                it.
            data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT NO : /path/to/shot/data} keeping track of where the data for each shot number
                is stored.
        """
        
        # INITIALIZE DEVICE TYPE SO THAT WE KNOW WHETHER WE ARE LOADING PROBE DATA OR IMAGE DATA.
        self.device_type = device_type

        # LIST OF EXPERIMENTAL (I.E. NON-BACKGROUND) SHOTS WHOSE DATA WE ARE PROCESSING
        self.exp_shot_nos = exp_shot_nos

        # LIST OF BACKGROUND SHOT NUMBERS - THESE ARE SHOTS OVER WHOM WE WANT TO TAKE AN AVERAGE
        # BEFORE SUBTRACTION
        self.bkg_shot_nos = bkg_shot_nos
        
        # DICTIONARY KEYED BY SHOT NUMBER, WITH VALUES CORRESPONDING TO THE PATHS TO THE DATA
        # FOR BOTH BACKGROUND AND EXPERIMENTAL SHOTS
        self.data_paths_dict = data_paths_dict
        

    def load(self)->Tuple[Dict[int, np.ndarray], Dict[int, np.ndarray], Dict[int, np.ndarray]]:
        """Loads dictionaries of indexed experimental, background, and background-corrected data. Each of these
        three dictionaries returned by the function is of the form {SHOT NO : np.ndarray}, where the
        np.ndarray is the data itself.
        
        Returns
        -------
            raw_data_dict : Dict[int, np.ndarray]
                Dictionary containing indexed experimental shot data, where the keys are the experimental shot
                numbers, and the values are the actual data in np.ndarray form.
            bkg_data_dict : Dict[int, np.ndarray]
                Dictionary containing indexed background shot data, where the keys are the background shot
                numbers, and the values are the actual background data in np.ndarray form.
            corrected_data_dict : Dict[int, np.ndarray]
                Dictionary containing indexed backgroud-CORRECTED shot data, where the keys correspond to the
                experimental shot numbers, and the values are the data itself after background subtraction.
                N.B.: the background subtraction is done using an arithmetic mean of the background images
                which are supplied to the startup manager.
        """


        #CHECK TO SEE WHICH DEVICE_TYPE WE ARE DEALING WITH- SHOULD BE EITHER IMAGE OR PROBE
        
        #########
        # IMAGE #
        #########
        if self.device_type == "IMAGE":
            #IF IMAGE, THEN HAVE TO DEAL WITH 2D DATA
            raw_data_dict = self.IMAGE_load_shots(shot_nos=self.exp_shot_nos, data_paths_dict=self.data_paths_dict)
            bkg_data_dict = self.IMAGE_load_shots(self.bkg_shot_nos, self.data_paths_dict)
            #Take average of background data to produce single background
            bkg_images = [bkg_data_dict[shot] for shot in bkg_data_dict.keys()]
            averaged_bkg = arrays_stats(bkg_images)[0]
        
        #########
        # PROBE #
        #########
        elif self.device_type == "PROBE":
            #IF PROBE, HAVE TO DEAL WITH THE OSCILLOSCOPE DATA
            
            # {Shot no : Experimental (raw) data}
            exp_data_dict = self.PROBE_load_all_shots(self.exp_shot_nos, self.data_paths_dict)
            
            # {Shot no : Background data}
            bkg_data_dict = self.PROBE_load_all_shots(self.bkg_shot_nos, self.data_paths_dict)
            
            # PRODUCE LIST OF VOLTAGES FROM BACKGROUND OSCILLOSCOPE TRACES, AND THEN PASS TO 
            # ARRAYS_STATS METHOD TO PRODUCE BACKGROUND AVERAGE
            bkg_voltages = [datum["VOLTAGES"] for datum in bkg_data_dict.values()]
            #Take average of background data to produce single background
            averaged_bkg = arrays_stats(bkg_voltages)[0]
        
        # RAISE ERROR IF USER SPECIFIES AN ERRONEOUS DEVICE_TYPE
        else:
            raise ValueError(f"Warning: device type '{self.device_type}' not valid- device_type must be either\
                             'IMAGE' or 'PROBE'.")
        

        ##########################
        # BACKGROUND SUBTRACTION #
        ##########################
        # Subtract mean background image from the experimental shot data to produce dictionary of
        # corrected shot data
        
        # DICTIONARY OF FORM {EXP_SHOT_NO : BACKGROUND_CORRECTED_DATA}
        corrected_data_dict = {}
        for shot_no in self.exp_shot_nos:
            corrected_data = self.bkg_subtraction(raw_arr=exp_data_dict[shot_no], bkg_arr=averaged_bkg)
            corrected_data_dict[shot_no] = corrected_data

        return raw_data_dict, bkg_data_dict, corrected_data_dict
    
    
    def bkg_subtraction(self, raw_arr:np.ndarray, bkg_arr:np.ndarray)->np.ndarray:
        """Subtracts some background array from some raw data array.
        
        Parameters
        ----------
            raw_arr:np.ndarray
                The "raw" image array, from whom some background is meant to be subtracted.
            bkg_arr:np.ndarray
                The "background" image array, which will be subtracted from the raw array.

        Returns
        -------
            corrected_array : np.ndarray
                raw_arr - bkg_arr = corrected_array.
        """
        corrected_array = np.subtract(raw_arr, bkg_arr)
        return corrected_array

    ################################################################################
    # HELPER FUNCTIONS TO LOAD DATA FROM .CSV FILES PRODUCED BY OSCILLOSCOPES/CAMS #
    ################################################################################

    ##########
    # IMAGES #
    ##########

    # this is where we HARDCODE all the lovely, idiosyncratic ways in which different cameras store
    # image data.
    
    def load_digicam_image(self, path:str)->np.ndarray:
        """Loads image object from .csv given by DigiCam. Due to the way that the DigiCams store image data,
        the first column and first row have to be removed, as these contain coordinate information about the
        pixels.
        
        Parameters
        ----------
            path : str
                The path to the raw .csv file where the DigiCam image is stored.
        
        Returns
        -------
            img : np.ndarray
                The image as a numpy array after being loaded from the .csv, and after having its first column and
                first row trimmed.
        """
        
        #Remove top row and first column, as this is coordinate data
        img = np.loadtxt(path, delimiter=',', skiprows=1)
        img = np.delete(img, 0, axis=1)
        
        return img
    
    def load_ORCA_image(self):
        pass

    def load_ANDOR_image(self):
        pass

    ##########
    # PROBES #
    ########## 

    def load_scope_voltages(self, path:str, volt_key:str="Ampl", skiprows:int=4):
        """Loads voltage data from oscilloscope .csv at a specified path, in the form of an arraylike list.
        
        Parameters
        ----------
            path : str
                Path to the .csv where the oscilloscope has stored voltage/time data, from which we load voltage data.
            volt_key : str = "Ampl"
                Column title for the voltage information in the oscilloscope dataframe
            skiprows : int = 4
                Due to the strange way in which the LECROY 'scopes dump data, the top 4 rows have to be skipped over.
        """
    
        if not path.endswith('.csv'):
            raise ValueError(f"Warning: oscilloscope files should be .csv type, but path provided ends in {path[:-4]}.")

        # READ AND RETURN THE VOLTAGES FROM APPROPRIATE COLUMN IN THE PANDAS DATAFRAME
        voltages = pd.read_csv(path, skiprows=skiprows)[volt_key]
        return voltages

    
    def load_scope_times(self, path:str, time_key = "Time", skiprows = 4):
        """Loads time data from oscilloscope .csv at a specified path, in the form of an arraylike list.
        
        Parameters:
        -----------
            path : str
                Path to the .csv where the oscilloscope has stored voltage/time data, from which we load voltage data.
            time_key : str = "Time"
                Column title for the time information in the oscilloscope dataframe
            skiprows : int = 4
                Due to the strange way in which the LECROY 'scopes dump data, the top 4 rows have to be skipped over.
        """

        # READ AND RETURN TIMES FROM APPROPRIATE COLUMN IN PANDAS DATAFRAME
        times = pd.read_csv(path, skiprows=skiprows)[time_key]
        return times

    ##################################################################
    # WRAPPER METHODS FOR LOADING SEVERAL SHOTS' DATA SIMULTANEOUSLY #
    # ESSENTIALLY CONVERT DATA PATH DICTS TO DATA DICTS              #
    ##################################################################
    
    # IMAGE MANAGER

    def IMAGE_load_shots(self, shot_nos:List[int], data_paths_dict:Dict[int, str])->Dict[int, np.ndarray]:
        """Loads multiple shots' images sequentially, using the data_paths_dict to dynamically select paths to
        different shot numbers' raw data files.
        
        Parameters
        ----------
            shot_nos : List[int]
                List of shot numbers for whom we would like to find and load image data.
            data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT NO : /PATH/TO/DATA} from which we can dynamically adjust our 
                search for the shot data for different shot numbers.
        
        Returns
        -------
            image_dict : Dict[int, np.ndarray]
                Dictionary of form {SHOT_NO : image_data (np.ndarray)} format. We can therefore view this function
                as one which converts the data_paths_dict to a data_dict where the dictionary values are now the data
                itself rather than the paths to the data.
        """
        
        # INITIALIZE EMPTY DICTIONARY OF FORM {SHOT NO : DATA (NP.NDARRAY)}
        image_dict = {}
        
        # ITERATE THROUGH SPECIFIED SHOT NUMBERS. THESE COULD CORRESPOND TO BACKGROUND SHOTS
        # OR EXPERIMENTAL (RAW) SHOTS
        for shot_no in shot_nos:
            #LOCATE SHOT'S DATA PATH FROM THE DATA_PATHS_DICT
            data_path = data_paths_dict[shot_no]

            # STORE THE DATA ITSELF FOR EACH SHOT IN THE IMAGE_DICT ARRAY
            # IMAGE DICT ARRAY HAS FORMAT {SHOT_NO : DATA (NP.NDARRAY)}
            # WARNING- WANT TO UPGRADE THIS TO ACCOUNT FOR DIFFERENT CAMERA TYPES
            image_dict[shot_no] = self.load_digicam_image(data_path) 

        return image_dict

    # PROBE MANAGER

    def PROBE_load_all_shots(self, shot_nos:List[int], data_paths_dict:Dict[int, str])->Dict[int, Dict[str, np.ndarray]]:
        """Loads multiple shots' oscilloscope data sequentially, using the data_paths_dict to dynamically select paths to
        different shot numbers' raw data files. Similar to the IMAGE_LOAD_ALL_SHOTS method above, but now the dictionary is
        a dictionary of dictionaries.
        
        Parameters
        ----------
            shot_nos : List[int]
                List of shot numbers for whom we would like to find and load oscilloscope data.
            data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT NO : /PATH/TO/DATA} from which we can dynamically adjust our 
                search for the shot data for different shot numbers.
        
        Returns
        -------
            scope_data_dict : Dict[int, Dict[str, np.ndarray]]
                Dictionary of dictionaries, of format {SHOT_NO : {"VOLTAGES": [voltage data], "TIMES" : [time data]}}.
                This is different to the image loader, where we want to store only one piece of data per shot number.
                Eventually, I could look at replacing this with a np.stack rather than a nested dictionary.
        
        """

        # DICTIONARY WHICH WILL ULTIMATELY BE OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        scope_data_dict = {}

        #ITERATE THROUGH SPECIFIED SHOT NUMBERS, AND APPEND DATA TO SCOPE_DATA_DICT
        for shot_no in shot_nos:
            # ACCESS PATH TO SHOT'S DATA USING DATA_PATH_DICT
            data_path = data_paths_dict[shot_no]

            #VOLTAGE DATA
            scope_data_dict[shot_no]["VOLTAGES"] = self.load_scope_voltages(data_path)
            
            #TIME DATA
            scope_data_dict[shot_no]["TIMES"] = self.load_scope_times(data_path)
        
        #RETURN THE DICTIONARY OF DICTIONARIES OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        return scope_data_dict
    
    
    