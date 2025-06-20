import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
from utils.loadmanager.loadmanager import LoadManager
from utils.stats.stats import probe_arrays_stats

class ProbeLoadManager(LoadManager):

    def __init__(self, input, data_paths_dict):
        super().__init__(input, data_paths_dict)
        self.channel_nos = [f"{i}" for i in np.arange(1, 5)]

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
        # PROBE #
        #########

        #IF PROBE, HAVE TO DEAL WITH THE OSCILLOSCOPE DATA
        
        # {Shot no : Experimental (raw) data}
        raw_data_dict = self.PROBE_load_shots(self.exp_shot_nos, self.data_paths_dict)
        
        
        if self.input["BACKGROUND_STATUS"] != "RAW":
            bkg_data_dict : Dict = self.PROBE_load_shots(self.bkg_shot_nos, 
                                                self.data_paths_dict,)
        
            mean_bkg, std_bkg = self.get_average_bkg(bkg_data_dict=bkg_data_dict)

            corrected_data_dict = {}
            for shot_no in self.exp_shot_nos:
                corrected_data_dict[shot_no] = {"DATA":{"VOLTAGES":{channel_no:None for channel_no in self.channel_nos}, "TIMES":{}}, "ERROR":{"DATA":{"VOLTAGES":{channel_no:None for channel_no in self.channel_nos}}}}
                for channel_no in self.channel_nos:
                    corrected_voltages = self.bkg_subtraction(raw_arr=raw_data_dict[shot_no]["DATA"]["VOLTAGES"][channel_no],\
                                                           bkg_arr=mean_bkg["DATA"]["VOLTAGES"][channel_no])
                    corrected_data_dict[shot_no]["DATA"]["VOLTAGES"][channel_no] = corrected_voltages 
                    corrected_data_dict[shot_no]["ERROR"]["DATA"]["VOLTAGES"][channel_no] = std_bkg["DATA"]["VOLTAGES"][channel_no]
                
                corrected_data_dict[shot_no]["DATA"]["TIMES"]["TIMES"] = raw_data_dict[shot_no]["DATA"]["TIMES"]["TIMES"]
                corrected_data_dict[shot_no]["DATA"]["TIMES"]["N"] = raw_data_dict[shot_no]["DATA"]["TIMES"]["N"]
                corrected_data_dict[shot_no]["DATA"]["TIMES"]["dt"] = raw_data_dict[shot_no]["DATA"]["TIMES"]["dt"]
        # Background-removal is not done shot-via-shot
        else:
            std_bkg = None
            corrected_data_dict = None

        return raw_data_dict, corrected_data_dict, std_bkg
    
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
    

    def get_average_bkg(self, bkg_data_dict:dict)->np.ndarray:
        """Returns the averaged background as a tensor.
        
        Parameters
        ----------
            bkg_data_dict : dict
                Dictionary containing background data, which has shot numbers as keys and data as values.
        """
        
        # Create list of background data
        bkg_data = [bkg_data_dict[shot] for shot in bkg_data_dict.keys()]

        # Get the mean (first value returned by img_arrays_stats() function
        mean_bkg, std_bkg = probe_arrays_stats(bkg_data)

        return mean_bkg, std_bkg
    

    def _load_scope_voltages(self, data_path:str, skiprows:int=16)->Tuple[np.ndarray, np.ndarray]:
        """Loads voltage data from oscilloscope .csv at a specified path, in the form of an arraylike list.
        
        Parameters
        ----------
            data_path : str
                Path to the .csv where the oscilloscope has stored voltage/time data, from which we load voltage data.
            skiprows : int = 16
                Due to the strange way in which the TEKTRONIX 'scopes dump data, the top 4 rows have to be skipped over.
        """
    
        if not data_path.endswith('.csv'):
            raise ValueError(f"Warning: oscilloscope files should be .csv type, but path provided ends in {data_path[:-4]}.")

        df = pd.read_csv(data_path, skiprows=skiprows)
        column_names = df.columns.values

        # Load the channels' voltage information. First, we want to see how many channels are present.
        voltage_channels = column_names[1:] # scrape out the voltage channel names, 
        voltage_means = {
            channel:np.mean(df[channel]) for channel in voltage_channels
        }

        # Create a list of voltages and sort by channel number
        if self.input["OPERATIONS"]["SUBTRACT_DC_OFFSET"]:
            voltage_corrections = {
                channel:voltage_means[channel] for channel in voltage_channels
            }
        else:
            voltage_corrections = {
                channel:0 for channel in voltage_channels
            }
        
        channel_voltages = {
            channel:np.subtract(df[channel], voltage_corrections[channel]) for channel in voltage_channels 
        }
        channel_voltages = dict(sorted(channel_voltages.items(), key=lambda item : item[0]))


        return [channel_voltages.get(f"CH{i}", np.zeros(len(df))) for i in range(1, 5)]

    
    def _load_scope_times(self, data_path:str, skiprows:int=16)->tuple[np.ndarray, int, float]:
        """Loads time data from oscilloscope .csv at a specified path, in the form of an arraylike list.
        
        Parameters:
        -----------
            data_path : str
                Path to the .csv where the oscilloscope has stored voltage/time data, from which we load voltage data.
            skiprows : int = 16
                Due to the strange way in which the TEKTRONIX 'scopes dump data, the top 16 rows have to be skipped over.

        Returns:
        --------
            times : np.ndarray
                Array of timestamps from the probe data.
            N : int
                The number of samples taken by the scope- this will be used for DFT later on.
            dt : float
                The time step size between samples.
        """

        # READ AND RETURN TIMES FROM APPROPRIATE COLUMN IN PANDAS DATAFRAME
        df = pd.read_csv(data_path)
        
        # Make sure that the N and dt values are legit- otherwise it's reading from a LeCroy scope.
        try:
            N = int(
                df[df.columns.values[1]].iloc[6]
            )
            
            dt = float(
                df[df.columns.values[1]].iloc[5]
            )
        
        except Exception as e:
            raise ValueError(f"Error when reading time data from {data_path}- potentially LeCroy data. {e}")

        # READ AND RETURN TIMES FROM APPROPRIATE COLUMN IN PANDAS DATAFRAME, this time skipping the rows
        df = pd.read_csv(data_path, skiprows=skiprows)
        
        times = df["TIME"]

        return times, N, dt

    ##################################################################
    # WRAPPER METHODS FOR LOADING SEVERAL SHOTS' DATA SIMULTANEOUSLY #
    # ESSENTIALLY CONVERT DATA PATH DICTS TO DATA DICTS              #
    ##################################################################

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
                            "2":[],
                            "3":[],
                            "4":[]
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
                    "VOLTAGES": {"1":None, "2":None, "3":None, "4":None}, 
                    "TIMES": {"TIMES":None, "N":None, "dt":None}
                },
                "ERROR":{
                    "DATA":{
                        "VOLTAGES":{channel_no:None for channel_no in self.channel_nos}
                        }
                }
            }

            # ACCESS PATH TO SHOT'S DATA USING DATA_PATH_DICT
            data_path = data_paths_dict[shot_no]

            #VOLTAGE DATA
            [voltages_1, voltages_2, voltages_3, voltages_4] = self._load_scope_voltages(data_path)
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["1"] = voltages_1
            scope_data_dict[shot_no]["ERROR"]["DATA"]["VOLTAGES"]["1"] = np.zeros_like(voltages_1)

            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["2"] = voltages_2
            scope_data_dict[shot_no]["ERROR"]["DATA"]["VOLTAGES"]["2"] = np.zeros_like(voltages_2)
            
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["3"] = voltages_3
            scope_data_dict[shot_no]["ERROR"]["DATA"]["VOLTAGES"]["3"] = np.zeros_like(voltages_3)

            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["4"] = voltages_4
            scope_data_dict[shot_no]["ERROR"]["DATA"]["VOLTAGES"]["4"] = np.zeros_like(voltages_4)
            
            #TIME DATA
            times, N, dt = self._load_scope_times(data_path)
            scope_data_dict[shot_no]["DATA"]["TIMES"]["TIMES"] = times
            scope_data_dict[shot_no]["DATA"]["TIMES"]["N"] = N
            scope_data_dict[shot_no]["DATA"]["TIMES"]["dt"] = dt
        
        #RETURN THE DICTIONARY OF DICTIONARIES OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        return scope_data_dict