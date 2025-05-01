import matplotlib.pyplot as plt

from utils.opmanager.operationsmanager import OperationsManager

class PT100OperationsManager(OperationsManager):
    
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data = None):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)

    def plot(self):
        fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(16,9))
        time = self.shot_data["TIME"]
        tnc_cable_temp = self.shot_data["TEMPERATURE"]["TNC"]
        tt61_cable_temp = self.shot_data["TEMPERATURE"]["TT61"]
        p_target_bot_temp = self.shot_data["TEMPERATURE"]["PBOTTOM"]
        p_target_top_temp = self.shot_data["TEMPERATURE"]["PTOP"]
        s_target_temp = self.shot_data["TEMPERATURE"]["S"]

        # CABLE TEMPERATURES
        axs[0,0].plot(time, tnc_cable_temp, label="TNC Cable", color="r")
        axs[0,0].set_ylabel("Temperature / C")
        axs[0,0].set_xticks([])
        axs[0,0].legend()

        axs[0,1].plot(time, tt61_cable_temp, label="TT61 Cable", color="m")
        axs[0,1].legend()
        axs[0,1].set_xticks([])

        # PRIMARY TARGET TEMPERATURES
        axs[1,0].plot(time, p_target_bot_temp, label="Primary Target, Top", color="b")
        axs[1,0].set_ylabel("Temperature / C")
        axs[1,0].set_xticks([])
        axs[1,0].legend()

        axs[1,1].plot(time, p_target_top_temp, label="Primary Target, Bottom", color="c")
        axs[1,1].set_xlabel("Time / s")
        axs[1,1].legend()

        # SECONDARY TARGET TEMPERATURES
        axs[2,0].plot(time, s_target_temp, label="Secondary Target", color="g")
        axs[2,0].set_ylabel("Temperature / C")
        axs[2,0].legend()
        axs[2,0].set_xlabel("Time / s")

        axs[2,1].axis("off")

        fig.suptitle("PT100 Temperature Data", fontsize=20)
        plt.show()