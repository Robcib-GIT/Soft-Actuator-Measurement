import os

import matplotlib.pyplot as plt
import numpy as np

from Utilities.blood_pressure import BloodPressure
from Utilities.data_operations import load_data

import statsmodels.api as sm


def plot_homoscedasticity(estimated, real, variable_name):
    error = np.array(real) - np.array(estimated)
    # media = (np.array(real) + np.array(estimated))/2

    coef = np.polyfit(real, error, deg=1)  # coef = [pendiente, intercepto]
    linea_tendencia = np.poly1d(coef)

    # Ajuste LOWESS
    # lowess = sm.nonparametric.lowess
    # ajuste = lowess(error, real, frac=0.6)  # frac controla el grado de suavizado

    plt.figure(figsize=(8, 5))
    plt.scatter(real, error, color='blue')

    plt.plot(real, linea_tendencia(real), color='red')
    # plt.plot(ajuste[:, 0], ajuste[:, 1], color='red')

    plt.xlabel(f"Presión {variable_name} real (mmHg)")
    plt.ylabel(f"Real - Estimada (mmHg)")
    plt.title(f"Presión {variable_name}")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":

    carpeta = "data"
    sam_sys = []
    sam_dia = []
    sam_ppm = []
    real_sys = []
    real_dia = []
    real_ppm = []

    for filename in os.listdir(carpeta):
        if filename.startswith("PRESION_") and filename.endswith(".csv"):
            filepath = os.path.join(carpeta, filename)
            data_dict, param_dict = load_data(filepath)
            # print(param_dict)

            fs = 1 / np.mean(np.diff(data_dict["Time"]))
            bp = BloodPressure(fs)

            # Obtener información
            # subject = param_dict['subject']
            # version = param_dict['version']
            # print(f"{subject} v{version}")

            results = {
                "real_sys": param_dict.get("SYS", None),
                "real_dia": param_dict.get("DIA", None),
                "real_ppm": param_dict.get("PPM", None)
            }

            # Calcular presiones con mi algoritmo
            try:
                sys, dia, ppm = bp.get_blood_pressure(data_dict["Pressure"])
                results["sam_sys"] = sys
                results["sam_dia"] = dia
                results["sam_ppm"] = ppm
            except Exception:
                results["sam_sys"] = None
                results["sam_dia"] = None
                results["sam_ppm"] = None

            # Almacenar informacion
            if results["real_sys"] is not None and results["sam_sys"] is not None:
                real_sys.append(results["real_sys"])
                sam_sys.append(results["sam_sys"])

            if results["real_dia"] is not None and results["sam_dia"] is not None:
                real_dia.append(results["real_dia"])
                sam_dia.append(results["sam_dia"])

    plot_homoscedasticity(estimated=sam_sys, real=real_sys, variable_name="sistólica")
    plot_homoscedasticity(estimated=sam_dia, real=real_dia, variable_name="diastólica")
