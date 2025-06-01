from utils.loadmanager.loadmanager import LoadManager
from nptdms import TdmsFile
import pandas as pd

class LDVLoadManager(LoadManager):
    
    def __init__(self, input, data_paths_dict):
        super().__init__(input, data_paths_dict)
        self.data_dict = {}

    def load(self)->dict:
        """Loading function for LDV and Strain Gauge Data.
        
        Returns
        -------
            self.data_dict
                Dictionary of shot data for all the specified shots. This is of the form {Shot NO: Shot Data Dict}
        """

        # EXTRACT SHOT NUMBERS AND SHOT DATA PATHS IN ITERABLE FORM
        shot_nos = [shot_no for shot_no in self.input["EXP_SHOT_NOS"]]
        shot_paths = [self.data_paths_dict[shot_no] for shot_no in shot_nos]

        for i, shot_no in enumerate(shot_nos):
            self.data_dict[shot_no] = self._load_ldv_data(shot_paths[i])
            
        return self.data_dict
    
    def _load_ldv_data(self, path)->dict:
        """Loads the LDV data in appropriate format. We have channels for time, LDV position, LDV speed, central gauge strain,
        and downstream gauge strain."""

        shot_data_dict = {}

        tdms_data_manager = TdmsDataManager(path)
        pretrigger_df, df_in_s, trigger_dataframes = tdms_data_manager.data_slice_by_time(
            acq_duration_s = 30,
            pre_trigger_duration_s = 0.040,
            remove_period_s=0.00025,
            time_windows=[5, 10, 20, 30]
        )
        first_window_high_freq = trigger_dataframes[0]

        shot_data_dict["PRETRIGGER_DF"] = pretrigger_df
        shot_data_dict["DF_IN_S"] = df_in_s
        shot_data_dict["TRIGGER_DATAFRAMES"] = trigger_dataframes
        shot_data_dict["FIRST_WINDOW_HIGH_FREQ"] = first_window_high_freq
        shot_data_dict["DISPLACEMENT_RANGE"] = tdms_data_manager.displacement_range
        shot_data_dict["VELOCITY_RANGE"] = tdms_data_manager.velocity_range
        shot_data_dict["ELONGATION_RANGE"] = tdms_data_manager.elongation_range

        return shot_data_dict



class TdmsDataManager():
    """Class to help us manage and lock up some of the data from the TDMS file."""
    
    def __init__(self, tdms_path):
        """Initialization function for the TdmsDataManger. Takes the tdmsfile object as input.
        
        Parameters
        ----------
            tdms_path
                The path to the tdms file.
        """

        #Initialize the tdms file object inside the datamanager class
        self.tdms_path = tdms_path
        self.df = self.tdms_to_dataframe()

        self.displacement_range = []
        self.velocity_range = []
        self.elongation_range = ['20', 'um'] # Default range for strain gauges in um
        self.strain_voltage_to_elongation_gain = 2  # Gain for the strain gauge voltage to elongation conversion [um/V]

   
        

    def tdms_to_dataframe(self):
        """Converts raw data in the tdms into a dataframe format.
        
        Returns
        -------
            df : Dataframe containing all of the relevant data from the tdms file.
        """

        with TdmsFile.open(self.tdms_path) as tdms_file:
            tdms_group = tdms_file["LDV_SG"]
    
            # Displacement and velocity ranges
            self.displacement_range = tdms_group["ranges"].properties["Displacement Range"].split(" ")
            self.velocity_range = tdms_group["ranges"].properties["Velocity Range"].split(" ")

            try:
                displacement_range = float(self.displacement_range[0])
                velocity_range = float(self.velocity_range[0])
            except ValueError:
                self.displacement_range[0] = '1'
                self.velocity_range[0] = '1'
                self.displacement_range.append("no-unit")
                self.velocity_range.append("no-unit")
    
            #Timestamp channel
            self.timestamp_data = tdms_group["timestamp"][:]
    
            #Displacement channel
            self.displacement_data = tdms_group["POS_LDV"][:]
    
            #Speed channel
            self.speed_data = tdms_group["SPEED_LDV"][:]
    
            #Strain gauge channels
            self.elongation_center_data = tdms_group["StrainGaugeCenter"][:]
            self.elongation_downstream_data = tdms_group["StrainGaugeDownstream"][:]
    
            #Wrap everything i
            columns = ["timestamp", "displacement", "velocity", "elongation_center", "elongation_downstream"]
            data_tuples = list(zip(self.timestamp_data, self.displacement_data, self.speed_data, self.elongation_center_data, self.elongation_downstream_data))
            df = pd.DataFrame(data_tuples, columns=columns)

        return df


    def subtract_epoch(self, dataframe):
        """Converts timestamp column values to time in seconds by zeroing to the initial timestamp.
        
        Parameters
        ----------
            dataframe
                Dataframe whose timestamp column is to be converted.
        Returns
        -------
            dataframe_t_to_s
                Dataframe whose timestamp column has been converted to seconds.
        """

        # Subtract initial time value from all timestamps
        dataframe["timestamp"] -= dataframe["timestamp"].iloc[0]
        
        # Rename dataframe column appropriately.
        dataframe_t_to_s = dataframe.rename(columns = {'timestamp': 'time (s)'})
        
        return dataframe_t_to_s

    def slice_data_by_trigger(self, dataframe, acq_time_s, skip_time_s):
        """Cuts the dataframe into pre- and post-trigger data.
        
        Parameters
        ----------
            dataframe
            acq_time_s
            skip_time_s

        Returns
        -------
            trigger_df
            pretrigger_df
        """

        # Calculate the trigger time by adding the skiptime variable to the first timestamp in the original data.
        start_time = dataframe["time (s)"].iloc[0]
        trigger_time = dataframe["time (s)"].iloc[0] + skip_time_s
        
        # Create the trigger dataframe by taking the values between the trigger and acquistion times in the original dataframe
        trigger_df = dataframe[dataframe["time (s)"].between(trigger_time, trigger_time + acq_time_s)] 
        pretrigger_df = dataframe[dataframe["time (s)"].between(start_time, trigger_time)]

        return trigger_df, pretrigger_df

    def add_time_difference_column(self, dataframe):
        """Appends a new column to the dataframe which encodes timestep information, which is important when filtering for important frequencies.
        
        Parameters
        ----------
            dataframe
        returns
            dataframe_copy
        """

        # Copy the dataframe
        dataframe_copy = dataframe.copy()

        # Calculate the time differences by taking the intervals between time in seconds
        time_difference = dataframe_copy["time (s)"].diff()
        time_difference = time_difference.round(5)

        dataframe_copy.loc[:, "time_diff"] = time_difference

        return dataframe_copy
    
    def remove_rows_with_time_diff(self, dataframe, time_diff):
        """Takes the given dataframe and keeps all the lines with a time difference different from the one that needs to be filtered out.

        :param dataframe: The target dataframe
        :type dataframe: dataframe
        :param time_diff: The unwanted time difference. Corresponds to a low-freq acquisition.
        :type time_diff: int
        :return: A dataframe without the unwanted samples.
        :rtype: dataframe
        """
        # Filter out rows where 'time_diff' column is equal to time_diff
        filtered_dataframe = dataframe[dataframe['time_diff'] != time_diff]

        return filtered_dataframe


    def slice_dataframes_by_time_diff(self, dataframe, time_diff):
        """Takes the given dataframe and slices it with the given time difference threshold.

        :param dataframe: The target dataframe
        :type dataframe: dataframe
        :param time_diff: The time difference threshold. If a time diff between samples is bigger, they belong to different sets of data.
        :type time_diff: int
        :return: A list of the dataframes, each corresponding to a high-freq acquisition
        :rtype: list
        """
        # Initialize a list to store DataFrames
        list_of_dataframes = []
        # Initialize a DataFrame to store rows
        current_dataframe = pd.DataFrame(columns=dataframe.columns)

        # Iterate over the dataframe
        for index, row in dataframe.iterrows():
            # Check if the time difference is bigger than 1E-05
            if row['time_diff'] > time_diff:
                # If there are rows in the current dataframe, store it in the list
                if not current_dataframe.empty:
                    list_of_dataframes.append(current_dataframe)
                    # Reset the current dataframe
                    current_dataframe = pd.DataFrame(columns=dataframe.columns)

            # Add the current row to the current dataframe
            current_dataframe.loc[index] = row

        # If there are rows in the current dataframe, store it in the list
        if not current_dataframe.empty:
            list_of_dataframes.append(current_dataframe)

        return list_of_dataframes

    def slice_dataframes_by_time_windows(self, dataframe, time_windows):
        """Takes the given dataframe and slices it with the list of time windows given.

        :param dataframe: The target dataframe
        :type dataframe: dataframe
        :param time_windows: The instants in which a new high-freq acquisition starts
        :type time_windows: list
        :return: A list of the dataframes, each corresponding to a high-freq acquisition
        :rtype: list
        """
        first_window_start = dataframe['time (s)'].iloc[0]
        first_window_finish = first_window_start + 0.005
        second_window_start = time_windows[0]
        second_window_finish = second_window_start + 0.001
        third_window_start = time_windows[1]
        third_window_finish = third_window_start + 0.001
        fourth_window_start = time_windows[2]
        fourth_window_finish = fourth_window_start + 0.001
        fifth_window_start = time_windows[3]
        fifth_window_finish = dataframe['time (s)'].iloc[-1]
        first_window_trigger = dataframe[dataframe['time (s)'].between(first_window_start, first_window_finish)]
        second_window_trigger = dataframe[dataframe['time (s)'].between(second_window_start, second_window_finish)]
        third_window_trigger = dataframe[dataframe['time (s)'].between(third_window_start, third_window_finish)]
        fourth_window_trigger = dataframe[dataframe['time (s)'].between(fourth_window_start, fourth_window_finish)]
        fifth_window_trigger = dataframe[dataframe['time (s)'].between(fifth_window_start, fifth_window_finish)]
        dataframes_list = [first_window_trigger, second_window_trigger, third_window_trigger, fourth_window_trigger,
                           fifth_window_trigger]
        # print(first_window_start, first_window_finish)
        # print(second_window_start, second_window_finish)
        # print(third_window_start, third_window_finish)
        # print(fourth_window_start, fourth_window_finish)
        # print(fifth_window_finish, fifth_window_trigger)
        return dataframes_list

    def scale_volts_to_units(self, dataframe):
        """Takes the given dataframe with raw data and makes use of the ranges stored in attributes to scale it.

        :param dataframe: dataframe with parameters in volts (raw data)
        :type dataframe: dataframe
        :return: scaled dataframe
        :rtype: dataframe
        """
        displacement_range = float(self.displacement_range[0])
        velocity_range = float(self.velocity_range[0])
        # print(dataframe.head())
        # Scale displacement
        dataframe["displacement"] = dataframe["displacement"].apply(lambda x: x / 2 * displacement_range)

        # Scale velocity
        dataframe["velocity"] = dataframe["velocity"].apply(lambda x: x / 2 * velocity_range)
        
        #Scale strain gauges
        dataframe["elongation_center"] = dataframe["elongation_center"].apply(lambda x: x * self.strain_voltage_to_elongation_gain)
        dataframe["elongation_downstream"] = dataframe["elongation_downstream"].apply(lambda x: x * self.strain_voltage_to_elongation_gain)

        return dataframe

    def data_slice_by_time(self, acq_duration_s, pre_trigger_duration_s, remove_period_s, time_windows):
        """Allows the slicing of the acquired data by the known time windows of high-frequency acquisition.
        Also performs all the intermediate steps to convert the tdms to dataframe and divide it into pre and post trigger.

        :param acq_duration_s: duration of acquisition after trigger, in seconds
        :type acq_duration_s: int
        :param pre_trigger_duration_s: duration of pretrigger, in seconds
        :type pre_trigger_duration_s: int
        :param remove_period_s: period of the low-frequency acquisition, in seconds. In other words, time difference between samples.
        :type remove_period_s: int
        :param time_windows: Moments in which a high-frequency acquisition is started, in seconds
        :type time_windows: int
        :return: dataframe of the pretrigger data, dataframe of all the data in seconds (instead of timestamp) and list of the dataframes corresponding to the windows of high-frequency acquired data
        :rtype: dataframe, dataframe, list of dataframes
        """
        full_df = self.tdms_to_dataframe()
        full_df = self.scale_volts_to_units(full_df)
        df_in_s = self.subtract_epoch(full_df)
        trigger_df, pretrigger_df = self.slice_data_by_trigger(df_in_s, acq_duration_s, pre_trigger_duration_s)
        trigger_df = self.add_time_difference_column(trigger_df)
        trigger_df = self.remove_rows_with_time_diff(trigger_df, remove_period_s)
        trigger_df = self.add_time_difference_column(trigger_df)
        trigger_dataframes = self.slice_dataframes_by_time_windows(trigger_df, time_windows)
        return pretrigger_df, df_in_s, trigger_dataframes

    def data_slice_by_freq(self, acq_time_s, skip_time_s, remove_freq, time_diff):
        """Allows the slicing of the acquired data by detecting the frequency of acquisition of each sample. This is done by checking the time difference with the previous sample.
        Also performs all the intermediate steps to convert the tdms to dataframe and divide it into pre and post trigger.

        :param acq_time_s: duration of acquisition after trigger, in seconds
        :type acq_time_s: int
        :param skip_time_s: duration of pretrigger, in seconds
        :type skip_time_s: int
        :param remove_freq: period of the low-frequency acquisition, in seconds. In other words, time difference between samples.
        :type remove_freq: int
        :param time_diff: Time difference threshold 
        :type time_diff: int
        :return: dataframe of the pretrigger data, dataframe of all the data in seconds (instead of timestamp) and list of the dataframes corresponding to the windows of high-frequency acquired data
        :rtype: dataframe, dataframe, list of dataframes
        """
        full_df = self.tdms_to_dataframe()
        full_df = self.scale_volts_to_units(full_df)
        df_in_s = self.substract_epoc(full_df)
        trigger_df, pretrigger_df = self.slice_data_by_trigger(df_in_s, acq_time_s, skip_time_s)
        trigger_df = self.add_time_difference_column(trigger_df)
        trigger_df = self.remove_rows_with_time_diff(trigger_df, remove_freq)
        trigger_df = self.add_time_difference_column(trigger_df)
        trigger_dataframes = self.slice_dataframes_by_time_diff(trigger_df, time_diff)
        return pretrigger_df, df_in_s, trigger_dataframes


        


