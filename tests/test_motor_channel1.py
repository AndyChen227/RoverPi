from gpiozero import Motor, PWMOutputDevice
from time import sleep


# Motor-driver Channel 1 controls both left-side motors.
# BCM GPIO numbering: PWM1=12, INA1=23, INB1=24.
motor = Motor(forward=23, backward=24)
pwm = PWMOutputDevice(12)

try:
    print("Channel 1 test starts in 3 seconds...")
    sleep(3)

    pwm.value = 0.30
    motor.forward()
    sleep(1)
finally:
    motor.stop()
    pwm.off()
    print("Channel 1 stopped.")
