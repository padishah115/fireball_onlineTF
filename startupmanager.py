from typing import List, Dict, Tuple
import numpy as np
import pandas as pd

from device_methods import *

class StartupManager:

    def __init__(self, device_type, raw_shot_nos, bkg_shot_nos, data_paths_dict):
        
        self.device_type = device_type
        self.raw_shot_nos = raw_shot_nos
        self.bkg_shot_nos = bkg_shot_nos
        self.data_paths_dict = data_paths_dict
        

    def load(self):
        if self.device_type == "IMAGE":
            raw_data_dict = self.IMAGE_load_shots(shot_nos=self.raw_shot_nos, data_paths_dict=self.data_paths_dict)
            bkg_data_dict = self.IMAGE_load_shots(self.bkg_shot_nos, self.data_paths_dict)
            #Take average of background data to produce single background
            bkg_images = [bkg_data_dict[shot] for shot in bkg_data_dict.keys()]
            averaged_bkg = self.arrays_stats(bkg_images)[0]
        elif self.device_type == "PROBE":
            raw_data_dict = self.PROBE_load_all_shots(self.raw_shot_nos, self.data_paths_dict)
            bkg_data_dict = self.PROBE_load_all_shots(self.bkg_shot_nos, self.data_paths_dict)
            bkg_voltages = [datum["VOLTAGES"] for datum in bkg_data_dict.values()]
            #Take average of background data to produce single background
            averaged_bkg = self.arrays_stats(bkg_voltages)[0]
        else:
            raise ValueError(f"Warning: device type '{self.device_type}' not valid.")
        
        #use subtraction function to create appropriate (corrected) images
        corrected_data_dict = {}
        for shot_no in self.raw_shot_nos:
            corrected_data = self.bkg_subtraction(raw_arr=raw_data_dict[shot_no], bkg_arr=averaged_bkg)
            corrected_data_dict[shot_no] = corrected_data

        return raw_data_dict, bkg_data_dict, corrected_data_dict

    #class Image(Data):
    def load_digicam_image(self, path:str)->np.ndarray:
        """Loads image object from .csv given by DigiCam"""
        #Remove top row and first column, as this is coordinate data
        img = np.loadtxt(path, delimiter=',', skiprows=1)
        img = np.delete(img, 0, axis=1)
        return img

    #class Probe(Data):
    def load_scope_voltages(self, path:str, volt_key="Ampl", skiprows=4):
        voltages = pd.read_csv(path, skiprows=skiprows)[volt_key]
        return voltages

    def load_scope_times(self, path:str, time_key = "Time", skiprows = 4):
        times = pd.read_csv(path, skiprows=skiprows)[time_key]
        return times

    # IMAGE MANAGER

    def IMAGE_load_shots(self, shot_nos:List[int], data_paths_dict:Dict[int, str])->Dict[int, np.ndarray]:
        image_dict = {}
        print(shot_nos)
        for shot_no in shot_nos:
            data_path = data_paths_dict[shot_no]

            # WARNING- WANT TO CHANGE THIS TO DIGICAM=TRUE
            image_dict[shot_no] = self.load_digicam_image(data_path) 

        return image_dict

    # PROBE MANAGER

    def PROBE_load_all_shots(self, shot_nos, 
                            data_paths_dict:Dict[int, str])->Dict[int, Dict[str, np.ndarray]]:
        scope_dict = {}
        for shot_no in shot_nos:
            data_path = data_paths_dict[shot_no]
            scope_dict[shot_no]["VOLTAGES"] = self.load_scope_voltages(data_path)
            scope_dict[shot_no]["TIMES"] = self.load_scope_times(data_path)
        return scope_dict
    
    def bkg_subtraction(self, raw_arr:np.ndarray, bkg_arr:np.ndarray)->np.ndarray:
        """Subtracts some background array from some raw data array."""
        corrected_array = np.subtract(raw_arr, bkg_arr)
        return corrected_array
    
    def arrays_stats(self, arrays:List[np.ndarray])->Tuple[np.ndarray,np.ndarray]:
        stack = arrays[0]

        for arr in arrays[1:]:
            stack = np.stack([stack, arr], axis=0)

        #Array of mean values
        mean_arr = np.multiply(np.sum(stack, axis=0), 1/len(arrays))
        #Array of std values
        std_arr = np.std(stack, axis=0)

        return mean_arr, std_arr