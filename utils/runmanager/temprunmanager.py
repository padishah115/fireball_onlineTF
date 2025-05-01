from utils.runmanager.runmanager import RunManager
from utils.loadmanager.temploadmanager import TempLoadManager
from utils.opmanager.pt100operationsmanager import PT100OperationsManager

class TempRunManager(RunManager):
    def __init__(self, input, data_paths_dict):
        super().__init__(input, data_paths_dict)

    def run(self):

        loadmanager = TempLoadManager(
            input=self.input,
            data_paths_dict=self.data_paths_dict
        )

        # RETURN A DICTIONARY OF FORM {SHOT NO : DATA}        
        data_dict = loadmanager.load()
        shot_nos = data_dict.keys()
        print(shot_nos)

        LABEL = None

        for shot_no in shot_nos:
            opmanager = PT100OperationsManager(
                DEVICE_NAME=self.input["DEVICE_NAME"],
                shot_no=shot_no,
                label=LABEL,
                shot_data=data_dict[shot_no],
                input=self.input,
            )
            print(shot_no)
            opmanager.plot()
