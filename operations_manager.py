class OperationsManager:

    def __init__(self, shot_data, operations):
        """
        Parameters
        ----------
            shot_data : np.ndarray
                The shot data, array form, on which we want to perform some specified
                operations
            operations : List[str]
                List of operations which we would like to perform on the shot
        """

        self.shot_data = shot_data
        self.operations = operations

    def run(self):
        
        if "FFT" in self.operations:
            self.fft(self.shot_data)

        if "PLOT RAW" in self.operations:
            self.plot_raw(self.shot_data)