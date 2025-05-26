import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, filtfilt, butter, savgol_filter


def find_1d_peak_widths(signal):
    peaks, _ = find_peaks(signal)
    widths = []
    for i, peak in enumerate(peaks):
        left = 0
        right = len(signal)-1
        if i > 0:
            temp = signal[peak]
            for j in range(peak, peaks[i - 1], -1):
                left = j
                if signal[j] <= temp:
                    temp = signal[j]
                else:
                    left = j+1
                    break

        if i < len(peaks)-1:
            temp = signal[peak]
            for j in range(peak, peaks[i + 1]+1):
                right = j
                if signal[j] <= temp:
                    temp = signal[j]
                else:
                    right = j-1
                    break

        widths.append(right - left)
    return peaks, widths

def polinomial_fitting(signal, deg=3):
    x = np.arange(len(signal))
    coeffs = np.polyfit(x, signal, deg=deg)
    poly = np.poly1d(coeffs)
    return poly(x)

# def get_map()


if __name__ == "__main__":
    amplitudes = [0.0, 7.2, 7.74, 9.43, 7.71, 10.14, 10.89, 6.63, 8.14, 8.68, 7.6, 7.41, 5.81, 4.97, 4.69]
    # amplitudes = [7.11, 13.68, 13.82, 15.93, 15.04, 14.24, 12.66, 10.79, 9.72, 6.45, 6.78, 7.48, 4.36, 6.6, 6.03, 6.35, 7.13, 6.29, 7.84]
    smoothed = polinomial_fitting(amplitudes)

    peaks, widths = find_1d_peak_widths(smoothed)
    print(f"Amplitudes: {amplitudes}")
    print(f"Picos en: {peaks}")
    print(f"Con anchura: {widths}")

    #idx_map = peaks[np.argmax(widths)]
    idx_max_smoothed = np.argmax(smoothed)
    idx_map = idx_max_smoothed-1 + np.argmax([amplitudes[idx_max_smoothed-1:idx_max_smoothed+2]])

    print(f"MAP: {amplitudes[idx_map]}")
    plt.plot(range(len(amplitudes)), amplitudes, label='Amplitudes original')
    plt.scatter(idx_map, amplitudes[idx_map], color='red', s=30)
    plt.plot(range(len(amplitudes)), smoothed, label='Amplitudes suavizada')
    plt.scatter(idx_max_smoothed, smoothed[idx_max_smoothed], color='red', s=30)
    plt.legend()
    plt.show()
