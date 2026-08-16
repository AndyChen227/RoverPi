from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep


# ==========================================
# Channel 1 - Left-side motors
# ==========================================
PWM1 = PWMOutputDevice(12)
INA1 = DigitalOutputDevice(23)
INB1 = DigitalOutputDevice(24)

# ==========================================
# Channel 2 - Right-side motors
# ==========================================
PWM2 = PWMOutputDevice(13)
INA2 = DigitalOutputDevice(5)
INB2 = DigitalOutputDevice(6)


def stop():
    PWM1.value = 0
    PWM2.value = 0

    INA1.off()
    INB1.off()

    INA2.off()
    INB2.off()


def forward(speed=0.30):
    # Left side - verified forward
    INA1.off()
    INB1.on()

    # Right side - verified forward
    INA2.on()
    INB2.off()

    PWM1.value = speed
    PWM2.value = speed


def backward(speed=0.30):
    # Left side - reverse
    INA1.on()
    INB1.off()

    # Right side - reverse
    INA2.off()
    INB2.on()

    PWM1.value = speed
    PWM2.value = speed


print("===================================")
print("RoverPi - Four Motor Test")
print("===================================")
print()
print("WARNING: All four wheels will move.")
print("Starting in 3 seconds...")
print()

stop()
sleep(3)

try:

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

    stop()
    print("STOP - all motors stopped safely.")