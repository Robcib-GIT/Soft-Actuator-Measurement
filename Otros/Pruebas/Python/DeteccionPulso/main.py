from matplotlib import pyplot as plt
from scipy.signal import butter, lfilter
import numpy as np
from scipy.signal import find_peaks

# TODO ajustar
MAX_SISTOLICO = 550
BARRERA_SIS_DIA = 515
MIN_DIASTOLICO = 480
MIN_MUESTRAS_ENTRE_PULSOS = (60/100)*(1000/40)

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


def aplicar_deteccion_PPG(lista_detecciones):
    if not lista_detecciones:
        detectado = False
    else:
        detectado = lista_detecciones[-1]

    for i in range(len(senal_filtrada)):
        if 560 > senal_filtrada[i] > 480:  # TODO ajustar
            if i in indices_picos:
                detectado = True
        else:
            detectado = False
        lista_detecciones.append(detectado)
    return


if __name__ == '__main__':
    # ##################### OBTENER DATOS ####################################
    ruta_datos = "../Data/SalidaPulsoSujeto1_RUIDO.txt"
    datos_pulso = leer_datos(ruta_datos)
    dt = 40
    tiempo = [dt * i for i in range(len(datos_pulso))]

    # ##################### FILTRAR SEÑAL ####################################

    fs = 1000 / dt  # Frecuencia de muestreo (Hz)
    cutoff = 3  # Frecuencia de corte (Hz) (entre 2 y 5 va bien)
    b, a = init_filtro_paso_bajo(cutoff, fs)
    zi = None

    senal_filtrada = []
    for dato in datos_pulso:
        y, zi = aplicar_filtro_paso_bajo([dato], b, a, zi)
        senal_filtrada.append(y[0])

    indices_picos, _ = find_peaks(senal_filtrada, distance=2)
    indices_sistolicos, _ = find_peaks(
        senal_filtrada,
        height=(BARRERA_SIS_DIA, MAX_SISTOLICO),
        distance=MIN_MUESTRAS_ENTRE_PULSOS)
    indices_diastolicos, _ = find_peaks(
        senal_filtrada,
        height=(MIN_DIASTOLICO, BARRERA_SIS_DIA),
        distance=MIN_MUESTRAS_ENTRE_PULSOS)
    maximos_tiempo = [[], []]
    sistolicos_tiempo = [[], []]
    diastolicos_tiempo = [[], []]

    for indice in indices_picos:
        maximos_tiempo[0].append(senal_filtrada[indice])
        maximos_tiempo[1].append(tiempo[indice])

    # TODO filtrar y añadir picos sistólicos y diastólicos
    for indice in indices_sistolicos:
        sistolicos_tiempo[0].append(senal_filtrada[indice])
        sistolicos_tiempo[1].append(tiempo[indice])

    for indice in indices_diastolicos:
        diastolicos_tiempo[0].append(senal_filtrada[indice])
        diastolicos_tiempo[1].append(tiempo[indice])

    # ##################### Detección de señal PPG ####################################
    PPG_detectado = []
    aplicar_deteccion_PPG(PPG_detectado)

    # ##################### GRAFICAR RESULTADOS ####################################
    fig, axs = plt.subplots(2, 1, figsize=(13, 6))

    axs[0].axhline(
        y=1023 / 2,
        color='black',
        linestyle='--',
        linewidth=1,
        alpha=0.6)
    axs[0].plot(
        tiempo,
        datos_pulso,
        color='blue',
        linestyle='-',
        linewidth=0.5,
        label="Onda PPG original")
    axs[0].plot(
        tiempo,
        senal_filtrada,
        color='green',
        linestyle='-',
        linewidth=1.5,
        label="Onda PPG filtrada")

    axs[0].scatter(
        sistolicos_tiempo[1],
        sistolicos_tiempo[0],
        marker='o',
        color='blue',
        s=15,
        label='Picos sistólicos')

    axs[0].scatter(
        diastolicos_tiempo[1],
        diastolicos_tiempo[0],
        marker='s',
        color='red',
        s=12,
        label='Picos diastólicos')
    '''
    axs[0].scatter(
        sistolicos_tiempo[1],
        sistolicos_tiempo[0],
        color='blue',
        s=15,
        label='Máximos')
    '''
    axs[0].set_xlabel('Tiempo [ms]')
    axs[0].set_ylim(min(datos_pulso) - 10, max(datos_pulso) + 10)
    axs[0].set_ylabel('Amplitud [mV]')
    axs[0].set_title('Detección de onda PPG')
    # axs[0].legend()

    axs[1].plot(
        tiempo,
        PPG_detectado,
        linestyle='-',
        linewidth=1.5,
        label="PPG detectada")
    axs[1].set_xlabel("Tiempo [ms]")
    axs[1].autoscale(axis='y')
    axs[1].set_ylabel("PPG detectada [0-1]")
    axs[1].set_title("Detección de onda PPG")

    for ax in axs:
        ax.autoscale(axis='x')
        ax.set_xmargin(0)
    plt.tight_layout()
    plt.show()
