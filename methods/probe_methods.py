#################
# PROBE CLASSES #
#################

class Probe():
    """Probe parent device class for dealing with field data as a function of time. This is relevant for the BDot and Faraday Probes.
    
    Things the probe parent class must do:
        -Subtract background data (multiple background images)
        -Show voltage v time traces
        -Average traces over multiple shots and get mean/std. information
    """
