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
        
        #RETURN THE DICTIONARY OF DICTIONARIES OF FORM {SHOT NO : {"VOLTAGES":[VOLTAGE DATA], "TIMES":[TIME DATA]}}
        return scope_data_dict