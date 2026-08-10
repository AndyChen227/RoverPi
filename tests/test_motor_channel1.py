"""Briefly run the two left-side motors forward, then stop them safely."""

# PWMOutputDevice controls motor speed; DigitalOutputDevice sets direction.
# sleep() creates a warning delay and limits how long the wheels run.
from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep


# Channel 1 drives both left-side motors. These are BCM GPIO numbers, not
# physical header-pin numbers: PWM1=GPIO12, INA1=GPIO23, INB1=GPIO24.
PWM1 = PWMOutputDevice(12)
INA1 = DigitalOutputDevice(23)
INB1 = DigitalOutputDevice(24)


def motor_stop():
    """Remove PWM power and place both direction inputs in the inactive state."""
    PWM1.value = 0
    INA1.off()
    INB1.off()


def motor_forward(speed=0.30):
    """Run the left side in its physically verified rover-forward direction."""
    # The left motors are mounted opposite the right motors. On this build,
    # rover-forward is INA1 low and INB1 high; do not reverse this polarity.
    INA1.off()
    INB1.on()
    PWM1.value = speed


# Start from a known stopped state, warn the operator, and allow three seconds
# to confirm that the wheels are lifted clear of the floor.
motor_stop()
print("Channel 1 forward test starts in 3 seconds...")
sleep(3)

try:
    # Apply 30% PWM for one second. This exact low-speed pattern was verified
    # on the physical rover on 2026-08-10.
    motor_forward(0.30)
    sleep(1)
finally:
    # A finally block runs after success, Ctrl+C, or most runtime errors, so the
    # test does not intentionally leave the motors powered.
    motor_stop()
    print("Channel 1 stopped safely.")
