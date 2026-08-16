"""Briefly run the two right-side motors backward, then stop safely.

Physically verified on 2026-08-10. This is exactly the inverse of right-side
forward, kept in rover_pins.RIGHT_BACKWARD.
"""

from time import sleep

import rover_pins


rover_pins.warn_and_wait("Channel 2 backward test (right side only).")

try:
    # Run at the verified low test speed for only one second.
    rover_pins.right_only(rover_pins.RIGHT_BACKWARD)
    sleep(1)
finally:
    # The cleanup path is intentionally independent of how the test exits.
    rover_pins.stop()
    print("Channel 2 stopped safely.")
