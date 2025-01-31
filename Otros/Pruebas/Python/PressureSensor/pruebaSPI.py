import spidev

spi = spidev.SpiDev()
spi.open(0, 0)  # Usar SPI1, CS0 (ajustar si usas otro)
spi.max_speed_hz = 500000  # Velocidad de reloj
spi.mode = 0  # Modo SPI (CPOL=0, CPHA=0)
spi.bits_per_word = 8

# Enviar y recibir datos (debe recibir lo mismo que envía)
send_data = [0xAA, 0x55, 0xFF]  # Datos de prueba
received_data = spi.xfer2(send_data)

print("Enviado:", send_data)
print("Recibido:", received_data)

spi.close()
