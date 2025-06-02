# File containing bandpass filter methods for LDV analysis

import scipy

def butter_bandpass(low_cut, high_cut, fs, order=5):
    """Creates a Butterworth bandpass filter.
    :param low_cut: The lower cutoff frequency
    :type low_cut: float
    :param high_cut: The higher cutoff frequency
    :type high_cut: float
    :param fs: The sampling frequency
    :type fs: float
    :param order: The order of the filter
    :type order: int
    :return: The filter coefficients (b, a)
    :rtype: tuple
    """

    return scipy.signal.butter(order, [low_cut, high_cut], fs=fs, btype='band')


def butter_bandpass_filter(data, low_cut, high_cut, fs, order=5):
    """Applies a Butterworth bandpass filter to the given data.
    :param data: The data to be filtered
    :type data: array-like
    :param low_cut: The lower cutoff frequency
    :type low_cut: float
    :param high_cut: The higher cutoff frequency
    :type high_cut: float
    :param fs: The sampling frequency
    :type fs: float
    :param order: The order of the filter
    :type order: int
    :return: The filtered data
    :rtype: array-like
    """
    b, a = butter_bandpass(low_cut, high_cut, fs, order=order)
    y = scipy.signal.lfilter(b, a, data)
    return y