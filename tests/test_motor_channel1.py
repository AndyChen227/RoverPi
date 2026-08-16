from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep

# Motor driver channel 1
PWM1 = PWMOutputDevice(12)      # Physical pin 32
INA1 = DigitalOutputDevice(23)  # Physical pin 16
INB1 = DigitalOutputDevice(24)  # Physical pin 18


def stop():
    PWM1.value = 0
    INA1.off()
    INB1.off()


print("Motor test will start in 3 seconds...")
sleep(3)

INA1.on()
INB1.off()
PWM1.value = 0.3

sleep(1)

stop()

print("Motor test finished.")