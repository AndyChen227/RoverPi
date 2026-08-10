"""Briefly run the two right-side motors forward, then stop them safely."""

# These gpiozero classes map a PWM speed signal and two digital direction
# signals to the second channel of the motor driver.
from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep


# Channel 2 BCM map: PWM2=GPIO13, INA2=GPIO5, INB2=GPIO6.
PWM2 = PWMOutputDevice(13)
INA2 = DigitalOutputDevice(5)
INB2 = DigitalOutputDevice(6)


def motor_stop():
    """Remove speed output and clear both Channel 2 direction inputs."""
    PWM2.value = 0
    INA2.off()
    INB2.off()


def motor_forward(speed=0.30):
    """Run the right side in its physically verified rover-forward direction."""
    # Right-side rover-forward is the opposite input combination from the left
    # side because the motors face opposite directions on the chassis.
    INA2.on()
    INB2.off()
    PWM2.value = speed


motor_stop()
print("Channel 2 forward test starts in 3 seconds...")
sleep(3)

try:
    # The physical rover passed this one-second test at 30% PWM on 2026-08-10.
    motor_forward(0.30)
    sleep(1)
finally:
    # Stop even if execution is interrupted during the timed movement.
    motor_stop()
    print("Channel 2 stopped safely.")
