"""
Este codigo es la adaptación del código "DetecciónPulso" para ejecutarse en tiempo
real. El concepto es el siguiente:
1-Obtener tandas de datos cada 3secs
2-Unir la nueva tanda al restante de la anterior, siendo el restante los puntos a
    partir del último pico sistólico detectado
3-Obtener picos sistólicos y diastólicos del conjunto
4-Averiguar si se está detectando pulso
5-Si se detecta pulso obtener datos relacionados con el pulso
6-Mostrar/enviar resultados
7-Descartar tanda hasta ultimo pico sistolico (almacenar tambien tiempo del ultimo
    pico)
8-Repetir el proceso


De esta manera, al trabajar con un conjunto finito de datos, se pueden utilizar los
vectores de numpy para mayor agilidad. Hay que utilizar colas de datos para no
perderlos mientras se procesan las tandas.
"""

"""
==============================================================================
0: CONFIGURACIÓN
==============================================================================
Descripción: carga librerías y define constantes que servirán para filtrar la
    onda.
"""
from matplotlib import pyplot as plt, animation
from scipy.signal import butter, lfilter, find_peaks
import numpy as np
import queue
import threading
import time

# TODO ajustar
MAX_SISTOLICO = 550  # Dedo: 550 | Brazo: 580
BARRERA_SIS_DIA = 515  # Dedo: 515 | Brazo: 525
MIN_DIASTOLICO = 480
MIN_MUESTRAS_ENTRE_PULSOS = (60 / 100) * (1000 / 40)

MUESTRAS_ENVIO = 5
SEGMENTOS_ANALISIS = 11  # 15  # Equivalente a 3secs de datos

ruta_datos = "../Data/Prueba.txt"

"""
==============================================================================
1: DEFINICIÓN DE FUNCIONES
==============================================================================
"""


def leer_datos(archivo):
    datos = np.loadtxt(archivo, dtype=int)
    return datos


def init_filtro_paso_bajo(_cutoff, _fs, order=4):
    nyquist = 0.5 * _fs
    normal_cutoff = _cutoff / nyquist
    _b, _a = butter(order, normal_cutoff, btype='low', analog=False)
    return _b, _a


def aplicar_filtro_paso_bajo(data, _b, _a, _zi=None):
    if _zi is None:
        _zi = np.zeros((max(len(a), len(b)) - 1,))
    yf, zf = lfilter(b, a, data, zi=_zi)
    return yf, zf


"""
==============================================================================
2: CÓDIGO PRINCIPAL
==============================================================================
"""

if __name__ == '__main__':
    # _______________2.1: LEER TODOS LOS DATOS_______________
    datos_pulso_completo = leer_datos(ruta_datos)
    dt = 40  # TODO: Extraer del Json
    tiempo_completo = np.arange(len(datos_pulso_completo)) * dt

    # _______________2.2: SEGMENTAR DATOS_______________
    # Descripción: Se segmentan los datos en packs de 5 para simular la recepción
    #   desde Arduino
    cola = queue.Queue()
    segmentos = [datos_pulso_completo[i:i + MUESTRAS_ENVIO] for i in
                 range(0, len(datos_pulso_completo), MUESTRAS_ENVIO)]

    for segmento in segmentos:
        cola.put(segmento)
    cola.put(None)

    # _______________2.3: PREPARACIÓN PARA EL ANALISIS_______________
    datos_procesados = 0
    fin_analisis = False
    fs = 1000 / dt  # Frecuencia de muestreo (Hz)
    cutoff = 3  # Frecuencia de corte (Hz) (entre 2 y 5 va bien)
    b, a = init_filtro_paso_bajo(cutoff, fs)
    zi = None

    senal_filtrada = np.array([], dtype=int)  # TODO: borrar
    sistolicos_tiempo_completo = [np.array([]), np.array([])]  # TODO: borrar
    diastolicos_tiempo_completo = [np.array([]), np.array([])]  # TODO: borrar

    # _______________2.4: PROCESAR DATOS_______________
    while not fin_analisis:

        # 2.4.1: Obtener paquete de datos
        datos_pulso = np.array([], dtype=int)
        for i in range(SEGMENTOS_ANALISIS):
            segmento = cola.get()
            if segmento is None:
                fin_analisis = True
                break
            else:
                datos_pulso = np.concatenate((datos_pulso, segmento))

        elementos_muestra = len(datos_pulso)
        if elementos_muestra > 0:
            tiempo = np.arange(datos_procesados, datos_procesados + elementos_muestra) * dt

            # 2.4.2: Aplicar filtro de paso bajo (Butterworth)
            datos_filtrados, zi = aplicar_filtro_paso_bajo(datos_pulso, b, a, zi)

            # 2.4.3: Localizar puntos de interés
            indices_sistolicos, _ = find_peaks(
                datos_filtrados,
                height=(BARRERA_SIS_DIA, MAX_SISTOLICO),
                distance=MIN_MUESTRAS_ENTRE_PULSOS)
            indices_diastolicos, _ = find_peaks(
                datos_filtrados,
                height=(MIN_DIASTOLICO, BARRERA_SIS_DIA),
                distance=MIN_MUESTRAS_ENTRE_PULSOS)

            sistolicos_tiempo = [[], []]
            diastolicos_tiempo = [[], []]

            if len(indices_sistolicos) > 0:
                for indice in indices_sistolicos:
                    sistolicos_tiempo[0].append(datos_filtrados[indice])
                    sistolicos_tiempo[1].append(tiempo[indice])

            if len(indices_diastolicos) > 0:
                for indice in indices_diastolicos:
                    diastolicos_tiempo[0].append(datos_filtrados[indice])
                    diastolicos_tiempo[1].append(tiempo[indice])

            # 2.4.X: TODO Almacenar sobrante para la proxima vuelta
            # if indices_sistolicos:
            #    if indices_sistolicos[-1] == len(datos_filtrados):

            datos_procesados += elementos_muestra
            senal_filtrada = np.concatenate((senal_filtrada, datos_filtrados))

            if len(sistolicos_tiempo[0]) > 0:
                sistolicos_tiempo_completo[0] = np.concatenate(
                    (sistolicos_tiempo_completo[0], np.array(sistolicos_tiempo[0])))
                sistolicos_tiempo_completo[1] = np.concatenate(
                    (sistolicos_tiempo_completo[1], np.array(sistolicos_tiempo[1])))

            if len(diastolicos_tiempo[0]) > 0:
                diastolicos_tiempo_completo[0] = np.concatenate(
                    (diastolicos_tiempo_completo[0], np.array(diastolicos_tiempo[0])))
                diastolicos_tiempo_completo[1] = np.concatenate(
                    (diastolicos_tiempo_completo[1], np.array(diastolicos_tiempo[1])))

    # 2.X: Graficar resultados
    fig, axs = plt.subplots(2, 1, figsize=(13, 6))

    axs[0].axhline(
        y=1023 / 2,
        color='black',
        linestyle='--',
        linewidth=1,
        alpha=0.6)
    axs[0].plot(
        tiempo_completo,
        datos_pulso_completo,
        color='blue',
        linestyle='-',
        linewidth=0.5,
        label="Onda PPG original")
    axs[0].plot(
        tiempo_completo,
        senal_filtrada,
        color='green',
        linestyle='-',
        linewidth=1.5,
        label="Onda PPG filtrada")
    axs[0].scatter(
        sistolicos_tiempo_completo[1],
        sistolicos_tiempo_completo[0],
        marker='o',
        color='blue',
        s=15,
        label='Picos sistólicos')

    axs[0].scatter(
        diastolicos_tiempo_completo[1],
        diastolicos_tiempo_completo[0],
        marker='s',
        color='red',
        s=12,
        label='Picos diastólicos')

    axs[0].set_xlabel('Tiempo [ms]')
    axs[0].set_ylim(MIN_DIASTOLICO - 10, MAX_SISTOLICO + 10)
    axs[0].set_ylabel('Amplitud [mV]')
    axs[0].set_title('Detección de onda PPG')
    axs[0].legend()

    for ax in axs:
        ax.autoscale(axis='x')
        ax.set_xmargin(0)

    plt.tight_layout()
    plt.show()
