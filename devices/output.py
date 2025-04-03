# OUTPUT CLASS THAT KEEPS TRACK OF WHAT TYPE OF EXTENSION IS NEEDED BY EACH MEASUREMENT ETC

################
# PARENT CLASS #
################

class Output:

    def __init__(self, name, data_path, save_extension):
        """
        Parameters 
        ----------
            name : str
                Name of the output measurement
            data_path : str
                Path to the where the output is dumped by the beamlog
            save_extension : str
                File extension that we would like once we save the data
        """
        
        self.name = name
        self.data_path = data_path
        self.save_extension = save_extension

    def __str__(self):
        pass

    def analyze(self):
        operation = 2+2

        self.analysis = operation
        return 0
    
    def save_analysis(self, save_path):
        """Saves the analysis """
        def save():
            return 0
        
        save(self.analysis)