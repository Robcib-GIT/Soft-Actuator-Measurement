import ADS1x15
from time import sleep

ADS = ADS1x15.ADS1115(0, 0x48)

try:
        while True:

                pulse = ADS.readADC(0)
                print(f"Raw: {pulse} |  Voltage: {ADS.toVoltage(pulse)}")
                sleep(1)
        

except KeyboardInterrupt:
        pass

