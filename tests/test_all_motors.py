"""Verify four-wheel forward, stop, backward, and final stop in sequence.

Physically verified on 2026-08-10. The sequence is unchanged; only the source
of the pin numbers and polarities moved into rover_pins.
"""

from time import sleep

import rover_pins


rover_pins.warn_and_wait("Four-wheel movement test. All four wheels will move.")

try:
    # This exact sequence was physically verified on 2026-08-10: forward for
    # one second, stopped for two seconds, then backward for one second. The
    # stop between the two directions is what makes the reversal safe.
    print("FORWARD")
    rover_pins.forward()
    sleep(1)

    print("STOP")
    rover_pins.stop()
    sleep(2)

    print("BACKWARD")
    rover_pins.backward()
    sleep(1)
finally:
    # Finish in a known stopped state even after Ctrl+C or an exception.
    rover_pins.stop()
    print("STOP - all motors stopped safely.")
