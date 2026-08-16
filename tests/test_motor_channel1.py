"""Briefly run the two left-side motors forward, then stop them safely.

Physically verified on 2026-08-10. The pin numbers and the 30% test speed now
come from rover_pins so that a wiring change is made in exactly one place.
"""

from time import sleep

import rover_pins


# Start from a known stopped state, warn the operator, and allow three seconds
# to confirm that the wheels are lifted clear of the floor.
rover_pins.warn_and_wait("Channel 1 forward test (left side only).")

try:
    # Apply 30% PWM for one second. This exact low-speed pattern was verified
    # on the physical rover on 2026-08-10.
    rover_pins.left_only(rover_pins.LEFT_FORWARD)
    sleep(1)
finally:
    # A finally block runs after success, Ctrl+C, or most runtime errors, so the
    # test does not intentionally leave the motors powered.
    rover_pins.stop()
    print("Channel 1 stopped safely.")
