"""
Inspirado en: "https://gist.github.com/amotl/94c83f3ecc3dbf181da708fdd8ef9f45"
y "https://gist.github.com/underdoeg/98a38b54f889fce2b237"

Para bus 0:
MOSI: 19 | MISO: 21

Para bus 1:
MOSI: 37 | MISO: 22
"""
import spidev
import time

import Jetson.GPIO as GPIO
# Configuración de GPIO
GPIO.setmode(GPIO.BOARD)  # Usar numeración física de pines
GPIO.setup(31, GPIO.IN)  # Configura el pin GPIO 31 como entrada

class HX710B:
    def __init__(self, spi_bus, spi_device = 0, gain = 128):

        self.spi = spidev.SpiDev()
        self.spi.open(0,0)   #(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000     # 2 * 1/(2e-6)
        self.spi.mode = 0b00  # CPOL = 0, CPHA = 0
        self.spi.bits_per_word = 8

        self.clock_25 = [0xAA] * 6 + [0x80]
        self.clock_26 = [0xAA] * 6 + [0xA0]
        self.clock_27 = [0xAA] * 6 + [0xA8]
        self.clock = self.clock_25
        self.in_data = bytearray(7)

        self.offset = 0 # TODO: ajustar
        self.calibration_factor = 1 # TODO: ajustar
        

        self.set_gain(gain)

    def is_ready(self):
        estado = GPIO.input(31)  # Leer el estado del pin GPIO 31
        print(f"Estado del pin: {'Alto' if estado else 'Bajo'}")
        # Se comprueba si el ultimo bit recibido es 0
        respuesta = self.spi.xfer2([0x00])
        print(f"Respuesta: {bin(respuesta[0])} len: {len(respuesta)}")
        return (self.spi.xfer2([0x00])[0] & 0x01) == 0

    def set_gain(self, gain):
        if gain == 128:
            self.clock = self.clock_25
        elif gain == 64:
            self.clock = self.clock_27
        elif gain == 32:
            self.clock = self.clock_26
        
        self.read() # Para ajustar la ganancia

    def read(self):
        # Esperar a que el sensor esté listo
        while not self.is_ready():
            time.sleep(2)

        # Enviar reloj ficticio por MOSI y leer datos
        self.in_data = self.spi.xfer2(self.clock)  

        # Extraer uno no uno si para compensar el reloj ficticio
        result = 0
        for i in range(6):
            result = (result << 4) + (self.in_data[i] & 0x55)

        # Corregir el signo (nº de complemento a dos -> numero con signo)
        return result - ((result & 0x800000) << 1)
    
    def read_average(self, samples=3):
        sum = 0
        for _ in range(samples):
            sum += self.read()
        
        return sum/samples
    
    def get_pressure(self):
        pressure = (self.read() + self.offset) * self.calibration_factor
        return pressure

    def get_average_pressure(self, samples):
        average_pressure = (self.read_average() + self.offset) * self.calibration_factor
        return average_pressure
    
    def close(self):
        GPIO.cleanup()
        self.spi.close()