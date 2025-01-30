import Jetson.GPIO as GPIO
import time

# Pin definitions
SCK_PIN = 18  # GPIO pin for SCK
DT_PIN = 23   # GPIO pin for DT

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SCK_PIN, GPIO.OUT)
GPIO.setup(DT_PIN, GPIO.IN)

def read_hx710b():
    # Wait for the DT pin to go low (data ready)
    while GPIO.input(DT_PIN) == 1:
        pass

    # Read 24 bits of data
    data = 0
    for _ in range(24):
        GPIO.output(SCK_PIN, 1)
        time.sleep(0.00001)  # Small delay for clock pulse
        GPIO.output(SCK_PIN, 0)
        time.sleep(0.00001)
        data = (data << 1) | GPIO.input(DT_PIN)

    # Send an additional clock pulse to set the gain
    GPIO.output(SCK_PIN, 1)
    time.sleep(0.00001)
    GPIO.output(SCK_PIN, 0)
    time.sleep(0.00001)

    # Convert the 24-bit data to a signed integer
    if data & 0x800000:  # Check if the sign bit is set
        data -= 0x1000000

    return data

def main():
    try:
        while True:
            pressure_value = read_hx710b()
            print(f"Pressure Value: {pressure_value}")
            time.sleep(seconds=1)  # Delay between readings
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()