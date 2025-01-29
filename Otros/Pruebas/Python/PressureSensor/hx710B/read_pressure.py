from hx710B import HX710B
import time

# Configurar sensores
pressure_sensor_1 = HX710B(0)

def main():
    try:
        while True:
            pressure = pressure_sensor_1.read()
            print(f"Pressure: {pressure}")
            time.sleep(1)  # Delay between readings
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # Close SPI
        pressure_sensor_1.close()

if __name__ == "__main__":
    main()