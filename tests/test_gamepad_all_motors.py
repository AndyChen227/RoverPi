from evdev import InputDevice, ecodes
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


# ==========================================
# DualSense
# ==========================================
GAMEPAD = "/dev/input/event11"
gamepad = InputDevice(GAMEPAD)

LEFT_STICK_X = ecodes.ABS_X
LEFT_STICK_Y = ecodes.ABS_Y


# ==========================================
# Stick calibration
#
# X:
# Left   ≈ 0
# Center ≈ 128
# Right  ≈ 255
#
# Y:
# Up     ≈ 0
# Center ≈ 128
# Down   ≈ 255
# ==========================================
CENTER = 128
DEADZONE = 20

LOW_THRESHOLD = CENTER - DEADZONE    # 108
HIGH_THRESHOLD = CENTER + DEADZONE  # 148

SPEED = 0.30


# Current stick position
x = CENTER
y = CENTER


# ==========================================
# Motor functions
# ==========================================

def stop():
    PWM1.value = 0
    PWM2.value = 0

    INA1.off()
    INB1.off()

    INA2.off()
    INB2.off()


def forward(speed=SPEED):

    # Left forward
    INA1.off()
    INB1.on()

    # Right forward
    INA2.on()
    INB2.off()

    PWM1.value = speed
    PWM2.value = speed


def backward(speed=SPEED):

    # Left backward
    INA1.on()
    INB1.off()

    # Right backward
    INA2.off()
    INB2.on()

    PWM1.value = speed
    PWM2.value = speed


def turn_left(speed=SPEED):

    # Left side backward
    INA1.on()
    INB1.off()

    # Right side forward
    INA2.on()
    INB2.off()

    PWM1.value = speed
    PWM2.value = speed


def turn_right(speed=SPEED):

    # Left side forward
    INA1.off()
    INB1.on()

    # Right side backward
    INA2.off()
    INB2.on()

    PWM1.value = speed
    PWM2.value = speed


# ==========================================
# Decide rover movement
# ==========================================

def update_movement():

    # LEFT / RIGHT gets priority for this test

    if x < LOW_THRESHOLD:
        print(f"LEFT       x={x} y={y}")
        turn_left()

    elif x > HIGH_THRESHOLD:
        print(f"RIGHT      x={x} y={y}")
        turn_right()

    elif y < LOW_THRESHOLD:
        print(f"FORWARD    x={x} y={y}")
        forward()

    elif y > HIGH_THRESHOLD:
        print(f"BACKWARD   x={x} y={y}")
        backward()

    else:
        print(f"STOP       x={x} y={y}")
        stop()


# ==========================================
# Start
# ==========================================

print("====================================")
print("RoverPi - Full Gamepad Driving Test")
print("====================================")
print()
print("Stick UP     -> FORWARD")
print("Stick DOWN   -> BACKWARD")
print("Stick LEFT   -> TURN LEFT")
print("Stick RIGHT  -> TURN RIGHT")
print("Stick CENTER -> STOP")
print()
print("Press Ctrl+C to stop safely.")
print()
print("Starting in 3 seconds...")
print()

stop()
sleep(3)


try:

    for event in gamepad.read_loop():

        if event.type == ecodes.EV_ABS:

            if event.code == LEFT_STICK_X:
                x = event.value
                update_movement()

            elif event.code == LEFT_STICK_Y:
                y = event.value
                update_movement()


except KeyboardInterrupt:
    print("\nCtrl+C detected.")


finally:
    stop()
    print("All motors stopped safely.")