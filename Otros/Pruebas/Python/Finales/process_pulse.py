from Utilities.pulse import Pulse
from Utilities.data_operations import load_data
from typing import List


def process_pulse_segment(segment: List[int]):
    filtered_segment = pulse.apply_low_pass_filter(pulse_segment)
    # print(filtered_segment)
    ppm, mean_ibi, frequency, sdnn, rmssd = pulse.analice_pulse_signal()
    print(f"\rppm: {ppm}  |  freq: {frequency}  |  sdnn: {sdnn}  |  rmssd: {rmssd}", end="")


if __name__ == "__main__":
    pulse = Pulse(fs=25)

    pulse_data = load_data()[0]

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
