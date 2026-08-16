from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep


# =========================
# Motor Driver - Channel 2
# Right-side motors
# =========================
PWM2 = PWMOutputDevice(13)
INA2 = DigitalOutputDevice(5)
INB2 = DigitalOutputDevice(6)


def motor_stop():
    PWM2.value = 0
    INA2.off()
    INB2.off()


def motor_backward(speed=0.30):
    INA2.off()
    INB2.on()
    PWM2.value = speed


print("===================================")
print("RoverPi - Channel 2 Backward Test")
print("===================================")
print()
print("Right-side motors will run BACKWARD")
print("at 30% PWM for about 1 second.")
print()
print("Starting in 3 seconds...")
print()

motor_stop()
sleep(3)

try:
    motor_backward(0.30)
    sleep(1)

finally:
    motor_stop()
    print("Channel 2 stopped safely.")