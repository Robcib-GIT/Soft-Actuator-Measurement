import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from tkinter import Tk, filedialog


def seleccionar_csv():
    root = Tk()
    root.withdraw()
    directorio_inicial = os.path.dirname(os.path.abspath(__file__))
    filepath = filedialog.askopenfilename(
        initialdir=directorio_inicial,
        title="Selecciona el archivo CSV",
        filetypes=[("CSV files", "*.csv")]
    )
    return filepath


def cargar_datos_csv(filepath):
    df = pd.read_csv(filepath)
    tiempo = df.iloc[:, 0].values
    presion = df.iloc[:, 1].values
    return tiempo, presion


def calcular_derivada(tiempo, presion):
    derivada = np.gradient(presion, tiempo)
    return derivada


def filtro_paso_bajo(data, fs, fc, orden=4):
    nyquist = 0.5 * fs
    normal_fc = fc / nyquist
    b, a = butter(orden, normal_fc, btype='low', analog=False)
    data_filtrada = filtfilt(b, a, data)
    return data_filtrada


# Paso 1: Seleccionar archivo
ruta_csv = seleccionar_csv()

# Paso 2: Cargar datos
tiempo, presion = cargar_datos_csv(ruta_csv)

# Paso 3: Derivada
derivada_presion = calcular_derivada(tiempo, presion)

# Paso 4: Calcular frecuencia de muestreo
fs = 1 / np.mean(np.diff(tiempo))  # Hz

# Paso 5: Filtrar derivada
derivada_filtrada = filtro_paso_bajo(derivada_presion, fs, fc=2.5)

# Paso 6: Graficar
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(tiempo, presion, label='Presión original')
plt.xlabel('Tiempo (s)')
plt.ylabel('Presión (mmHg)')
plt.title('Presión vs Tiempo')
plt.grid()
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(tiempo, derivada_presion, label='Derivada sin filtrar', alpha=0.6)
plt.plot(tiempo, derivada_filtrada, label='Derivada filtrada (20 Hz)', linewidth=2)
plt.xlabel('Tiempo (s)')
plt.ylabel('dPresión/dt (mmHg/s)')
plt.title('Primera derivada de la presión')
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
