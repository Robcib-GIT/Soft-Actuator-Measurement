import DPS

from time import sleep


dps310 = DPS.DPS(0x77,0)
units = "Pa"
try:
        pressure = dps310.measurePressureOnce(units)
        print(f'Presión: {pressure:8.1f} {units}')
        dps310.tare_pressure()

        while True:

            pressure = dps310.measurePressureOnce(units)

            print(f'Presión: {pressure:8.2f} {units}')

            sleep(0.1)
        

except KeyboardInterrupt:

        pass