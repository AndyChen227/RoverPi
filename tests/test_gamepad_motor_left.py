"""Control the verified left-side motor channel with DualSense ABS_Y.

Physically verified on 2026-08-10 with a 20-count dead zone. The dead zone is
now the shared 35 counts and a disconnect watchdog was added, so this exact
script has not been re-run on the rover yet.
"""

import rover_input
import rover_pins


gamepad = rover_input.open_gamepad()

rover_pins.warn_and_wait("DualSense left-motor test (Channel 1 only).")

last_command = None

try:
    while True:
        try:
            axes = rover_input.read_axis_events(gamepad)
        except ConnectionError as error:
            print(f"CONTROLLER LOST ({error}) - stopping Channel 1.")
            break

        if not axes:
            continue

        # This test deliberately reads only the vertical axis, so a horizontal
        # push must not move the left side.
        y = None
        for code, value in axes:
            if code == rover_input.ecodes.ABS_Y:
                y = value
        if y is None:
            continue

        # A forward push produces a low number; a backward pull produces a
        # high number. Values inside the dead zone command an immediate stop.
        if y < rover_input.LOW_THRESHOLD:
            command = "forward"
            rover_pins.left_only(rover_pins.LEFT_FORWARD)
        elif y > rover_input.HIGH_THRESHOLD:
            command = "backward"
            rover_pins.left_only(rover_pins.LEFT_BACKWARD)
        else:
            command = "stop"
            rover_pins.left_only(rover_pins.LEFT_OFF)

        if command != last_command:
            print(f"{command.upper()} y={y}")
            last_command = command
except KeyboardInterrupt:
    print("\nCtrl+C detected.")
finally:
    # Always remove motor output when the loop ends normally or unexpectedly.
    rover_pins.stop()
    print("Channel 1 stopped safely.")
