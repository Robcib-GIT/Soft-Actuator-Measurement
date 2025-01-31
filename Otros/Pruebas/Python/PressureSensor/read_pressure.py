import spidev
import time

# Configurar SPI
spi = spidev.SpiDev()
spi.open(0, 1)  # Open SPI bus 0, device (CS) 0


# Configurar velocidad de reloj (ajustable)
spi.max_speed_hz = 10000  # 500 kHz
spi.mode = 0b10  # CPOL = 0, CPHA = 0



def read_pressure():
    
    # Send 24 empty bits (3 bytes of zeros)
    raw_data = spi.xfer2([0x00, 0x00, 0x00])  # Enviar 3 bytes vacíos para generar los pulsos
    #resultado = (raw_data[0] << 16) | (raw_data[1] << 8) | raw_data[2]  # Combinar los 3 bytes

    # Convertir a valor entero (24 bits, complemento a dos)
    #if resultado & 0x800000:  # Si el bit más alto está en 1 (negativo en complemento a dos)
    #    resultado -= 0x1000000

    return raw_data

    

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