import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks, peak_prominences
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
fc = 2.5
derivada_filtrada = filtro_paso_bajo(derivada_presion, fs, fc=fc)

# Encontrar maximo presion
max_presion = np.max(presion)
indice_max_presion = np.argmax(presion) + 10 #offset para evitar cosas raras

# Encontrar picos vPresion
indices_picos_vPresion, _ = find_peaks(
    derivada_filtrada,
    height=(-25, -4),  # TODO: ajustar
    prominence=1.5,  # Primero filtrar por el maximo de las bases
    # width=(fs*60/180.0, fs*60/40.0) TODO:
)
width=(fs*60/200.0, fs*60/20.0)
picos_vPresion = [derivada_filtrada[i] for i in indices_picos_vPresion]
tiempo_picos_vPresion = [tiempo[i] for i in indices_picos_vPresion]

prominencias, izq_bases, der_bases = peak_prominences(derivada_filtrada, indices_picos_vPresion)

# Calcula "prominencia alternativa" usando el mínimo de las dos bases
bases_min = np.minimum(derivada_filtrada[izq_bases], derivada_filtrada[der_bases])
prominencia_min = derivada_filtrada[indices_picos_vPresion] - bases_min

# Filtrar los picos cuya prominencia mínima sea mayor que cierto valor, por ejemplo 1.5
umbral = 5
#indices_picos_filtrados = [indices_picos_vPresion[i] for i, prominencia in enumerate(prominencia_min) if prominencia > umbral]
indices_picos_filtrados = []

# Recorremos cada elemento de la lista prominencia_min con su índice
for i in range(len(prominencia_min)):
    # Si la prominencia es mayor que el umbral
    if prominencia_min[i] > umbral and indices_picos_vPresion[i]>indice_max_presion:
        # Añadimos el índice correspondiente de indices_picos_vPresion a la nueva lista
        indices_picos_filtrados.append(indices_picos_vPresion[i])
new_picos_vPresion = [derivada_filtrada[i] for i in indices_picos_filtrados]
new_tiempo_picos_vPresion = [tiempo[i] for i in indices_picos_filtrados]

# Calcular presiones sys y dia
indice_sys = indices_picos_filtrados[0]
sys = int(presion[indice_sys])
indice_dia = indices_picos_filtrados[-1]
dia = int(presion[indice_dia])
print(f"Sys: {sys}mmHg  |  Dia: {dia}mmHg")

# Paso 6: Graficar
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(tiempo, presion, label='Presión original')
plt.scatter(tiempo[indice_sys], presion[indice_sys], color='blue', marker='o', label=f"SYS: {sys}mmHg")
plt.scatter(tiempo[indice_dia], presion[indice_dia], color='green', marker='o', label=f"DIA: {dia}mmHg")
plt.xlabel('Tiempo (s)')
plt.ylabel('Presión (mmHg)')
plt.title('Presión vs Tiempo')
plt.grid()
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(tiempo, derivada_presion, label='Derivada sin filtrar', alpha=0.6)
plt.plot(tiempo, derivada_filtrada, label=f'Derivada filtrada ({fc} Hz)', linewidth=2)
plt.scatter(new_tiempo_picos_vPresion, new_picos_vPresion, color='red', marker='o', label='Picos detectados')
plt.xlabel('Tiempo (s)')
plt.ylabel('dPresión/dt (mmHg/s)')
plt.title('Primera derivada de la presión')
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
