import math
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, find_peaks, peak_prominences
from tkinter import Tk, filedialog

prominence_min = 1.5
prominence_max = 5
max_height = 0
min_height = -25


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
fc = 2
derivada_filtrada = filtro_paso_bajo(derivada_presion, fs, fc=fc)

# Encontrar maximo presion
max_presion = np.max(presion)
indice_max_presion = np.argmax(presion)

# Encontrar picos vPresion
indices_picos_vPresion, _ = find_peaks(
    derivada_filtrada,
    height=(min_height, max_height),
    prominence=prominence_min,  # Primero filtrar por el maximo de las bases
    distance=1
)

picos_vPresion = [derivada_filtrada[i] for i in indices_picos_vPresion]
tiempo_picos_vPresion = [tiempo[i] for i in indices_picos_vPresion]

prominencias, izq_bases, der_bases = peak_prominences(derivada_filtrada, indices_picos_vPresion)

# Calcula "prominencia alternativa" usando el mínimo de las dos bases
bases_min = np.minimum(derivada_filtrada[izq_bases], derivada_filtrada[der_bases])
prominencia_min = derivada_filtrada[indices_picos_vPresion] - bases_min

# Filtrar los picos cuya prominencia mínima sea mayor que cierto valor
indices_picos_filtrados = []

# Recorremos cada elemento de la lista prominencia_min con su índice
for i in range(len(prominencia_min)):
    # Si la prominencia es mayor que el umbral, el pico esta en la parte de desinflado
    if prominencia_min[i] > prominence_max and indices_picos_vPresion[i] > indice_max_presion:
        # Añadimos el índice correspondiente de indices_picos_vPresion a la nueva lista
        indices_picos_filtrados.append(indices_picos_vPresion[i])

print(f"Indices picos (1er filtrado): {indices_picos_filtrados}")

# Volver a filtrar por el histograma de distancias para sacar los agrupados e importantes
distancias = np.diff(indices_picos_filtrados)
distancia_min = math.floor(60 / 230 * fs)  # 230ppm
distancia_max = math.ceil(60 / 40 * fs)  # 40ppm
variacion_pulsos = math.ceil(60E-3 * fs)  # Maxima diferencia entre pulsos de 60ms=60E-3*fs samples
bins = np.arange(distancia_min, distancia_max + 1, variacion_pulsos)
hist, bin_edges = np.histogram(distancias, bins=bins)

print("Histograma:", hist)
print("Límites de los bins:", bin_edges)

plt.hist(distancias, bins=bins, edgecolor='black')
plt.xticks(bin_edges)  # Mostrar los bordes en el eje x
plt.xlabel('Distancia')
plt.ylabel('Frecuencia')
plt.title('Histograma con 4 bins')
plt.grid(True)
plt.show()

# Encontrar punto de evaluacion
# FIXME: cuando cae en medio no detecta algunos
indice_moda = np.argmax(hist)
if 0 < indice_moda < len(hist) - 1:
    if hist[indice_moda - 1] >= hist[indice_moda + 1]:
        distancia_filtrado = bin_edges[indice_moda]
    else:
        distancia_filtrado = bin_edges[indice_moda + 1]
elif indice_moda == 0:
    distancia_filtrado = bin_edges[1]
else:
    distancia_filtrado = bin_edges[indice_moda]

# Obtener indices de los tramos que no cumplen con esa distancia
# Recorrer la lista de atras adelante para que no cambien los indices
segmentos_viables = []  # Se guardan los posibles segmentos que incluyen los picos buenos seguidos
indice_inicio_corte = 0
for i, distancia in enumerate(distancias):
    desfase_distancia = abs(distancia_filtrado - distancia)
    desfase_distancia_doble = abs(distancia_filtrado * 2 - distancia)  # Para cuando se salta un pulso
    if desfase_distancia > variacion_pulsos :# and desfase_distancia_doble > variacion_pulsos:  # Igual*2 tambien
        segmentos_viables.append(indices_picos_filtrados[indice_inicio_corte:i+1])
        indice_inicio_corte = i+1
        # print(f"Corte entre puntos {i}-{i+1}")    TODO: borrar
segmentos_viables.append(indices_picos_filtrados[indice_inicio_corte:])
print(segmentos_viables)

indices_picos_filtrados = max(segmentos_viables, key=len)





# Obtener puntos
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
