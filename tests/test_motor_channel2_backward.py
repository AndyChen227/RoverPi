"""Briefly run the two right-side motors backward, then stop safely."""

# PWMOutputDevice sets speed; two DigitalOutputDevice objects set direction.
from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep


# BCM wiring for motor-driver Channel 2 (the two right-side motors).
PWM2 = PWMOutputDevice(13)
INA2 = DigitalOutputDevice(5)
INB2 = DigitalOutputDevice(6)


def motor_stop():
    """Set speed to zero and return both direction pins to low."""
    PWM2.value = 0
    INA2.off()
    INB2.off()


def motor_backward(speed=0.30):
    """Use the physically verified right-side reverse polarity."""
    # This is exactly the inverse of right-side forward.
    INA2.off()
    INB2.on()
    PWM2.value = speed


motor_stop()
print("Channel 2 backward test starts in 3 seconds...")
sleep(3)

try:
    # Run at the verified low test speed for only one second.
    motor_backward(0.30)
    sleep(1)
finally:
    # The cleanup path is intentionally independent of how the test exits.
    motor_stop()
    print("Channel 2 stopped safely.")
