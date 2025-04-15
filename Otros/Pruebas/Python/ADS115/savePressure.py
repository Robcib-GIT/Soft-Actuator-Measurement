import ADS1x15
import time
import csv
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog

# Configuración del ADS1115
ADS = ADS1x15.ADS1115(0, 0x48)
ADS.setGain(ADS.PGA_0_512V)

# Función para obtener la presión
def getPressure(offset=27.0, pressureRef=200.0, valueRef=2960.0):
    pressure_raw = ADS.readADC_Differential_0_1()
    pressure = (pressure_raw - offset) * pressureRef / valueRef
    return float(pressure)

# Intervalo de tiempo en segundos
interval = 0.025  # Cambia este valor por el que necesites

# Inicializar lista para almacenar los datos de presión
presiones = []

try:
    while True:
        pressure = getPressure()
        presiones.append(pressure)
        print(f"\rPresión: {pressure:.2f} mmHg     ", end="")
        time.sleep(interval)

except KeyboardInterrupt:
    print("\nLectura interrumpida por el usuario.")

    # Mostrar gráfico con los valores
    plt.plot(presiones)
    plt.xlabel('Tiempo (segundos)')
    plt.ylabel('Presión (mmHg)')
    plt.title('Gráfico de Presión')
    plt.grid(True)
    plt.show()

    # Crear ventana de diálogo para guardar el archivo CSV
    root = Tk()
    root.withdraw()  # Ocultar ventana principal
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

    if file_path:
        # Guardar los datos en un archivo CSV
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Tiempo (segundos)', 'Presión (mmHg)'])
            for i, presion in enumerate(presiones):
                writer.writerow([i * interval, presion])
        print(f"Archivo guardado como {file_path}")
    else:
        print("No se guardó el archivo.")
