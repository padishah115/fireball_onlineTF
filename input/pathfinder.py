######################################################################################################
# SCRIPT WHICH BUILDS DICTIONARIES OF DATA PATHS FOR SHOTS. IDEA IS THAT THIS TAKES SOME INPUT .CSV, #
#  EITHER ONE PER INSTRUMENT OR FROM ONE MASTER.CSV, AND THEN CONVERTS TO SOME DICTIONARY FORMAT     #
#  APPROPRIATE FOR USE IN THE MAIN CODE.                                                             #
######################################################################################################

# !!!!!!!!!! THIS SHOULD BE THE ONLY FILE IN THE PROJECT WITH HARD-CODED VALUES, WHICH ARE THE PATHS TO THE .CSV FILES !!!!!!!!

# MODULE IMPORTS
import pandas as pd

# .csv for camerafiles
camera_timestamp_csv_path = './example_data/HRMT64_timestamps_shots_camerafiles.csv' # !!!!!!! HARDCODED !!!!!!!
camera_timestamp_df = pd.read_csv(camera_timestamp_csv_path, delimiter=',')

class PathFinder:
    """Class responsible for scraping .csv files which contain information about the storage location of data for all equipment across all shots."""

    def __init__(self, timestamp_csv_path):
        """
        Parameters
        ----------
            timestamp_path : str
                Path to the .csv file containing information about where all data has been stored for each shot.
        """

        # OBJECT'S CSV PATH. I'VE SHORTENED THIS FOR CLARITY, AND BY THIS POINT THERE
        #  SHOULD BE NO AMBIGUITY ABOUT WHICH .CSV THIS IS.
        self.csv_path = timestamp_csv_path

    def _find_shots(self):
        """Scrape through the specified .csv looking to see which shots actually happened."""
        pass

