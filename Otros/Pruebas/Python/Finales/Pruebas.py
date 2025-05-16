import time
from Utilities.data_operations import save_data, load_data
import numpy as np


# --- Bucle principal con PID ---
if __name__ == "__main__":
    fs = 250
    interval = 1/fs
    data_dict, param_dict = load_data()
    data_dict['Time'] = np.arange(0, len(data_dict['Pressure'])) * interval

    claves_deseadas = ['SYS', 'DIA', 'PPM']
    nuevo_dict = {k: param_dict[k] for k in claves_deseadas if k in param_dict}

    save_data(data_dict=data_dict, results_dict= nuevo_dict)

