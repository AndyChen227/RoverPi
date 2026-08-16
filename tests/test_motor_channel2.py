"""Briefly run the two right-side motors forward, then stop them safely.

Physically verified on 2026-08-10. Right-side rover-forward is the opposite
input combination from the left side, because the motors face opposite
directions on the chassis. That polarity lives in rover_pins.RIGHT_FORWARD.
"""

from time import sleep

import rover_pins


rover_pins.warn_and_wait("Channel 2 forward test (right side only).")

try:
    # The physical rover passed this one-second test at 30% PWM on 2026-08-10.
    rover_pins.right_only(rover_pins.RIGHT_FORWARD)
    sleep(1)
finally:
    # Stop even if execution is interrupted during the timed movement.
    rover_pins.stop()
    print("Channel 2 stopped safely.")
