from matplotlib import pyplot as plt
from scipy.signal import butter, lfilter
import numpy as np
from scipy.signal import find_peaks


def leer_datos(archivo):
    with open(archivo, 'r') as f:
        datos = [int(linea.strip()) for linea in f]
    return datos


def init_filtro_paso_bajo(cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def aplicar_filtro_paso_bajo(data, b, a, zi=None):
    if zi is None:
        zi = np.zeros((max(len(a), len(b)) - 1,))
    y, zf = lfilter(b, a, data, zi=zi)
    return y, zf


if __name__ == '__main__':
    ruta_datos = "../Data/SalidaPulsoSujeto2.txt"
    datos_pulso = leer_datos(ruta_datos)
    dt = 40
    tiempo = [40*i for i in range(len(datos_pulso))]

    lenD = len(datos_pulso)
    lenT = len(tiempo)

    fs = 1000/40  # Frecuencia de muestreo (Hz)
    cutoff = 5  # Frecuencia de corte (Hz)
    b, a = init_filtro_paso_bajo(cutoff, fs)
    zi = None

    senal_filtrada = []
    for dato in datos_pulso:
        y, zi = aplicar_filtro_paso_bajo([dato], b, a, zi)
        senal_filtrada.append(y[0])

    indices_picos, _ = find_peaks(senal_filtrada, distance=2)
    maximos_tiempo = [[], []]
    for indice in indices_picos:
        maximos_tiempo[0].append(senal_filtrada[indice])
        maximos_tiempo[1].append(tiempo[indice])

    plt.figure(figsize=(13, 6))
    plt.plot(tiempo, datos_pulso, linestyle='-', linewidth=0.5, label="Onda PPG")
    plt.plot(tiempo, senal_filtrada, linestyle='-', linewidth=1.5, label="Onda PPG filtrada")
    plt.scatter(
        maximos_tiempo[1],
        maximos_tiempo[0],
        color='blue',
        s=15,
        label='Máximos')
    plt.xlim(min(tiempo), max(tiempo))
    plt.ylim(min(datos_pulso) - 10, max(datos_pulso) + 10)
    plt.xlabel('Tiempo [ms]')
    plt.ylabel('Amplitud [mV]')
    plt.title('Detección de onda PPG')
    plt.legend()
    plt.show()
