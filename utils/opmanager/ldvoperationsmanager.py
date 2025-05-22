from utils.opmanager.operationsmanager import OperationsManager

from nptdms import TdmsFile
import matplotlib.pyplot as plt

class LDVOperationsManager(OperationsManager):
    
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data = None):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)

    def plot(self):
        """Produces plots for LDV data- this includes the position and velocity of the LDV data as a function of time, as well as upstream and central
        strain gauge readings. We produce these as 2x2 plots."""

        #######################################
        # LOAD DATA FROM SHOT DATA DICTIONARY #
        #######################################

        # TIME IN SECONDS
        times = self.shot_data["timestamp"]

        # DISPLACEMENT OF THE LDV IN UM
        ldv_position = self.shot_data["POS_LDV"]

        # LDV VELOCITY IN MM/S
        ldv_speed = self.shot_data["SPEED_LDV"]
        
        # STRAIN GAUGE READINGS IN PPM
        strain_gauge_center = self.shot_data["StrainGaugeCenter"]
        strain_gauge_downstream = self.shot_data["StrainGaugeDownstream"]

        fig, axs = plt.subplots(2, 2, figsize=(16,9))

        # LDV POSITION VS TIME
        axs[0, 0].plot(times, ldv_position)
        axs[0, 0].set_title("LDV Position")
        axs[0, 0].set_xlabel("Time / s")
        axs[0, 0].set_ylabel("Displacement / um")
        axs[0, 0].grid()

        # LDV SPEED VS TIME
        axs[0,1].plot(times, ldv_speed)
        axs[0, 1].set_title("LDV Velocity")
        axs[0, 1].set_xlabel("Time / s")
        axs[0, 1].set_ylabel("Velocity / mm s^-1")
        axs[0, 1].grid()
        
        # CENTRAL GAUGE POSITION VS TIME
        axs[1,0].plot(times, strain_gauge_center)
        axs[1, 0].set_title("Strain Gauge (Center)")
        axs[1, 0].set_xlabel("Time / s")
        axs[1, 0].set_ylabel("Strain / ppm")
        axs[1, 0].grid()
        
        # DOWNSTREAM GAUGE POSITION VS TIME
        axs[1,1].plot(times, strain_gauge_downstream)
        axs[1, 1].set_title("Strain Gauge (Downstream)")
        axs[1, 1].set_xlabel("Time / s")
        axs[1, 1].set_ylabel("Strain / ppm")
        axs[1, 1].grid()

        fig.suptitle("LDV and String Gauge Data")
        fig.tight_layout()
        plt.show()
