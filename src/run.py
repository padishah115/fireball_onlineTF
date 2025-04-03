#Module imports
import os

#Imports from diagnostics module- this is a little dirty but I think it's OK here.
from devices import *

#Imports from run-manger
from run_manager.run_manager import RunManager

def main():
    
    #Think about passing the devices list from an input/configuration file here instead of passing them one-by-one to a list.
    #Which devices would we like for the run?
    myDevices = []

    myManager = RunManager(
        devices=myDevices
    )

    #Execute the run- call all of the data collection that we want to do.
    myManager.run()


if __name__ == "__main__":
    main()