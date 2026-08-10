"""Control the verified left-side motor channel with DualSense ABS_Y."""

# evdev supplies controller events; gpiozero controls Channel 1; sleep gives
# the operator time to prepare before the motor can move.
from evdev import InputDevice, ecodes
from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep


# BCM wiring for motor-driver Channel 1 (the two left-side motors).
PWM1 = PWMOutputDevice(12)
INA1 = DigitalOutputDevice(23)
INB1 = DigitalOutputDevice(24)

# This path was correct during the test session only. Discover the current
# eventX value and edit it whenever the controller reconnects or the Pi reboots.
GAMEPAD = "/dev/input/event11"
gamepad = InputDevice(GAMEPAD)

# evdev reported up≈0, center≈128, and down≈255. A 20-count dead zone keeps the
# motors stopped while the stick is released near its imperfect center value.
CENTER = 128
DEADZONE = 20
FORWARD_THRESHOLD = CENTER - DEADZONE
BACKWARD_THRESHOLD = CENTER + DEADZONE


def stop():
    """Stop Channel 1 and clear its two direction inputs."""
    PWM1.value = 0
    INA1.off()
    INB1.off()


def forward(speed=0.30):
    """Use the physically verified left-side forward polarity."""
    INA1.off()
    INB1.on()
    PWM1.value = speed


def backward(speed=0.30):
    """Reverse both left motors by swapping the direction-input states."""
    INA1.on()
    INB1.off()
    PWM1.value = speed


# Ensure a safe initial state, then leave three seconds to lift the wheels.
stop()
print("DualSense left-motor test starts in 3 seconds...")
sleep(3)

try:
    # Process only the left stick's vertical ABS_Y reports.
    for event in gamepad.read_loop():
        if event.type != ecodes.EV_ABS or event.code != ecodes.ABS_Y:
            continue

        # A forward push produces a low number; a backward pull produces a
        # high number. Values in the middle command an immediate stop.
        if event.value < FORWARD_THRESHOLD:
            print(f"FORWARD y={event.value}")
            forward()
        elif event.value > BACKWARD_THRESHOLD:
            print(f"BACKWARD y={event.value}")
            backward()
        else:
            print(f"STOP y={event.value}")
            stop()
except KeyboardInterrupt:
    print("\nCtrl+C detected.")
finally:
    # Always remove motor output when the loop ends normally or unexpectedly.
    stop()
    print("Channel 1 stopped safely.")
