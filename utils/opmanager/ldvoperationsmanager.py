from utils.opmanager.operationsmanager import OperationsManager
import matplotlib.pyplot as plt
import numpy as np
import scipy
import pywt
import numpy as np
from utils.opmanager.ldv_filters import butter_bandpass, butter_bandpass_filter


class LDVOperationsManager(OperationsManager):
    
    def __init__(self, DEVICE_NAME, shot_no, label, shot_data, input, std_data = None):
        super().__init__(DEVICE_NAME, shot_no, label, shot_data, input, std_data)
        

    def plot(self):
        """Produces plots for LDV data- this includes the position and velocity of the LDV data as a function of time, as well as upstream and central strain gauge readings. We produce these as 2x2 plots."""
        
        # Dataframe for the LDV data before the trigger.
        pretrigger_df = self.shot_data["PRETRIGGER_DF"]

        #Dataframe after conversion of time units to seconds
        df_in_s = self.shot_data["DF_IN_S"]

        # Ranges of displacement, velocity, elongation 
        displacement_range = self.shot_data["DISPLACEMENT_RANGE"]
        velocity_range = self.shot_data["VELOCITY_RANGE"]
        elongation_range = self.shot_data["ELONGATION_RANGE"]
        
        first_window_high_freq = self.shot_data["FIRST_WINDOW_HIGH_FREQ"]


        self.plot_pre_post_trigger(
            pretrigger_df, 
            first_window_high_freq,
            displacement_range=displacement_range,
            velocity_range=velocity_range,
            elongation_range=elongation_range
        )

        self.plot_data(
            df_in_s, 
            "Global",
            displacement_range, 
            velocity_range, 
            elongation_range,
        )

        self.perform_fft_filtered(
            first_window_high_freq,
            "velocity",
            4e6,
            1500,
            "FFT filtered signal"
        )
        

    def plot_data(self, dataframe, title, displacement_range, velocity_range, elongation_range):
        """Plots the given data over time, splitting the data by parameter. Includes lines to indicate selected range.

        :param dataframe: The target dataframe
        :type dataframe: dataframe
        :param title: Title of the plot
        :type title: string
        :param displacement_range: The chosen displacement range
        :type displacement_range: list of strings (number, units)
        :param velocity_range: The chosen velocity range
        :type velocity_range: list of strings (number, units)
        :param elongation_range: The chosen elongation range
        :type elongation_range: list of strings (number, units)
        """
        
        time = dataframe["time (s)"]
        displacement = dataframe["displacement"]
        
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(20, 5), sharex=True)

        # Displacement vs time plot
        ax1.plot(time, displacement)
        ax1.axhline(float(displacement_range[0]), color='red', linestyle='--',
                    label=(displacement_range[0] + " " + displacement_range[1]))
        ax1.axhline(-float(displacement_range[0]), color='red', linestyle='--',
                    label=("-" + displacement_range[0] + " " + displacement_range[1]))
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Displacement' + " " + "(" + displacement_range[1] + ")")
        ax1.grid(alpha=0.2, ls='dashed')
        ax1.legend()
        
        # Velocity vs time 
        ax2.plot(time, dataframe["velocity"])
        ax2.axhline(float(velocity_range[0]), color='red', linestyle='--',
                    label=(velocity_range[0] + " " + velocity_range[1]))
        ax2.axhline(-float(velocity_range[0]), color='red', linestyle='--',
                    label=("-" + velocity_range[0] + " " + velocity_range[1]))
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Velocity' + " " + "(" + velocity_range[1] + ")")
        ax2.grid(alpha=0.2, ls='dashed')
        ax2.legend()
        ax3.plot(time, dataframe["elongation_center"])
        ax3.axhline(float(elongation_range[0]), color='red', linestyle='--',
                    label=(elongation_range[0] + " " + elongation_range[1]))
        ax3.axhline(-float(elongation_range[0]), color='red', linestyle='--',
                    label=("-" + elongation_range[0] + " " + elongation_range[1]))
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Elongation ' + "(" + elongation_range[1] + ")")
        ax3.grid(alpha=0.2, ls='dashed')
        ax3.legend()
        ax4.plot(time, dataframe["elongation_downstream"])
        ax4.axhline(float(elongation_range[0]), color='red', linestyle='--',
                    label=(elongation_range[0] + " " + elongation_range[1]))
        ax4.axhline(-float(elongation_range[0]), color='red', linestyle='--',
                    label=("-" + elongation_range[0] + " " + elongation_range[1]))
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Elongation ' + "(" + elongation_range[1] + ")")
        ax4.grid(alpha=0.2, ls='dashed')
        ax4.legend()

        fig.suptitle(title, fontsize=20)
        plt.show()

    def plot_pre_post_trigger(self, pretrigger_df, posttrigger_df, displacement_range, velocity_range,
                                elongation_range):
        """

        :param pretrigger_df: The pretrigger data
        :type pretrigger_df: dataframe
        :param posttrigger_df: The posttrigger data
        :type posttrigger_df: dataframe
        :param displacement_range: The chosen displacement range
        :type displacement_range: list of strings (number, units)
        :param velocity_range: The chosen velocity range
        :type velocity_range: list of strings (number, units)
        :param elongation_range: The chosen elongation range
        :type elongation_range: list of strings (number, units)
        """
        fig, axes = plt.subplots(4, 2, figsize=(24, 12))
        fig.tight_layout(pad=3.0)  # Adjust spacing between subplots

        # Plot Displacement
        axes[0, 0].plot(pretrigger_df['time (s)'], pretrigger_df['displacement'], label='Pretrigger Displacement',
                        color='blue')
        axes[0, 0].set_title('Pretrigger Displacement')
        # axes[0, 0].axhline(float(displacement_range[0]), color='red', linestyle='--',
        #                    label=(displacement_range[0] + " " + displacement_range[1]))
        # axes[0, 0].axhline(-float(displacement_range[0]), color='red', linestyle='--',
        #                    label=("-" + displacement_range[0] + " " + displacement_range[1]))
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Displacement' + " " + "(" + displacement_range[1] + ")")
        axes[0, 0].legend()
        axes[0, 0].grid()

        axes[0, 1].plot(posttrigger_df['time (s)'], posttrigger_df['displacement'], label='Posttrigger Displacement',
                        color='orange')
        axes[0, 1].set_title('Posttrigger Displacement')
        # axes[0, 1].axhline(float(displacement_range[0]), color='red', linestyle='--',
        #                    label=(displacement_range[0] + " " + displacement_range[1]))
        # axes[0, 1].axhline(-float(displacement_range[0]), color='red', linestyle='--',
        #                    label=("-" + displacement_range[0] + " " + displacement_range[1]))
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Displacement' + " " + "(" + displacement_range[1] + ")")
        axes[0, 1].legend()
        axes[0, 1].grid()

        # Plot Velocity
        axes[1, 0].plot(pretrigger_df['time (s)'], pretrigger_df['velocity'], label='Pretrigger Velocity', color='blue')
        axes[1, 0].set_title('Pretrigger Velocity')
        # axes[1, 0].axhline(float(velocity_range[0]), color='red', linestyle='--',
        #                    label=(velocity_range[0] + " " + velocity_range[1]))
        # axes[1, 0].axhline(-float(velocity_range[0]), color='red', linestyle='--',
        #                    label=("-" + velocity_range[0] + " " + velocity_range[1]))
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Velocity' + " " + "(" + velocity_range[1] + ")")
        axes[1, 0].legend()
        axes[1, 0].grid()

        axes[1, 1].plot(posttrigger_df['time (s)'], posttrigger_df['velocity'], label='Posttrigger Velocity',
                        color='orange')
        axes[1, 1].set_title('Posttrigger Velocity')
        # axes[1, 1].axhline(float(velocity_range[0]), color='red', linestyle='--',
        #                    label=(velocity_range[0] + " " + velocity_range[1]))
        # axes[1, 1].axhline(-float(velocity_range[0]), color='red', linestyle='--',
        #                    label=("-" + velocity_range[0] + " " + velocity_range[1]))
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].set_ylabel('Velocity' + " " + "(" + velocity_range[1] + ")")
        axes[1, 1].legend()
        axes[1, 1].grid()

        # Plot Elongation Center
        axes[2, 0].plot(pretrigger_df['time (s)'], pretrigger_df['elongation_center'], label='Pretrigger Elongation Center', color='blue')
        axes[2, 0].set_title('Pretrigger Elongation Center')
        axes[2, 0].set_xlabel('Time (s)')
        axes[2, 0].set_ylabel('Elongation '+ "(" + elongation_range[1] + ")")
        axes[2, 0].legend()
        axes[2, 0].grid()

        axes[2, 1].plot(posttrigger_df['time (s)'], posttrigger_df['elongation_center'], label='Posttrigger Elongation Center',
                        color='orange')
        axes[2, 1].set_title('Posttrigger Elongation Center')

        axes[2, 1].set_xlabel('Time (s)')
        axes[2, 1].set_ylabel('Elongation ' + "(" + elongation_range[1] + ")")
        axes[2, 1].legend()
        axes[2, 1].grid()
        
        # Plot Elongation Downstream
        axes[3, 0].plot(pretrigger_df['time (s)'], pretrigger_df['elongation_downstream'], label='Pretrigger Elongation Downstream', color='blue')
        axes[3, 0].set_title('Pretrigger Elongation Downstream')
        axes[3, 0].set_xlabel('Time (s)')
        axes[3, 0].set_ylabel('Elongation ' + "(" + elongation_range[1] + ")")
        axes[3, 0].legend()
        axes[3, 0].grid()

        axes[3, 1].plot(posttrigger_df['time (s)'], posttrigger_df['elongation_downstream'], label='Posttrigger Elongation Downstream',
                        color='orange')
        axes[3, 1].set_title('Posttrigger Elongation Downstream')

        axes[3, 1].set_xlabel('Time (s)')
        axes[3, 1].set_ylabel('Elongation ' + "(" + elongation_range[1] + ")")
        axes[3, 1].legend()
        axes[3, 1].grid()
        plt.show()
        

    def perform_fft(self, dataframe, ldv_parameter, sampling_frequency_Hz, display_from_Hz, display_until_kHz, title):
        """Performs the FFT on the data for the given parameter. 

        :param dataframe: The target dataframe
        :type dataframe: dataframe
        :param ldv_parameter: The parameter on which the FFT is performed.
        :type ldv_parameter: string
        :param sampling_frequency_Hz: The frequency of acquisition of the given data.
        :type sampling_frequency_Hz: int
        :param display_from_Hz: The min frequency of display in the plot.
        :type display_from_Hz: int
        :param display_until_kHz: The max frequency of display in the plot.
        :type display_until_kHz: int
        :param title: The title of the plot
        :type title: string
        :raises ValueError: Raised error if the given parameter does not exist.
        """

        if ldv_parameter == "displacement":
            fft_signal = dataframe["displacement"]
        elif ldv_parameter == "velocity":
            fft_signal = dataframe["velocity"]
        elif ldv_parameter == "acceleration":
            fft_signal = dataframe["acceleration"]
        else:
            raise ValueError("The given parameter is not a LDV parameter.")

        N = len(fft_signal)
        xf, yf = scipy.signal.welch(fft_signal, sampling_frequency_Hz, nperseg=N, scaling='spectrum', average='mean',
                                    axis=-1, detrend=False)

        fig, ax = plt.subplots(figsize=(15, 5))
        xf = xf / 1e3
        yf = 2 * np.sqrt(yf)
        xf_disp = xf[10:]
        yf_disp = yf[10:]
        ax.plot(xf_disp, yf_disp)
        ax.set_xlim(display_from_Hz/1e3, display_until_kHz)
        ax.set_xlabel('Frequency (kHz)')
        ax.set_ylabel('FFT amplitude (a.u.)')
        ax.grid(alpha=0.2, ls='dashed')
        fig.suptitle(title, fontsize=20)
        plt.show()

    def perform_fft_filtered(self, dataframe, ldv_parameter, sampling_frequency_Hz, display_until_kHz, title):
        """Performs the FFT on the data for the given parameter.

        :param dataframe: The target dataframe
        :type dataframe: dataframe
        :param ldv_parameter: The parameter on which the FFT is performed.
        :type ldv_parameter: string
        :param sampling_frequency_Hz: The frequency of acquisition of the given data.
        :type sampling_frequency_Hz: int
        :param display_until_kHz: The max frequency of display in the plot.
        :type display_until_kHz: int
        :param title: The title of the plot
        :type title: string
        :raises ValueError: Raised error if the given parameter does not exist.
        """

        if ldv_parameter == "displacement":
            fft_signal = dataframe["displacement"]
        elif ldv_parameter == "velocity":
            fft_signal = dataframe["velocity"]
        elif ldv_parameter == "acceleration":
            fft_signal = dataframe["acceleration"]
        else:
            raise ValueError("The given parameter is not a LDV parameter.")

        N = len(fft_signal)
        sampling_frequency = 4e6
        filtered_fft_signal = butter_bandpass_filter(fft_signal, 5e3, 1500e3, sampling_frequency, order=6)

        xf, yf = scipy.signal.welch(filtered_fft_signal, sampling_frequency_Hz, nperseg=N, scaling='spectrum',
                                    average='mean',
                                    axis=-1, detrend=False)

        fig, ax = plt.subplots(figsize=(15, 5))
        ax.plot(xf / 1e3, 2 * np.sqrt(yf))
        ax.set_xlim(0, display_until_kHz)
        ax.set_xlabel('Frequency (kHz)')
        ax.set_ylabel('FFT amplitude (a.u.)')
        ax.grid(alpha=0.2, ls='dashed')
        fig.suptitle(title, fontsize=20)
        plt.show()

    def perform_cwt(self, dataframe, ldv_parameter, sampling_frequency_Hz):
        """Performs the continuous wavelet transform on the data for the given parameter.

        :param dataframe: The target dataframe
        :type dataframe: dataframe
        :param ldv_parameter: The parameter on which the FFT is performed.
        :type ldv_parameter: string
        :param sampling_frequency_Hz: The frequency of acquisition of the given data.
        :type sampling_frequency_Hz: int
        :raises ValueError: Raised error if the given parameter does not exist.
        """
        if ldv_parameter == "displacement":
            cwt_signal = dataframe["displacement"]
        elif ldv_parameter == "velocity":
            cwt_signal = dataframe["velocity"]
        elif ldv_parameter == "acceleration":
            cwt_signal = dataframe["acceleration"]
        else:
            raise ValueError("The given parameter is not a LDV parameter.")
        N = len(cwt_signal)
        xf, yf = scipy.signal.welch(cwt_signal, sampling_frequency_Hz, nperseg=N, scaling='spectrum', average='mean',
                                    axis=-1, detrend=False)

        # wavelet properties
        bw_freq = 1.5
        center_freq = 2.0
        wavelet_f = (('cmor-%.1f-%.1f') % (
            bw_freq, center_freq))  # complex morlet wavelet with bandwidth/center frequency

        time = dataframe["time (ms)"]
        end_time = time.iloc[-1]

        # Scales to calculate the wavelength for
        low_frequency = 5e3
        high_frequency = 1000e3
        frequency_step = 5e3
        dt = 1 / sampling_frequency_Hz

        scales = center_freq / (np.arange(low_frequency, high_frequency + frequency_step, frequency_step) * dt)
        scales = np.hstack([1e4, scales])  # no idea why the hell I do that

        cwt_cfs, cwt_frq = pywt.cwt(
            cwt_signal,
            scales,
            wavelet=wavelet_f,
            sampling_period=sampling_frequency_Hz
        )

        # transform scales to pseudo frequency
        cwt_frq = pywt.scale2frequency(wavelet_f, scales) / dt / 1e3  # kHz

        f, ax = plt.subplots(dpi=200)
        cf = ax.contourf(
            time * 1e6,
            cwt_frq,
            np.abs(cwt_cfs.real) / np.max(np.abs(cwt_cfs.real)),
            # just normalize to 1 and plot the absolute CWT amplitude
            levels=400,
            vmin=0,
            vmax=1,
            cmap='turbo'
        )

        ax.set_ylabel('Frequency (kHz)')
        ax.set_xlabel('Time (us)')

        # Overlay FFT if you're fancy
        fft_norm = 2 * np.sqrt(yf)
        fft_norm = fft_norm / np.max(fft_norm)
        ax.plot(fft_norm * 2 / 3 * end_time * 1e6, xf / 1e3, color='white', alpha=0.5)
        ax.set_ylim(0, 1000)

        f.tight_layout()

        cbar = f.colorbar(cf, ax=ax, location='right', aspect=50, pad=0.02)
        cbar.ax.set_ylabel('Absolute CWT amplitude (a.u.)')
        cbar.ax.set_ylim(0, 1)
        cbar.ax.set_yticks(np.arange(0, 1 + 0.2, 0.2))

        plt.show()


