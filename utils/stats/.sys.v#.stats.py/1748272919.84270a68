import numpy as np
import matplotlib.pyplot as plt

# STATISTICS 
def img_arrays_stats(data_dict_list:list[dict])->tuple[dict, dict]:
    """Performs statistical calculation on some list of arraylike objects,
    returning mean and standard deviation information.
    
    Paramters
    ---------
        data_dict_list : list[dict]
            List of the data dictionaries over whom we want to perform statistical calculations.
    
    Returns
    -------
        mean_data : dict
            Dictionary of data which encodes mean image data.
        std_data : dict
            Dictionary of data which encodes stddev image data.
    """

    #Initialize stack using the first array in the list
    stack = data_dict_list[0]["DATA"]
    stack = np.expand_dims(stack, axis=0)

    # Expand all of the arrays along a new dimension, 0, which will serve to index the 
    # different shot nos' arrays
    stack_list = [np.expand_dims(d["DATA"], axis=0) for d in data_dict_list]
    stack = np.concatenate(stack_list, axis=0) #join along 0 axis

    #Array of mean values, produced by calculating mean across axis 0
    mean_arr = np.multiply(np.sum(stack, axis=0), 1/stack.shape[0])
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


def probe_arrays_stats(data_dict_list:list[dict])->tuple[dict, dict]:
    """Returns mean and standard deviation data for multiple shots, which have been passed to the function via the
    data_dict_list.
    
    Parameters
    ----------
        data_dict_list : list[dict]
            List of data dictionaries across all shots over whom we want to perform statistical calculations.

    Returns
    -------
        mean_data : dict
            Dictionary of averaged shot data over the specified shot numbers.
        std_data : dict
            Dictionary of standard deviation data over the specified shot numbers.
    """

    channel_nos = ["1", "2", "3", "4"]

    # Initialise empty mean and standard deviation data dictionaries.
    mean_data = {
        "DATA":{
            "TIMES":{
                "TIMES":data_dict_list[0]["DATA"]["TIMES"]["TIMES"],
                "N":data_dict_list[0]["DATA"]["TIMES"]["N"],
                "dt":data_dict_list[0]["DATA"]["TIMES"]["dt"],
            },
            "VOLTAGES":{
                channel_no:None for channel_no in channel_nos
            }
        }
    }
    std_data = {
        "DATA":{
            "VOLTAGES":{
                channel_no:None for channel_no in channel_nos
            }
        }
    }


    # Perform statistical calculations (mean and standard deviation) for each of the channels in the 'scope data.
    for channel_no in channel_nos:

        stack_list = [np.expand_dims(a=d["DATA"]["VOLTAGES"][channel_no], axis=0) for d in data_dict_list]
        stack = np.concatenate(stack_list, axis=0)
        
        channel_voltages_mean = np.multiply(np.mean(a=stack, axis=0), 1 / stack.shape[0])
        channel_voltages_stddev = np.std(a=stack, axis=0)

        mean_data["DATA"]["VOLTAGES"][channel_no] = channel_voltages_mean
        std_data["DATA"]["VOLTAGES"][channel_no] = channel_voltages_stddev

    # Return the dictionaries.
    return mean_data, std_data