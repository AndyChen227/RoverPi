from evdev import InputDevice, ecodes
from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep


# =========================
# Motor Driver - Channel 1
# Left-side motors
# =========================
PWM1 = PWMOutputDevice(12)
INA1 = DigitalOutputDevice(23)
INB1 = DigitalOutputDevice(24)


# =========================
# DualSense
# =========================
GAMEPAD = "/dev/input/event11"
gamepad = InputDevice(GAMEPAD)

LEFT_STICK_Y = ecodes.ABS_Y


# =========================
# Stick calibration
#
# Forward  ≈ 0
# Center   ≈ 128
# Backward ≈ 255
# =========================
CENTER = 128
DEADZONE = 20

FORWARD_THRESHOLD = CENTER - DEADZONE   # 108
BACKWARD_THRESHOLD = CENTER + DEADZONE  # 148


def motor_stop():
    PWM1.value = 0
    INA1.off()
    INB1.off()


def motor_forward(speed=0.30):
    # Verified forward polarity
    INA1.off()
    INB1.on()
    PWM1.value = speed


def motor_backward(speed=0.30):
    # Reverse polarity
    INA1.on()
    INB1.off()
    PWM1.value = speed


print("===================================")
print("RoverPi - Gamepad Left Motor Test")
print("===================================")
print()
print("Left stick UP     -> forward")
print("Stick CENTER      -> stop")
print("Left stick DOWN   -> backward")
print()
print("Press Ctrl+C to stop safely.")
print()
print("Starting in 3 seconds...")
print()

motor_stop()
sleep(3)

try:
    for event in gamepad.read_loop():

        if event.type == ecodes.EV_ABS and event.code == LEFT_STICK_Y:

            y = event.value

            # Forward
            if y < FORWARD_THRESHOLD:
                print(f"FORWARD    y={y}")
                motor_forward(0.30)

            # Backward
            elif y > BACKWARD_THRESHOLD:
                print(f"BACKWARD   y={y}")
                motor_backward(0.30)

            # Center / deadzone
            else:
                print(f"STOP       y={y}")
                motor_stop()


except KeyboardInterrupt:
    print("\nCtrl+C detected.")


finally:
    motor_stop()
    print("Motors stopped safely.")