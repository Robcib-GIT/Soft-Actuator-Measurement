"""
Inspirado en: "https://gist.github.com/amotl/94c83f3ecc3dbf181da708fdd8ef9f45.js"
"""
import spidev
import time

class HX710B:
    def __init__(self, spi_bus, spi_device = 0, gain = 128):
        self.spi = spidev.Spidev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000     # 2 * 1/(2e-6)
        self.spi.mode = 0b00  # CPOL = 0, CPHA = 0

        self.clock_25 = [0xAA] * 6 + [0x80]
        self.clock_26 = [0xAA] * 6 + [0xA0]
        self.clock_27 = [0xAA] * 6 + [0xA8]
        self.clock = self.clock_25
        self.in_data = bytearray(7)

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.clock = self.clock_25
        elif gain == 64:
            self.clock = self.clock_27
        elif gain == 32:
            self.clock = self.clock_26
        
        self.read() # Para ajustar la ganancia

    def read(self):
        # Esperar a que el sensor esté listo comprobando si el ultimo bit recibido es 0
        while self.spi.xfer2([0x00])[0] & 0x01:
            time.sleep(0.001)

        # Enviar reloj ficticio por MOSI y leer datos
        self.in_data = self.spi.xfer2(self.clock)  

        # Extraer uno no uno si para compensar el reloj ficticio
        result = 0
        for i in range(6):
            result = (result << 4) + (self.in_data[i] & 0x55)

        # Corregir el signo (nº de complemento a dos -> numero con signo)
        return result - ((result & 0x800000) << 1)
    
    def close(self):
        self.spi.close()