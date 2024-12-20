from matplotlib import pyplot as plt
from scipy.signal import butter, lfilter, find_peaks
import numpy as np

# TODO ajustar
MAX_SISTOLICO = 580  # Para dedo 550
BARRERA_SIS_DIA = 525  # Para dedo 515
MIN_DIASTOLICO = 480
MIN_MUESTRAS_ENTRE_PULSOS = (60 / 100) * (1000 / 40)


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
        if MAX_SISTOLICO > senal_filtrada[i] > MIN_DIASTOLICO:  # TODO ajustar
            if i in indices_sistolicos:
                detectado = True
        else:
            detectado = False
        lista_detecciones.append(detectado)
    return


def obtener_ppm(tiempos_sistolicos):
    n = len(tiempos_sistolicos)
    pulsaciones = [[], []]
    if n > 1:
        for i in range(n-1):
            diferencia = tiempos_sistolicos[i + 1] - tiempos_sistolicos[i]
            pulsaciones[0].append(60e3 / diferencia)
            pulsaciones[1].append(tiempos_sistolicos[i] + diferencia/2)

    return pulsaciones


if __name__ == '__main__':
    # ##################### OBTENER DATOS ####################################
    ruta_datos = "../Data/SalidaPulsoSujeto1_BRAZO_I.txt"
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

    # ##################### ENCONTRAR PICOS ####################################

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

    # ##################### SACAR DERIVADA ####################################
    # central_diff = [(datos_pulso[i+1] - datos_pulso[i-1]) / (2 * dt) for i in range(1, len(datos_pulso)-1)]

    # ##################### OTENER DATOS DE PULSO ####################################
    ppm = obtener_ppm(sistolicos_tiempo[1])

    # ##################### Detección de señal PPG ####################################
    PPG_detectado = []
    aplicar_deteccion_PPG(PPG_detectado)

    # ##################### GRAFICAR RESULTADOS ####################################
    fig, axs = plt.subplots(3, 1, figsize=(13, 12))

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
    axs[0].set_ylim(MIN_DIASTOLICO - 10, MAX_SISTOLICO + 10)
    axs[0].set_ylabel('Amplitud [mV]')
    axs[0].set_title('Detección de onda PPG')
    axs[0].legend()

    axs[1].plot(
        ppm[1],
        ppm[0],
        linestyle='-',
        linewidth=1.5)
    axs[1].set_xlabel("Tiempo [ms]")
    axs[1].set_ylim(50, 100)
    axs[1].set_ylabel("PPM")
    axs[1].set_title("PPM / Tiempo")

    axs[2].plot(
        tiempo,
        PPG_detectado,
        linestyle='-',
        linewidth=1.5,
        label="PPG detectada")
    axs[2].set_xlabel("Tiempo [ms]")
    axs[2].autoscale(axis='y')
    axs[2].set_ylabel("PPG detectada [0-1]")
    axs[2].set_title("Detección de onda PPG")

    for ax in axs:
        ax.autoscale(axis='x')
        ax.set_xmargin(0)

    plt.tight_layout()
    plt.show()
