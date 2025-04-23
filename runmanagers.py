from typing import List, Dict
import numpy as np

from methods.device_methods import *

# IMAGE MANAGER

def IMAGE_load_shots(shot_nos, data_paths_dict:Dict[int, str])->Dict[int, np.ndarray]:
    image_dict = {}
    for shot_no in shot_nos:
        data_path = data_paths_dict[shot_no]

        # WARNING- WANT TO CHANGE THIS TO DIGICAM=TRUE
        image_dict[shot_no] = load_digicam_image(data_path) 

    return image_dict

# PROBE MANAGER

def PROBE_load_all_shots(shot_nos, 
                         data_paths_dict:Dict[int, str])->Dict[int, Dict[str, np.ndarray]]:
    scope_dict = {}
    for shot_no in shot_nos:
        data_path = data_paths_dict[shot_no]
        scope_dict[shot_no]["VOLTAGES"] = load_scope_voltages(data_path)
        scope_dict[shot_no]["TIMES"] = load_scope_times(data_path)
    return scope_dict