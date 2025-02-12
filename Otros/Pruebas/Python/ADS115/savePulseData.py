import ADS1x15
import time
import os
import random  # Usa esto para simular lecturas de ADC, reemplázalo con tu código real de lectura ADC

# Configuración
file_dir = "./data"  # Carpeta donde se guardará el archivo
file_name = "brazo5.txt"  # Nombre del archivo
num_readings = 250  # Número de lecturas a guardar
interval = 0.04  # Intervalo de 40ms

ADS = ADS1x15.ADS1115(0, 0x48)
ADS.setDataRate(2) #32sps

# Crear carpeta 'data' si no existe
if not os.path.exists(file_dir):
    os.makedirs(file_dir)

# Función para simular la lectura del ADC (Reemplázala con tu código real de lectura ADC)
def read_adc():
    # Esta es una simulación de un valor de ADC
    return random.uniform(1.0, 4.0)  # Ajusta según el rango de tu ADC

# Guardar lecturas en un archivo
try:
    with open(os.path.join(file_dir, file_name), 'w') as file:
        for i in range(num_readings):
            # Leer ADC
            reading = ADS.readADC(0)

            # Escribir la lectura en el archivo
            file.write(f"{reading}\n")

            # Mostrar el progreso en la misma línea
            print(f"\rLectura {i}/{num_readings}", end="")

            # Esperar 40ms antes de la siguiente lectura
            time.sleep(interval)

        print(f"\n{num_readings} lecturas guardadas en {os.path.join(file_dir, file_name)}")

except KeyboardInterrupt:
    print("\nProceso cancelado por el usuario. Cerrando el programa...")

