import spidev
import time

# Configurar SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device (CS) 0


# Configurar velocidad de reloj (ajustable)
spi.max_speed_hz = 500000  # 500 kHz
spi.mode = 0b00  # CPOL = 0, CPHA = 0
spi.bits_per_word = 8  # SPI bits per word



def read_pressure():
    # Send 3 bytes of zeros to read 24 bits of data
    raw_data = spi.xfer2([0, 0, 0])  # Enviar 3 bytes vacíos para generar los pulsos

    # Combine the 3 bytes into a single 24-bit value
    resultado = (raw_data[0] << 16) | (raw_data[1] << 8) | raw_data[2]

    # Convertir a valor entero (24 bits, complemento a dos)
    if resultado & 0x800000:  # Si el bit más alto está en 1 (negativo en complemento a dos)
        resultado -= 0x1000000

    return resultado

    

def main():
    try:
        while True:
            pressure = read_pressure()
            print(f"Pressure: {pressure}")
            time.sleep(1)  # Delay between readings
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # Close SPI
        spi.close()

if __name__ == "__main__":
    main()