import Jetson.GPIO as GPIO
import time
import spidev

"""
Para device 0:
MOSI: 19 | MISO: 21 | SCK: 23
"""

# Configuración de GPIO
GPIO.setmode(GPIO.BOARD)  # Usar numeración física de pines
GPIO.setup(31, GPIO.IN)  # Configura el pin GPIO 31 como entrada

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000     # 2 * 1/(2e-6)
spi.mode = 0b00  # CPOL = 0, CPHA = 0
spi.bits_per_word = 8

try:
    while True:
        estado = GPIO.input(31)  # Leer el estado del pin GPIO 31
        print(f"Estado del pin: {'Alto' if estado else 'Bajo'}")
        time.sleep(2)

except KeyboardInterrupt:
    print("Programa detenido por el usuario.")
finally:
    GPIO.cleanup()  # Limpiar la configuración de GPIO al finalizar
    spi.close()
