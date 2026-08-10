"""Drive all four motors from the DualSense left stick at 30% PWM.

Forward, backward, and stop were physically verified on 2026-08-10.
Left/right spin-turn logic is implemented but has NOT been physically tested.
"""

# evdev reads the controller; gpiozero generates motor-driver signals; sleep
# provides a safety delay before the event loop can move the rover.
from evdev import InputDevice, ecodes
from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep


# Verified BCM GPIO map for both motor-driver channels.
PWM1 = PWMOutputDevice(12)
INA1 = DigitalOutputDevice(23)
INB1 = DigitalOutputDevice(24)
PWM2 = PWMOutputDevice(13)
INA2 = DigitalOutputDevice(5)
INB2 = DigitalOutputDevice(6)

# event11 is only the value from the verified session. Linux may assign a new
# eventX number after reconnecting or rebooting; discover and update it first.
GAMEPAD = "/dev/input/event11"
gamepad = InputDevice(GAMEPAD)
LEFT_STICK_X = ecodes.ABS_X
LEFT_STICK_Y = ecodes.ABS_Y

# Observed evdev calibration: left/up≈0, center≈128, right/down≈255.
CENTER = 128
DEADZONE = 20
LOW_THRESHOLD = CENTER - DEADZONE
HIGH_THRESHOLD = CENTER + DEADZONE
SPEED = 0.30
x = CENTER
y = CENTER


def stop():
    """Remove PWM power and clear all direction pins."""
    PWM1.value = 0
    PWM2.value = 0
    INA1.off()
    INB1.off()
    INA2.off()
    INB2.off()


def forward(speed=SPEED):
    """Use the physically verified forward polarity on both sides."""
    INA1.off()
    INB1.on()
    INA2.on()
    INB2.off()
    PWM1.value = speed
    PWM2.value = speed


def backward(speed=SPEED):
    """Use the physically verified backward polarity on both sides."""
    INA1.on()
    INB1.off()
    INA2.off()
    INB2.on()
    PWM1.value = speed
    PWM2.value = speed


def turn_left(speed=SPEED):
    """Spin left: left side backward and right side forward (UNVERIFIED)."""
    # This differential-drive combination is implemented from the verified
    # side polarities, but the complete turn has not been tested on the rover.
    INA1.on()
    INB1.off()
    INA2.on()
    INB2.off()
    PWM1.value = speed
    PWM2.value = speed


def turn_right(speed=SPEED):
    """Spin right: left side forward and right side backward (UNVERIFIED)."""
    # As above, this combination is logically correct but awaits a safe,
    # wheels-lifted physical verification.
    INA1.off()
    INB1.on()
    INA2.off()
    INB2.on()
    PWM1.value = speed
    PWM2.value = speed


def update_movement():
    """Translate the latest X/Y values into one discrete movement command."""
    # Horizontal commands intentionally have priority in this simple test.
    # Avoid diagonal input until a future analog mixing controller is added.
    if x < LOW_THRESHOLD:
        print(f"LEFT (UNVERIFIED TURN) x={x} y={y}")
        turn_left()
    elif x > HIGH_THRESHOLD:
        print(f"RIGHT (UNVERIFIED TURN) x={x} y={y}")
        turn_right()
    elif y < LOW_THRESHOLD:
        print(f"FORWARD x={x} y={y}")
        forward()
    elif y > HIGH_THRESHOLD:
        print(f"BACKWARD x={x} y={y}")
        backward()
    else:
        print(f"STOP x={x} y={y}")
        stop()


# Establish a safe initial state and allow time to lift all wheels.
stop()
print("RoverPi full gamepad test starts in 3 seconds.")
print("WARNING: left/right turn behavior is not yet physically verified.")
sleep(3)

try:
    # Update only the two left-stick axes. Each new reading immediately
    # recalculates the movement command from the latest stored X and Y values.
    for event in gamepad.read_loop():
        if event.type != ecodes.EV_ABS:
            continue
        if event.code == LEFT_STICK_X:
            x = event.value
            update_movement()
        elif event.code == LEFT_STICK_Y:
            y = event.value
            update_movement()
except KeyboardInterrupt:
    print("\nCtrl+C detected.")
finally:
    # Always attempt a software stop when the program exits.
    stop()
    print("All motors stopped safely.")
