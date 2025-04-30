import numpy as np
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt

# STATISTICS 
def img_arrays_stats(data_dict_list:List[Dict])->Tuple[Dict, Dict]:
    """Performs statistical calculation on some list of arraylike objects,
    returning mean and standard deviation information.
    
    Paramters
    ---------
        data_dict_list : List[Dict]
            List of the data dictionaries over whom we want to perform statistical calculations.
    
    Returns
    -------
        mean_arr : np.ndarray
            Array which encodes mean data at each position.
        std_arr : np.ndarray
            Array which encodes std at each position.
    """

    #Initialize stack using the first array in the list
    stack = data_dict_list[0]["DATA"]
    stack = np.expand_dims(stack, axis=0)

    # Expand all of the arrays along a new dimension, 0, which will serve to index the 
    # different shot nos' arrays
    stack_list = [np.expand_dims(d["DATA"], axis=0) for d in data_dict_list]
    stack = np.concatenate(stack_list, axis=0) #join along 0 axis

    #Array of mean values, produced by calculating mean across axis 0
    mean_arr = np.multiply(np.sum(stack, axis=0), 1/len(data_dict_list))
    #Array of std values, produced by calculating std across axis 0
    std_arr = np.std(stack, axis=0)

    mean_data = {
        "DATA": mean_arr, 
        "X": data_dict_list[0]["X"], 
        "Y": data_dict_list[0]["Y"]
    }

    std_data = {
        "DATA":std_arr,
        "X": data_dict_list[0]["X"],
        "Y": data_dict_list[0]["Y"]
    }

    return mean_data, std_data


