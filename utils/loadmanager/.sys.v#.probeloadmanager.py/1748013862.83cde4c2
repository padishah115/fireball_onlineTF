import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
from utils.loadmanager.loadmanager import LoadManager

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
        # PROBE #
        #########

        #IF PROBE, HAVE TO DEAL WITH THE OSCILLOSCOPE DATA
        
        # {Shot no : Experimental (raw) data}
        exp_data_dict = self.PROBE_load_shots(self.exp_shot_nos, self.data_paths_dict)
        bkg_data_dict = None
        corrected_data_dict = None




        return exp_data_dict, bkg_data_dict, corrected_data_dict
    

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
        
        channel1_voltages = df["CH1"]
        channel2_voltages = df["CH2"]
        channel3_voltages = df["CH3"]
        channel4_voltages = df["CH4"]

        print(f"Lengths: \n1: {len(channel1_voltages)}, 2: {len(channel2_voltages)}, 3: {len(channel3_voltages)}, 4: {len(channel4_voltages)}")

        return channel1_voltages, channel2_voltages, channel3_voltages, channel4_voltages

    
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
            times
            N
            dt
        """

        # READ AND RETURN TIMES FROM APPROPRIATE COLUMN IN PANDAS DATAFRAME
        df = pd.read_csv(data_path)
        N = int(df[df.columns.values[1]][6])
        dt = float(df[df.columns.values[1]][5])
        print("N", N)
        print("dt", dt)

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
                }
            }

            # ACCESS PATH TO SHOT'S DATA USING DATA_PATH_DICT
            data_path = data_paths_dict[shot_no]

            #VOLTAGE DATA
            voltages_1, voltages_2, voltages_3, voltages_4 = self._load_scope_voltages(data_path)
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["1"] = voltages_1
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["2"] = voltages_2
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["3"] = voltages_3
            scope_data_dict[shot_no]["DATA"]["VOLTAGES"]["4"] = voltages_4
            
            #TIME DATA
            times, N, dt = self._load_scope_times(data_path)
            scope_data_dict[shot_no]["DATA"]["TIMES"]["TIMES"] = times
            scope_data_dict[shot_no]["DATA"]["TIMES"]["N"] = N
            scope_data_dict[shot_no]["DATA"]["TIMES"]["dt"] = dt
        
        #RETURN THE DICTIONARY OF DICTIONARIES OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        return scope_data_dict