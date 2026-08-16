"""Shared DualSense input handling for the RoverPi gamepad tests.

This module holds the observed controller calibration and the reading loop, so
that a test which only *watches* the stick and a test which actually *drives*
the motors interpret exactly the same numbers in exactly the same way.

Keeping them in one place matters: before this file existed, the read-only
rehearsal test used a 35-count dead zone and gave the vertical axis priority,
while the test that moved all four wheels used a 20-count dead zone and gave
the horizontal axis priority. Practising with one and driving with the other
meant the rehearsal did not predict the rover's real behavior.
"""

import os
from select import select

from evdev import InputDevice, ecodes


# ---------------------------------------------------------------------------
# Controller device path
# ---------------------------------------------------------------------------
# event11 was the main controller during the verified session only. Linux
# assigns /dev/input/eventX dynamically, so re-check it after every reconnect
# or reboot and update this value:
#
#     cat /proc/bus/input/devices | grep -A 8 "DualSense Wireless Controller"
#
# Use the handler line that contains both js0 and eventX. The motion-sensor
# and touchpad interfaces are separate devices and will not work here.
GAMEPAD = "/dev/input/event11"


# ---------------------------------------------------------------------------
# Observed evdev calibration
# ---------------------------------------------------------------------------
# In the verified session both left-stick axes reported roughly 0..255:
#   ABS_X: left about 0, center about 128, right about 255
#   ABS_Y: forward about 0, center about 128, backward about 255
#
# jstest reports the same physical stick as -32767..+32767. Never copy a
# threshold or a sign from one API into code that reads the other.
CENTER = 128

# 35 counts is the dead zone that was wide enough to keep the read-only test
# quiet with the stick released. The motor tests now use the same value; a
# narrower dead zone risks a released stick still commanding movement.
DEADZONE = 35
LOW_THRESHOLD = CENTER - DEADZONE
HIGH_THRESHOLD = CENTER + DEADZONE

# How long to wait for controller traffic before checking that the controller
# is still connected. A DualSense sends nothing while it is held perfectly
# still, so silence alone must never be treated as a fault.
POLL_TIMEOUT = 0.2


def open_gamepad(path=GAMEPAD):
    """Open the controller and fail with a readable message if it is missing."""
    if not os.path.exists(path):
        raise SystemExit(
            f"{path} does not exist.\n"
            "Reconnect the DualSense and find the current event number with:\n"
            '  cat /proc/bus/input/devices | grep -A 8 "DualSense Wireless Controller"'
        )
    device = InputDevice(path)
    print("Connected to:")
    print(device)
    return device


def read_axis_events(device, timeout=POLL_TIMEOUT):
    """Yield (code, value) for left-stick events, or raise on disconnect.

    Returns an empty list when the timeout expires and the controller is still
    present, which simply means the stick has not moved. Raises ConnectionError
    when the controller has actually gone away, so the caller can stop the
    motors instead of holding the last command forever.
    """
    ready, _, _ = select([device], [], [], timeout)

    if not ready:
        # Silence is normal. Silence plus a vanished device node is not: a
        # disconnected Bluetooth controller removes its /dev/input entry.
        if not os.path.exists(device.path):
            raise ConnectionError("controller device node disappeared")
        return []

    try:
        events = list(device.read())
    except OSError as error:
        # The device node can also fail mid-read during a disconnect.
        raise ConnectionError(f"controller read failed: {error}") from error

    axes = []
    for event in events:
        # Ignore buttons, triggers, touchpad and motion data. Only the two
        # left-stick absolute axes are used for driving.
        if event.type != ecodes.EV_ABS:
            continue
        if event.code in (ecodes.ABS_X, ecodes.ABS_Y):
            axes.append((event.code, event.value))
    return axes


def classify(x, y):
    """Turn the latest stick position into one discrete movement word.

    Vertical input has priority. The horizontal axis is read only while the
    vertical axis is inside its dead zone, so a slightly angled forward push
    drives forward instead of unexpectedly spinning the rover in place.
    """
    if y < LOW_THRESHOLD:
        return "forward"
    if y > HIGH_THRESHOLD:
        return "backward"
    if x < LOW_THRESHOLD:
        return "turn_left"
    if x > HIGH_THRESHOLD:
        return "turn_right"
    return "stop"
