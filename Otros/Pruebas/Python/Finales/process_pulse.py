from Utilities.pulse import Pulse
from Utilities.data_operations import load_data
from typing import List
import numpy as np
import time


def process_pulse_segment(segment: List[int]):
    filtered_segment = pulse.apply_low_pass_filter(pulse_segment)
    # print(filtered_segment)
    ppm, mean_ibi, frequency, sdnn, rmssd = pulse.analice_pulse_signal()
    print(f"\rppm: {ppm}  |  freq: {frequency:.2f}  |  sdnn: {sdnn:.2f}  |  rmssd: {rmssd:.2f}     ", end="")


if __name__ == "__main__":
    data, params_data = load_data()
    pulse_data = data['Pulse']

    time = np.array(data['Time'])
    fs = 1 / np.mean(np.diff(time))
    print(f"{params_data['subject']} v{params_data['version']} @{fs}Hz")
    pulse = Pulse(fs=fs)

    processing = False
    pulse_segment = []
    for value in pulse_data:

        if value == -1 and processing:
            processing = False
            process_pulse_segment(pulse_segment)
            pulse.plot_results()
            pulse.restart()
            pulse_segment = []
            print("\nFin del analisis cardiaco")

        elif value != -1:
            if not processing:
                print("Comienzo del análisis cardiaco")
                processing = True

            pulse_segment.append(value)

            if len(pulse_segment) >= pulse.shipping_samples:
                process_pulse_segment(pulse_segment)
                pulse_segment = []
