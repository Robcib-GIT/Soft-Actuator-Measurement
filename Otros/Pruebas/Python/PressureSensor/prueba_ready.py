import Jetson.GPIO as GPIO
import time
import spidev


"""
Para device 0:
MOSI: 19 | MISO: 21 | SCK: 23
"""


spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000     # 2 * 1/(2e-6)
spi.mode = 0b00  # CPOL = 0, CPHA = 0
spi.bits_per_word = 8

try:
    while True:
        respuesta = spi.xfer2([0x0])
        print(f"Respuesta: {bin(respuesta[0])} len: {len(respuesta)}")
        time.sleep(2)

except KeyboardInterrupt:
    print("Programa detenido por el usuario.")
finally:
    spi.close()