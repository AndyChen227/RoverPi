"""Shared motor-driver definitions for the RoverPi hardware tests.

This module is the single place where verified pin numbers, verified direction
polarities, and the safe test speed are defined. Before this file existed, the
same six pin objects and the same stop/forward/backward helpers were copied
into every test program, so a wiring change had to be repeated seven times.

Every value below was physically verified on the rover. Do not change a
polarity here unless a new physical test proves the new value.

All GPIO numbers are Broadcom (BCM) numbers, not physical header pins.
See docs/wiring.md for the full map and the physical-pin translation.
"""

from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep


# ---------------------------------------------------------------------------
# Verified BCM pin map
# ---------------------------------------------------------------------------
# Channel 1 drives the two left-side motors.
PWM1 = PWMOutputDevice(12)
INA1 = DigitalOutputDevice(23)
INB1 = DigitalOutputDevice(24)

# Channel 2 drives the two right-side motors.
PWM2 = PWMOutputDevice(13)
INA2 = DigitalOutputDevice(5)
INB2 = DigitalOutputDevice(6)


# ---------------------------------------------------------------------------
# Verified test parameters
# ---------------------------------------------------------------------------
# 30% PWM is the validated low test speed. Do not raise it until a higher
# speed has been separately validated with the wheels lifted.
SPEED = 0.30

# Seconds to hold both PWM channels at zero before reversing direction. The
# motors are still spinning at the instant a direction pin flips, so cutting
# power first protects the driver MOSFETs and the LiPo from a current spike.
DIRECTION_CHANGE_DELAY = 0.05

# Seconds of visible warning before any script is allowed to move a wheel.
WARNING_DELAY = 3


# ---------------------------------------------------------------------------
# Verified direction polarities
# ---------------------------------------------------------------------------
# The left and right motors face opposite directions on the chassis, so
# "rover forward" needs opposite electrical states on the two channels. Each
# tuple below is (INA, INB) for that channel, where True means the pin is high.
LEFT_FORWARD = (False, True)
LEFT_BACKWARD = (True, False)
LEFT_OFF = (False, False)

RIGHT_FORWARD = (True, False)
RIGHT_BACKWARD = (False, True)
RIGHT_OFF = (False, False)


# The last command that was actually written to the pins. Tracking it lets the
# module skip redundant GPIO writes when the same command repeats, and lets it
# insert the direction-change delay only when the direction really changes.
_current_command = None

# The same idea for the two single-channel tests, which drive one side only.
_left_state = None
_right_state = None


def _set(pin, active):
    """Drive one direction pin high (True) or low (False)."""
    if active:
        pin.on()
    else:
        pin.off()


def _apply(name, left, right, speed):
    """Write one complete movement command to both driver channels.

    ``left`` and ``right`` are (INA, INB) tuples from the verified polarity
    constants above. ``name`` identifies the command so repeated events do not
    rewrite pins that are already in the correct state.
    """
    global _current_command

    # The gamepad sends many events per second. Rewriting identical pin states
    # thousands of times adds nothing, so an unchanged command returns early.
    if _current_command == (name, speed):
        return

    # Reversing direction while the motors are still turning is the one case
    # that needs a protective pause at zero power first. Starting from a
    # stopped state does not, because PWM is already zero.
    previous = _current_command[0] if _current_command else None
    if previous is not None and previous != "stop" and previous != name:
        PWM1.value = 0
        PWM2.value = 0
        sleep(DIRECTION_CHANGE_DELAY)

    _set(INA1, left[0])
    _set(INB1, left[1])
    _set(INA2, right[0])
    _set(INB2, right[1])
    PWM1.value = speed
    PWM2.value = speed

    _current_command = (name, speed)


# ---------------------------------------------------------------------------
# Whole-rover commands
# ---------------------------------------------------------------------------
def stop():
    """Remove PWM power and clear all four direction pins."""
    global _current_command, _left_state, _right_state
    PWM1.value = 0
    PWM2.value = 0
    INA1.off()
    INB1.off()
    INA2.off()
    INB2.off()
    _current_command = ("stop", 0)
    _left_state = (LEFT_OFF, 0)
    _right_state = (RIGHT_OFF, 0)


def forward(speed=SPEED):
    """Both sides rover-forward. Physically verified 2026-08-10."""
    _apply("forward", LEFT_FORWARD, RIGHT_FORWARD, speed)


def backward(speed=SPEED):
    """Both sides rover-backward. Physically verified 2026-08-10."""
    _apply("backward", LEFT_BACKWARD, RIGHT_BACKWARD, speed)


def turn_left(speed=SPEED):
    """Spin left: left side backward, right side forward.

    Fully verified. The pin combination was confirmed in a driving session
    after 2026-08-10: the rover spins left when these four direction inputs
    are applied. The dominant-axis stick region that requests the turn was
    confirmed separately on 2026-08-16, on the ground.
    """
    _apply("turn_left", LEFT_BACKWARD, RIGHT_FORWARD, speed)


def turn_right(speed=SPEED):
    """Spin right: left side forward, right side backward.

    Physically verified in the same sessions as turn_left(), including the
    2026-08-16 ground drive under the dominant-axis rule.
    """
    _apply("turn_right", LEFT_FORWARD, RIGHT_BACKWARD, speed)


# ---------------------------------------------------------------------------
# Single-channel commands, used by the one-side validation tests
# ---------------------------------------------------------------------------
def left_only(direction, speed=SPEED):
    """Drive only Channel 1. ``direction`` is a LEFT_* polarity tuple."""
    global _current_command, _left_state

    if _left_state == (direction, speed):
        return

    # Same reversal protection as the whole-rover commands: cut power and let
    # the motors settle before flipping a direction pin.
    previous = _left_state[0] if _left_state else None
    if previous is not None and previous != LEFT_OFF and previous != direction:
        PWM1.value = 0
        sleep(DIRECTION_CHANGE_DELAY)

    _set(INA1, direction[0])
    _set(INB1, direction[1])
    PWM1.value = 0 if direction == LEFT_OFF else speed

    _left_state = (direction, speed)
    _current_command = None


def right_only(direction, speed=SPEED):
    """Drive only Channel 2. ``direction`` is a RIGHT_* polarity tuple."""
    global _current_command, _right_state

    if _right_state == (direction, speed):
        return

    previous = _right_state[0] if _right_state else None
    if previous is not None and previous != RIGHT_OFF and previous != direction:
        PWM2.value = 0
        sleep(DIRECTION_CHANGE_DELAY)

    _set(INA2, direction[0])
    _set(INB2, direction[1])
    PWM2.value = 0 if direction == RIGHT_OFF else speed

    _right_state = (direction, speed)
    _current_command = None


def warn_and_wait(message):
    """Start from a known stopped state, warn, and pause before any movement."""
    stop()
    print(message)
    print(f"Movement starts in {WARNING_DELAY} seconds. Lift all four wheels.")
    sleep(WARNING_DELAY)
