import matplotlib.pyplot as plt
import numpy as np
import queue
import threading
import time

from matplotlib import animation, ticker

dt = 40  # Intervalo entre mediciones
datos_tiempo_real = []
datos_leidos = 0
lock = threading.Lock()  # Para sincronizar el acceso a datos_tiempo_real
ELEMENTOS_PANTALLA = int(3000 / dt)

maximos_tiempo = []
minimos_tiempo = []
picos_sistolicos_tiempo = []

indice_ultimo_relativo = 0
buscar_max_o_min: bool = False


def leer_datos(archivo):
    with open(archivo, 'r') as f:
        datos = [int(linea.strip()) for linea in f]
    return datos


# Función para insertar datos en una cola
def productor(cola, lista_datos):
    for dato in generador_datos(lista_datos):
        cola.put(dato)  # Inserta el dato en la cola
    cola.put(None)  # Marca el final de los datos


# Función para consumir datos de una cola
def consumidor(cola):
    global datos_leidos
    while True:
        dato = cola.get()  # Saca un dato de la cola
        if dato is None:  # Si no hay más datos, termina
            break
        with lock:  # Bloquear acceso mientras actualizamos los datos
            datos_tiempo_real.append([dato, datos_leidos * dt])
            if buscar_max_o_min:
                encontrar_maximos(datos_tiempo_real[indice_ultimo_relativo:])
            else:
                encontrar_minimos(datos_tiempo_real[indice_ultimo_relativo:])

        datos_leidos += 1


# Generador de datos que utiliza yield
def generador_datos(lista):
    for i in range(len(lista)):
        yield lista[i]  # Produce un dato
        time.sleep(dt / 1000)  # Simula un retardo entre datos


# Función de inicialización de la animación
def init_grafico():
    linea.set_data([], [])
    picos_sistolicos.set_offsets(np.empty((0, 2)))  # Reinicia los puntos de picos sistólicos
    return linea, picos_sistolicos


def actualizar_grafico(frame):
    global datos_tiempo_real
    global maximos_tiempo

    # Si no hay datos suficientes aún, no actualizamos
    if len(datos_tiempo_real) == 0:
        return linea, picos_sistolicos

    # Usamos un lock para acceder a los datos de forma segura
    with lock:
        x = [dato[1] for dato in datos_tiempo_real]  # Tiempo
        y = [dato[0] for dato in datos_tiempo_real]  # Señal

    x_max = [dato[1] for dato in maximos_tiempo]  # Tiempo
    y_max = [dato[0] for dato in maximos_tiempo]  # Señal

    x_min = [dato[1] for dato in minimos_tiempo]  # Tiempo
    y_min = [dato[0] for dato in minimos_tiempo]  # Señal

    x_sis = [dato[1] for dato in picos_sistolicos_tiempo]  # Tiempo
    y_sis = [dato[0] for dato in picos_sistolicos_tiempo]  # Señal

    # Actualizamos los datos en el gráfico
    linea.set_data(x, y)

    # Actualizamos los maximos
    maximos.set_offsets(np.column_stack((x_max, y_max)))

    # Actualizamos los minimos
    minimos.set_offsets(np.column_stack((x_min, y_min)))

    # Actualizamos los picos sistolicos
    picos_sistolicos.set_offsets(np.column_stack((x_sis, y_sis)))

    # Ajustar eje X
    if len(x) > ELEMENTOS_PANTALLA:
        # print(f"ELEMENTOS_PANTALLA: {ELEMENTOS_PANTALLA}")
        ax.set_xlim(x[-ELEMENTOS_PANTALLA], x[-1])

    return linea, picos_sistolicos, maximos, minimos


def encontrar_maximos(sublista_tiempo):
    global indice_ultimo_relativo
    global buscar_max_o_min

    n = len(sublista_tiempo)

    for i in range(1, n - 1):
        # print(i)
        if sublista_tiempo[i][0] > sublista_tiempo[i - 1][0]:
            inicio = i
            while i < n - 2 and sublista_tiempo[i][0] == sublista_tiempo[i + 1][0]:
                i += 1
            if sublista_tiempo[inicio][0] > sublista_tiempo[i + 1][0]:
                indice_ultimo_relativo += inicio
                buscar_max_o_min = not buscar_max_o_min
                maximos_tiempo.append([sublista_tiempo[inicio][0], sublista_tiempo[inicio][1]])
                if 560 > sublista_tiempo[inicio][0] > 525:
                    picos_sistolicos_tiempo.append([sublista_tiempo[inicio][0], sublista_tiempo[inicio][1]])
                break

    return


def encontrar_minimos(sublista_tiempo):
    global indice_ultimo_relativo
    global buscar_max_o_min

    n = len(sublista_tiempo)

    for i in range(1, n - 1):
        # print(i)
        if sublista_tiempo[i][0] < sublista_tiempo[i - 1][0]:
            inicio = i
            while i < n - 2 and sublista_tiempo[i][0] == sublista_tiempo[i + 1][0]:
                i += 1
            if sublista_tiempo[inicio][0] < sublista_tiempo[i + 1][0]:
                indice_ultimo_relativo += inicio
                buscar_max_o_min = not buscar_max_o_min
                minimos_tiempo.append([sublista_tiempo[inicio][0], sublista_tiempo[inicio][1]])
                break

    return


if __name__ == '__main__':
    ruta_archivo = "Data/SalidaSensorPulso_0_1023.txt"
    datos = leer_datos(ruta_archivo)

    # Configuración de la figura
    fig, ax = plt.subplots(figsize=(10, 6))
    linea, = ax.plot([], [],
                     marker='',
                     linestyle='-',
                     linewidth=1,
                     color='r',
                     label='Señal PPG')

    maximos = ax.scatter([], [],
                         s=10,
                         marker='^',
                         color='b',
                         label='Maximos')

    minimos = ax.scatter([], [],
                         s=10,
                         marker='v',
                         color='b',
                         label='Mínimos')

    picos_sistolicos = ax.scatter([], [],
                                  s=18,
                                  marker='o',
                                  color='g',
                                  label='Picos sistólicos')

    ax.set_ylim(480, 580)  # Rango fijo en el eje Y
    ax.set_xlim(0, ELEMENTOS_PANTALLA * dt)  # Rango dinámico en el eje X len(datos) * dt

    ax.axhline(
        y=1023 / 2,  # TODO ajustar segun el datasheet
        color='black',
        linestyle='--',
        linewidth=1,
        alpha=0.5
    )

    ani = animation.FuncAnimation(
        fig,
        actualizar_grafico,
        init_func=init_grafico,
        frames=range(len(datos)),
        interval=dt,
        blit=True)

    # Crear una cola
    cola = queue.Queue()

    # Crear e iniciar hilos para productor y consumidor
    hilo_productor = threading.Thread(target=productor, args=(cola, datos))
    hilo_consumidor = threading.Thread(target=consumidor, args=(cola,))

    hilo_productor.start()
    hilo_consumidor.start()

    plt.show()

    # Esperar a que ambos hilos terminen
    hilo_productor.join()
    hilo_consumidor.join()
    print("Procesamiento completado.")
