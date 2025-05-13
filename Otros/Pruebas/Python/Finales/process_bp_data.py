import numpy as np
from matplotlib import pyplot as plt

from Utilities.blood_pressure import BloodPressure
from Utilities.data_operations import load_data

if __name__ == "__main__":
    time, pressures = load_data()
    fs = 1/np.mean(np.diff(time))
    bp = BloodPressure(fs)

    try:
        # Procesar información
        sys, dia = bp.get_blood_pressure(pressures)
        bp.plot_results()
    except Exception as e:
        print("Ocurrió un error al procesar los datos.")

        plt.figure(figsize=(12, 6))

        # Gráfico de presión original con anotaciones de presión sistólica y diastólica
        plt.subplot(2, 1, 1)
        # Gráfico de presión original con anotaciones de presión sistólica y diastólica
        plt.plot(bp.time, bp.pressures, label='Original pressure')
        plt.xlabel('Time (s)')
        plt.ylabel('Pressure (mmHg)')
        plt.title('Pressure vs Time')
        plt.grid()
        plt.legend()

        plt.subplot(2, 1, 2)
        # Gráfico de presión original con anotaciones de presión sistólica y diastólica
        plt.plot(bp.time, bp.d_pressures_filtered, label='Original pressure')
        plt.xlabel('Time (s)')
        plt.ylabel('d_Pressure (mmHg/s)')
        plt.title('d_Pressure vs Time')
        plt.grid()
        plt.legend()

        plt.show()
