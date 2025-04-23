import numpy as np
import pandas as pd
from typing import List, Tuple
from scipy.fft import fft, fft2

##############################
# TO BE MOVED TO RUN MANAGER #
##############################

# COMMON TO EVERYTHING
#class Data:
def bkg_subtraction(raw_arr:np.ndarray, bkg_arr:np.ndarray)->np.ndarray:
    """Subtracts some background array from some raw data array."""
    corrected_array = np.subtract(raw_arr, bkg_arr)
    return corrected_array

def lineout(array:np.ndarray, axis:int)->Tuple[np.ndarray, np.ndarray]:
    """Sums along given array axis."""
    if axis + axis == axis:
        pixels_1D = np.arange(0, array.shape[1], 1)
    else:
        pixels_1D = np.arange(0, array.shape[0], 1)
    lineout = np.sum(array, axis=axis)
    return lineout, pixels_1D

def arrays_stats(arrays:List[np.ndarray])->Tuple[np.ndarray,np.ndarray]:
    stack = arrays[0]

    for arr in arrays[1:]:
        stack = np.stack([stack, arr], axis=0)

    #Array of mean values
    mean_arr = np.multiply(np.sum(stack, axis=0), 1/len(arrays))
    #Array of std values
    std_arr = np.std(stack, axis=0)

    return mean_arr, std_arr

def FFT(array):
    fft_dict = {
        1:fft,
        2:fft2
    }
    return fft_dict[len(array.shape)](array)

#class Image(Data):
def load_digicam_image(path:str)->np.ndarray:
    """Loads image object from .csv given by DigiCam"""
    #Remove top row and first column, as this is coordinate data
    img = np.loadtxt(path, delimiter=',', skiprows=1)
    img = np.delete(img, 0, axis=1)
    return img


#class Probe(Data):
def load_scope_voltages(path:str, volt_key="Ampl", skiprows=4):
    voltages = pd.read_csv(path, skiprows=skiprows)[volt_key]
    return voltages

def load_scope_times(path:str, time_key = "Time", skiprows = 4):
    times = pd.read_csv(path, skiprows=skiprows)[time_key]
    return times

#######################################
# TO BE MOVED INTO OPERATIONS MANAGER #
#######################################

#Steal code from my demos notebooks.
#High-level functions for plotting- to be moved into 
def plot_img(img:np.ndarray):
    pass

def average_some_things_and_plot():
    pass

def subtract_two_things_which_may_or_may_not_be_averaged_and_plot():
    pass

def lineout_one_thing_could_be_anything_and_plot():
    pass

def fourier_transform_one_thing():
    pass

def fit_some_gaussian_to_some_image_corrected_or_not_and_plot():
    pass