"""Verify four-wheel forward, stop, backward, and final stop in sequence."""

# Each driver channel receives one PWM speed signal and two direction signals.
from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep


# Channel 1 drives the left side; Channel 2 drives the right side. All values
# below use Broadcom (BCM) GPIO numbering.
PWM1 = PWMOutputDevice(12)
INA1 = DigitalOutputDevice(23)
INB1 = DigitalOutputDevice(24)
PWM2 = PWMOutputDevice(13)
INA2 = DigitalOutputDevice(5)
INB2 = DigitalOutputDevice(6)


def stop():
    """Disable both speed outputs and clear all four direction inputs."""
    PWM1.value = 0
    PWM2.value = 0
    INA1.off()
    INB1.off()
    INA2.off()
    INB2.off()


def forward(speed=0.30):
    """Apply the verified rover-forward polarity to both sides."""
    # Left forward: A1 low/B1 high. Right forward: A2 high/B2 low.
    INA1.off()
    INB1.on()
    INA2.on()
    INB2.off()
    PWM1.value = speed
    PWM2.value = speed


def backward(speed=0.30):
    """Reverse the verified forward polarity on both sides."""
    INA1.on()
    INB1.off()
    INA2.off()
    INB2.on()
    PWM1.value = speed
    PWM2.value = speed


# Begin stopped and provide a visible three-second safety warning.
stop()
print("WARNING: all four wheels will move in 3 seconds.")
sleep(3)

try:
    # This exact sequence was physically verified on 2026-08-10: forward for
    # one second, stopped for two seconds, then backward for one second.
    print("FORWARD")
    forward(0.30)
    sleep(1)
    print("STOP")
    stop()
    sleep(2)
    print("BACKWARD")
    backward(0.30)
    sleep(1)
finally:
    # Finish in a known stopped state even after Ctrl+C or an exception.
    stop()
    print("STOP - all motors stopped safely.")
