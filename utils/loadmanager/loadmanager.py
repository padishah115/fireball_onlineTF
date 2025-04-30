from typing import List, Dict, Tuple
import numpy as np
import pandas as pd

from utils.stats.stats import img_arrays_stats

class LoadManager:
    """Class responsible for loading data for specified shots at runtime. This is responsible,
    in the main function, for producing dictionaries of experimental shot data, background shot data, and
    background-corrected shot data."""

    def __init__(self, 
                 input:Dict,
                 data_paths_dict:Dict[int, str]):
        """
        Parameters
        ----------
            input : Dict
                The Python dictionary which has been generated via loading the input.json file.
            data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT NO : /path/to/shot/data} keeping track of where the data for each shot number
                is stored.
        """
        
        # INITIALIZE INPUT DICTIONARY
        self.input = input

        # INITIALIZE DEVICE TYPE SO THAT WE KNOW WHETHER WE ARE LOADING _PROBE_ DATA OR _IMAGE_ DATA.
        self.device_type = self.input["DEVICE_TYPE"]

        # LIST OF EXPERIMENTAL (I.E. NON-BACKGROUND) SHOTS WHOSE DATA WE ARE PROCESSING
        self.exp_shot_nos = self.input["EXP_SHOT_NOS"]

        # LIST OF BACKGROUND SHOT NUMBERS - THESE ARE SHOTS OVER WHOM WE WANT TO TAKE AN AVERAGE
        # BEFORE SUBTRACTION
        self.bkg_shot_nos = self.input["BKG_SHOT_NOS"]
        
        # DICTIONARY KEYED BY SHOT NUMBER, WITH VALUES CORRESPONDING TO THE PATHS TO THE DATA
        # FOR BOTH BACKGROUND AND EXPERIMENTAL SHOTS
        self.data_paths_dict = data_paths_dict

        #SEE WHETHER WE WANT TO NORMALIZE THE DATA
        self.norm = self.input["NORM_PLOT"]
        

    def load(self)->Tuple[Dict[int, np.ndarray], Dict[int, np.ndarray], Dict[int, np.ndarray]]:
        """Loads dictionaries of indexed experimental, background, and background-corrected data. Each of these
        three dictionaries returned by the function is of the form {SHOT NO : np.ndarray}, where the
        np.ndarray is the data itself."""
        raise NotImplementedError(f"Error: no load method implemented for {self}.")
    
    

class CamLoadManager(LoadManager):
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
        if self.device_type == "CAMERA":

            #IF IMAGE, THEN HAVE TO DEAL WITH 2D DATA
            exp_data_dict : Dict = self.IMAGE_load_shots(shot_nos=self.exp_shot_nos, 
                                                  data_paths_dict=self.data_paths_dict,
                                                  camera_type=self.input["DEVICE_SPECIES"])
            
            # CHECK TO MAKE SURE THAT WE ACTUALLY WANT BACKGROUND SHOTS TO ENTER THE FRAY
            if self.input["BACKGROUND_STATUS"] != "RAW":
                bkg_data_dict : Dict = self.IMAGE_load_shots(self.bkg_shot_nos, 
                                                    self.data_paths_dict,
                                                    camera_type=self.input["DEVICE_SPECIES"])
            
                averaged_bkg = self.get_average_bkg(bkg_data_dict=bkg_data_dict, key_path=["DATA"])

                corrected_data_dict = {}
                for shot_no in self.exp_shot_nos:
                    corrected_data = self.bkg_subtraction(raw_arr=exp_data_dict[shot_no]["DATA"], bkg_arr=averaged_bkg)
                    corrected_data_dict[shot_no] = {}
                    corrected_data_dict[shot_no]["DATA"] = corrected_data
                    corrected_data_dict[shot_no]["X"] = exp_data_dict[shot_no]["X"]
                    corrected_data_dict[shot_no]["Y"] = exp_data_dict[shot_no]["Y"]
            else:
                bkg_data_dict = None
                corrected_data_dict = None
        
        #########
        # PROBE #
        #########
        elif self.device_type == "PROBE":
            #IF PROBE, HAVE TO DEAL WITH THE OSCILLOSCOPE DATA
            
            # {Shot no : Experimental (raw) data}
            exp_data_dict = self.PROBE_load_shots(self.exp_shot_nos, self.data_paths_dict)
            bkg_data_dict = None
            corrected_data_dict = None

         
        # RAISE ERROR IF USER SPECIFIES AN ERRONEOUS DEVICE_TYPE
        else:
            raise ValueError(f"Warning: device type '{self.device_type}' not valid- device_type must be either \"CAMERA\" or \"PROBE\".")
        
        # CHECK WHETHER WE WANT TO NORMALIZE THE DATA
        

        return exp_data_dict, bkg_data_dict, corrected_data_dict
    
    
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
    

    def get_average_bkg(self, bkg_data_dict:Dict, key_path:List[str])->np.ndarray:
        """Returns the averaged background as a tensor"""

        bkg_data = [bkg_data_dict[shot][key_path] for shot in bkg_data_dict.keys()]
        averaged_bkg = img_arrays_stats(bkg_data)[0]

        return averaged_bkg


    ################################################################################
    # HELPER FUNCTIONS TO LOAD DATA FROM .CSV FILES PRODUCED BY OSCILLOSCOPES/CAMS #
    ################################################################################

    ##########
    # IMAGES #
    ##########

    # this is where we HARDCODE all the lovely, idiosyncratic ways in which different cameras store
    # image data.
    
    def _load_digicam_image(self, path:str)->Tuple[np.ndarray, List, List]:
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
            x_pixels : np.ndarray
                The trimmed top row of the image data, which encodes the x coordinates in mm.
            y_pixels : np.ndarray
                The trimmed first column of the image data, which encodes the y coordinates in mm.
        """
        
        #Remove top row and first column, as this is coordinate data
        img = np.genfromtxt(path, delimiter=',')
        x_coords = img[0, 1:]
        y_coords = img[1:, 0]
        img = img[1:, 1:]
        
        return img, x_coords, y_coords
    
    def _load_ORCA_image(self, path:str):
        """Loads image from ORCA camera, which images OTR. The x dimension
        encodes spatial position in mm, whereas the y dimension gives time in ns."""
        
        img = np.genfromtxt(path)

        #x axis encodes information about space in mm
        space_mm_x = img[0, 1:]

        #y axis encodes information about time in ns
        time_ns_y = img[1:, 0]
        img = img[1:, 1:]

        return img, space_mm_x, time_ns_y


    def _load_ANDOR_image(self, path:str, skipfooter:int=41)->Tuple[np.ndarray, List, List]:
        """Loads an image produced by the ANDOR synchrotron spectroscopy camera from some specified
        path location.
        
        Parameters
        ----------
            path : str
                The path to the image data.
            skipfooter : int = 41
                The number of rows at the bottom of the andor .asc file which we have to skip over

        Returns
        -------
            img : np.ndarray
            pixels_x : List
            wavelengths (aka pixels_y) : List
        """

        image = np.genfromtxt(path, skip_footer=skipfooter)


        #EXTRACT THE FIRST COLUMN, WHICH CONTAIN WAVELENGTHS IN NM- this is "pixels_y"
        wavelengths = image[:, 0]

        #Index the pixels from 0 to the length of the x axis
        pixels_x = np.arange(0, len(image[0]))

        # trim away the first column to remove wavelength data
        image = image[:, 1:]

        return image, pixels_x, wavelengths

    ##########
    # PROBES #
    ########## 

    # MAY HAVE TO MODIFY THESE DEPENDING ON WHETHER WE ARE USING LECROY

    def _load_scope_voltages(self, data_path:str)->Tuple[np.ndarray, np.ndarray]:
        """Loads voltage data from oscilloscope .csv at a specified path, in the form of an arraylike list.
        
        Parameters
        ----------
            data_path : str
                Path to the .csv where the oscilloscope has stored voltage/time data, from which we load voltage data.
            volt_key : str = "Ampl"
                Column title for the voltage information in the oscilloscope dataframe
            skiprows : int = 4
                Due to the strange way in which the LECROY 'scopes dump data, the top 4 rows have to be skipped over.
        """
    
        if not data_path.endswith('.csv'):
            raise ValueError(f"Warning: oscilloscope files should be .csv type, but path provided ends in {data_path[:-4]}.")

        df = pd.read_csv(data_path)
        columns_list = df.columns.values.tolist()

        channel1_voltages = [float(columns_list[-2])] # the column header is the first data point :(
        channel1_voltages += df[columns_list[-2]] # add the rest of the column to the 'scope data

        channel2_voltages = [float(columns_list[-1])] # the column header is the first data point :(
        channel2_voltages += df[columns_list[-1]] # add the rest of the column to the 'scope data

        corr_voltages = np.subtract(channel2_voltages, channel1_voltages)

        return channel1_voltages, channel2_voltages

    
    def _load_scope_times(self, data_path:str):
        """Loads time data from oscilloscope .csv at a specified path, in the form of an arraylike list.
        
        Parameters:
        -----------
            data_path : str
                Path to the .csv where the oscilloscope has stored voltage/time data, from which we load voltage data.
            time_key : str = "Time"
                Column title for the time information in the oscilloscope dataframe
            skiprows : int = 4
                Due to the strange way in which the LECROY 'scopes dump data, the top 4 rows have to be skipped over.
        """

        # READ AND RETURN TIMES FROM APPROPRIATE COLUMN IN PANDAS DATAFRAME
        df = pd.read_csv(data_path)
        columns_list = df.columns.values.tolist()
        # TIME INTERVAL IN SECONDS
        dt = df[columns_list[1]][0]
        # NO OF RECORDING POINTS
        N = int(columns_list[1])

        # Initialize times array using information about the timestep and the number of sampling points
        times = np.multiply(np.arange(0, N-1, step=1), dt)

        return times, N, dt

    ##################################################################
    # WRAPPER METHODS FOR LOADING SEVERAL SHOTS' DATA SIMULTANEOUSLY #
    # ESSENTIALLY CONVERT DATA PATH DICTS TO DATA DICTS              #
    ##################################################################
    
    # IMAGE MANAGER

    def IMAGE_load_shots(self, shot_nos:List[int], data_paths_dict:Dict[int, str], camera_type:str)->Dict[int, np.ndarray]:
        """Loads multiple shots' images sequentially, using the data_paths_dict to dynamically select paths to
        different shot numbers' raw data files.
        
        Parameters
        ----------
            shot_nos : List[int]
                List of shot numbers for whom we would like to find and load image data.
            data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT NO : /PATH/TO/DATA} from which we can dynamically adjust our 
                search for the shot data for different shot numbers.
            camera_type : str
                The type of camera from which we are loading data.
        
        Returns
        -------
            image_dict : Dict[int, np.ndarray]
                Dictionary of form {SHOT_NO : image_data (np.ndarray)} format. We can therefore view this function
                as one which converts the data_paths_dict to a data_dict where the dictionary values are now the data
                itself rather than the paths to the data.
        """

        # DICTIONARY ALLOWING US TO DYNAMICALLY SWAP IMAGE LOADING  
        # METHODS DEPENDING ON THE CAMERA TYPE
        image_loader_function_dict = {
            "DIGICAM":self._load_digicam_image,
            "ORCA":self._load_ORCA_image,
            "ANDOR":self._load_ANDOR_image

        }
        
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
            image_dict[shot_no] = {}
            image_dict[shot_no]["DATA"], image_dict[shot_no]["X"], image_dict[shot_no]["Y"] = \
                image_loader_function_dict[camera_type](data_path)
            


        return image_dict

    # PROBE MANAGER

    def PROBE_load_shots(self, shot_nos:List[int], data_paths_dict:Dict[int, str])->Dict[int, Dict[str, np.ndarray]]:
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
                Dictionary of dictionaries, of format 
                {
                    SHOT_NO : {
                        "VOLTAGES": {
                            "1":[], 
                            "2":[]
                        }, 
                        
                        "TIMES" : {
                            "TIMES":[], 
                            "N":int, 
                            "dt":float
                        }
                    }
                }.
                
                This is different to the image loader, where we want to store only one piece of data per shot number.
                Eventually, I could look at replacing this with a np.stack rather than a nested dictionary.
        
        """

        # DICTIONARY WHICH WILL ULTIMATELY BE OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        scope_data_dict = {}
        

        #ITERATE THROUGH SPECIFIED SHOT NUMBERS, AND APPEND DATA TO SCOPE_DATA_DICT
        for shot_no in shot_nos:
            
            #initialize the shot data dictionary
            scope_data_dict[shot_no] = {
                "DATA":{
                    "VOLTAGES": {"1":None, "2":None}, 
                    "TIMES": {"TIMES":None, "N":None, "dt":None}
                }
            }

            # ACCESS PATH TO SHOT'S DATA USING DATA_PATH_DICT
            data_path = data_paths_dict[shot_no]

            #VOLTAGE DATA
            voltages_1, voltages_2 = self._load_scope_voltages(data_path)
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["1"] = voltages_1
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["2"] = voltages_2
            
            #TIME DATA
            times, N, dt = self._load_scope_times(data_path)
            scope_data_dict[shot_no]["DATA"]["TIMES"]["TIMES"] = times
            scope_data_dict[shot_no]["DATA"]["TIMES"]["N"] = N
            scope_data_dict[shot_no]["DATA"]["TIMES"]["dt"] = dt

            print("N, dt:", N, dt)
        
        #RETURN THE DICTIONARY OF DICTIONARIES OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        return scope_data_dict

class ProbeLoadManager(LoadManager):
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
        if self.device_type == "CAMERA":

            #IF IMAGE, THEN HAVE TO DEAL WITH 2D DATA
            exp_data_dict : Dict = self.IMAGE_load_shots(shot_nos=self.exp_shot_nos, 
                                                  data_paths_dict=self.data_paths_dict,
                                                  camera_type=self.input["DEVICE_SPECIES"])
            
            # CHECK TO MAKE SURE THAT WE ACTUALLY WANT BACKGROUND SHOTS TO ENTER THE FRAY
            if self.input["BACKGROUND_STATUS"] != "RAW":
                bkg_data_dict : Dict = self.IMAGE_load_shots(self.bkg_shot_nos, 
                                                    self.data_paths_dict,
                                                    camera_type=self.input["DEVICE_SPECIES"])
            
                averaged_bkg = self.get_average_bkg(bkg_data_dict=bkg_data_dict, key_path=["DATA"])

                corrected_data_dict = {}
                for shot_no in self.exp_shot_nos:
                    corrected_data = self.bkg_subtraction(raw_arr=exp_data_dict[shot_no]["DATA"], bkg_arr=averaged_bkg)
                    corrected_data_dict[shot_no] = {}
                    corrected_data_dict[shot_no]["DATA"] = corrected_data
                    corrected_data_dict[shot_no]["X"] = exp_data_dict[shot_no]["X"]
                    corrected_data_dict[shot_no]["Y"] = exp_data_dict[shot_no]["Y"]
            else:
                bkg_data_dict = None
                corrected_data_dict = None
        
        #########
        # PROBE #
        #########
        elif self.device_type == "PROBE":
            #IF PROBE, HAVE TO DEAL WITH THE OSCILLOSCOPE DATA
            
            # {Shot no : Experimental (raw) data}
            exp_data_dict = self.PROBE_load_shots(self.exp_shot_nos, self.data_paths_dict)
            bkg_data_dict = None
            corrected_data_dict = None

         
        # RAISE ERROR IF USER SPECIFIES AN ERRONEOUS DEVICE_TYPE
        else:
            raise ValueError(f"Warning: device type '{self.device_type}' not valid- device_type must be either \"CAMERA\" or \"PROBE\".")
        
        # CHECK WHETHER WE WANT TO NORMALIZE THE DATA
        

        return exp_data_dict, bkg_data_dict, corrected_data_dict
    
    
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
    

    def get_average_bkg(self, bkg_data_dict:Dict, key_path:List[str])->np.ndarray:
        """Returns the averaged background as a tensor"""

        bkg_data = [bkg_data_dict[shot][key_path] for shot in bkg_data_dict.keys()]
        averaged_bkg = img_arrays_stats(bkg_data)[0]

        return averaged_bkg


    ################################################################################
    # HELPER FUNCTIONS TO LOAD DATA FROM .CSV FILES PRODUCED BY OSCILLOSCOPES/CAMS #
    ################################################################################

    ##########
    # IMAGES #
    ##########

    # this is where we HARDCODE all the lovely, idiosyncratic ways in which different cameras store
    # image data.
    
    def _load_digicam_image(self, path:str)->Tuple[np.ndarray, List, List]:
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
            x_pixels : np.ndarray
                The trimmed top row of the image data, which encodes the x coordinates in mm.
            y_pixels : np.ndarray
                The trimmed first column of the image data, which encodes the y coordinates in mm.
        """
        
        #Remove top row and first column, as this is coordinate data
        img = np.genfromtxt(path, delimiter=',')
        x_coords = img[0, 1:]
        y_coords = img[1:, 0]
        img = img[1:, 1:]
        
        return img, x_coords, y_coords
    
    def _load_ORCA_image(self, path:str):
        """Loads image from ORCA camera, which images OTR. The x dimension
        encodes spatial position in mm, whereas the y dimension gives time in ns."""
        
        img = np.genfromtxt(path)

        #x axis encodes information about space in mm
        space_mm_x = img[0, 1:]

        #y axis encodes information about time in ns
        time_ns_y = img[1:, 0]
        img = img[1:, 1:]

        return img, space_mm_x, time_ns_y


    def _load_ANDOR_image(self, path:str, skipfooter:int=41)->Tuple[np.ndarray, List, List]:
        """Loads an image produced by the ANDOR synchrotron spectroscopy camera from some specified
        path location.
        
        Parameters
        ----------
            path : str
                The path to the image data.
            skipfooter : int = 41
                The number of rows at the bottom of the andor .asc file which we have to skip over

        Returns
        -------
            img : np.ndarray
            pixels_x : List
            wavelengths (aka pixels_y) : List
        """

        image = np.genfromtxt(path, skip_footer=skipfooter)


        #EXTRACT THE FIRST COLUMN, WHICH CONTAIN WAVELENGTHS IN NM- this is "pixels_y"
        wavelengths = image[:, 0]

        #Index the pixels from 0 to the length of the x axis
        pixels_x = np.arange(0, len(image[0]))

        # trim away the first column to remove wavelength data
        image = image[:, 1:]

        return image, pixels_x, wavelengths

    ##########
    # PROBES #
    ########## 

    # MAY HAVE TO MODIFY THESE DEPENDING ON WHETHER WE ARE USING LECROY

    def _load_scope_voltages(self, data_path:str)->Tuple[np.ndarray, np.ndarray]:
        """Loads voltage data from oscilloscope .csv at a specified path, in the form of an arraylike list.
        
        Parameters
        ----------
            data_path : str
                Path to the .csv where the oscilloscope has stored voltage/time data, from which we load voltage data.
            volt_key : str = "Ampl"
                Column title for the voltage information in the oscilloscope dataframe
            skiprows : int = 4
                Due to the strange way in which the LECROY 'scopes dump data, the top 4 rows have to be skipped over.
        """
    
        if not data_path.endswith('.csv'):
            raise ValueError(f"Warning: oscilloscope files should be .csv type, but path provided ends in {data_path[:-4]}.")

        df = pd.read_csv(data_path)
        columns_list = df.columns.values.tolist()

        channel1_voltages = [float(columns_list[-2])] # the column header is the first data point :(
        channel1_voltages += df[columns_list[-2]] # add the rest of the column to the 'scope data

        channel2_voltages = [float(columns_list[-1])] # the column header is the first data point :(
        channel2_voltages += df[columns_list[-1]] # add the rest of the column to the 'scope data

        corr_voltages = np.subtract(channel2_voltages, channel1_voltages)

        return channel1_voltages, channel2_voltages

    
    def _load_scope_times(self, data_path:str):
        """Loads time data from oscilloscope .csv at a specified path, in the form of an arraylike list.
        
        Parameters:
        -----------
            data_path : str
                Path to the .csv where the oscilloscope has stored voltage/time data, from which we load voltage data.
            time_key : str = "Time"
                Column title for the time information in the oscilloscope dataframe
            skiprows : int = 4
                Due to the strange way in which the LECROY 'scopes dump data, the top 4 rows have to be skipped over.
        """

        # READ AND RETURN TIMES FROM APPROPRIATE COLUMN IN PANDAS DATAFRAME
        df = pd.read_csv(data_path)
        columns_list = df.columns.values.tolist()
        # TIME INTERVAL IN SECONDS
        dt = df[columns_list[1]][0]
        # NO OF RECORDING POINTS
        N = int(columns_list[1])

        # Initialize times array using information about the timestep and the number of sampling points
        times = np.multiply(np.arange(0, N-1, step=1), dt)

        return times, N, dt

    ##################################################################
    # WRAPPER METHODS FOR LOADING SEVERAL SHOTS' DATA SIMULTANEOUSLY #
    # ESSENTIALLY CONVERT DATA PATH DICTS TO DATA DICTS              #
    ##################################################################
    
    # IMAGE MANAGER

    def IMAGE_load_shots(self, shot_nos:List[int], data_paths_dict:Dict[int, str], camera_type:str)->Dict[int, np.ndarray]:
        """Loads multiple shots' images sequentially, using the data_paths_dict to dynamically select paths to
        different shot numbers' raw data files.
        
        Parameters
        ----------
            shot_nos : List[int]
                List of shot numbers for whom we would like to find and load image data.
            data_paths_dict : Dict[int, str]
                Dictionary of form {SHOT NO : /PATH/TO/DATA} from which we can dynamically adjust our 
                search for the shot data for different shot numbers.
            camera_type : str
                The type of camera from which we are loading data.
        
        Returns
        -------
            image_dict : Dict[int, np.ndarray]
                Dictionary of form {SHOT_NO : image_data (np.ndarray)} format. We can therefore view this function
                as one which converts the data_paths_dict to a data_dict where the dictionary values are now the data
                itself rather than the paths to the data.
        """

        # DICTIONARY ALLOWING US TO DYNAMICALLY SWAP IMAGE LOADING  
        # METHODS DEPENDING ON THE CAMERA TYPE
        image_loader_function_dict = {
            "DIGICAM":self._load_digicam_image,
            "ORCA":self._load_ORCA_image,
            "ANDOR":self._load_ANDOR_image

        }
        
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
            image_dict[shot_no] = {}
            image_dict[shot_no]["DATA"], image_dict[shot_no]["X"], image_dict[shot_no]["Y"] = \
                image_loader_function_dict[camera_type](data_path)
            


        return image_dict

    # PROBE MANAGER

    def PROBE_load_shots(self, shot_nos:List[int], data_paths_dict:Dict[int, str])->Dict[int, Dict[str, np.ndarray]]:
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
                Dictionary of dictionaries, of format 
                {
                    SHOT_NO : {
                        "VOLTAGES": {
                            "1":[], 
                            "2":[]
                        }, 
                        
                        "TIMES" : {
                            "TIMES":[], 
                            "N":int, 
                            "dt":float
                        }
                    }
                }.
                
                This is different to the image loader, where we want to store only one piece of data per shot number.
                Eventually, I could look at replacing this with a np.stack rather than a nested dictionary.
        
        """

        # DICTIONARY WHICH WILL ULTIMATELY BE OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        scope_data_dict = {}
        

        #ITERATE THROUGH SPECIFIED SHOT NUMBERS, AND APPEND DATA TO SCOPE_DATA_DICT
        for shot_no in shot_nos:
            
            #initialize the shot data dictionary
            scope_data_dict[shot_no] = {
                "DATA":{
                    "VOLTAGES": {"1":None, "2":None}, 
                    "TIMES": {"TIMES":None, "N":None, "dt":None}
                }
            }

            # ACCESS PATH TO SHOT'S DATA USING DATA_PATH_DICT
            data_path = data_paths_dict[shot_no]

            #VOLTAGE DATA
            voltages_1, voltages_2 = self._load_scope_voltages(data_path)
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["1"] = voltages_1
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["2"] = voltages_2
            
            #TIME DATA
            times, N, dt = self._load_scope_times(data_path)
            scope_data_dict[shot_no]["DATA"]["TIMES"]["TIMES"] = times
            scope_data_dict[shot_no]["DATA"]["TIMES"]["N"] = N
            scope_data_dict[shot_no]["DATA"]["TIMES"]["dt"] = dt

            print("N, dt:", N, dt)
        
        #RETURN THE DICTIONARY OF DICTIONARIES OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        return scope_data_dict
    