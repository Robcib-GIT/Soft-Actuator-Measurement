from Utilities.blood_pressure import BloodPressure
from Utilities.data_operations import load_data
import numpy as np

"""
Para procesar lecturas de presión individuales
"""

if __name__ == "__main__":
    data, params_data = load_data()
    pressures = data['Pressure']

    time = np.array(data['Time'])
    fs = 1 / np.mean(np.diff(time))
    print(f"{params_data['Subject']} v{params_data['Version']} @{fs}Hz")

    bp = BloodPressure(fs=fs)

    try:
        # Procesar información
        sys, dia, ppm = bp.get_blood_pressure(pressures=pressures)
        print(f"SAM_SYS:  {sys}  |  SAM_DIA:  {dia}  |  SAM_PPM:  {ppm}")
        print(f"Real_SYS: {params_data['SYS']}  |  Real_SIA: {params_data['DIA']}  |  Real_PPM: {params_data['PPM']}")
    except Exception as e:
        print(f"Ocurrió un error al procesar los datos.\n {e}")
    finally:
        bp.plot_results()
