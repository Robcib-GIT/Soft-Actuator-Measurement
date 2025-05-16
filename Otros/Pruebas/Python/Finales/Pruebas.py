import time
from Utilities.data_operations import save_data, load_data
import numpy as np
from scipy.signal import find_peaks

def encontrar_pico_mas_ancho(lista):
    n = len(lista)
    mejor_pico = None
    mejor_ancho = -1

    for i in range(1, n - 1):
        if lista[i - 1] < lista[i] > lista[i + 1]:
            # Es un pico
            izquierda = i
            while izquierda > 0 and lista[izquierda - 1] < lista[izquierda]:
                izquierda -= 1

            derecha = i
            while derecha < n - 1 and lista[derecha + 1] < lista[derecha]:
                derecha += 1

            ancho = derecha - izquierda
            if ancho > mejor_ancho:
                mejor_ancho = ancho
                mejor_pico = lista[i]

    return mejor_pico



# --- Bucle principal con PID ---
if __name__ == "__main__":
    lista = [15, 25, 34, 38, 20, 37, 22, 15, 15]
    print(encontrar_pico_mas_ancho(lista))  # Output: 32
    idx_peaks, properties = find_peaks(lista, width=0)

    idx_map = idx_peaks[np.argmax(properties['widths'])]
    map_pressure = lista[idx_map]

    print(map_pressure)

