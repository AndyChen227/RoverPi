"""Drive all four motors from the DualSense left stick at 30% PWM.

Forward, backward, and stop were physically verified on 2026-08-10.
Left/right spin-turn logic is implemented but has NOT been physically tested.

Changed on 2026-08-16 and awaiting a new physical run:
  - the dead zone widened from 20 to the shared 35 counts;
  - the vertical axis now has priority over the horizontal axis;
  - a disconnect watchdog stops both channels if the controller goes away.
"""

import rover_input
import rover_pins


# Every pin number, polarity, and speed comes from rover_pins. Every controller
# threshold comes from rover_input. Neither is redefined here, so this file
# contains only the decision loop.
COMMANDS = {
    "stop": rover_pins.stop,
    "forward": rover_pins.forward,
    "backward": rover_pins.backward,
    "turn_left": rover_pins.turn_left,
    "turn_right": rover_pins.turn_right,
}

gamepad = rover_input.open_gamepad()

# Assume the stick is centered until the controller reports otherwise.
x = rover_input.CENTER
y = rover_input.CENTER
last_command = None

rover_pins.warn_and_wait(
    "RoverPi full gamepad test.\n"
    "WARNING: left/right turn behavior is not yet physically verified."
)

try:
    while True:
        try:
            axes = rover_input.read_axis_events(gamepad)
        except ConnectionError as error:
            # This is the fail-safe: without it, a dropped Bluetooth link left
            # the last PWM command applied and the rover kept driving.
            print(f"CONTROLLER LOST ({error}) - stopping both channels.")
            break

        if not axes:
            # No new stick data, controller still present: hold the current
            # command. A DualSense sends nothing while it is held still.
            continue

        for code, value in axes:
            if code == rover_input.ecodes.ABS_X:
                x = value
            else:
                y = value

        command = rover_input.classify(x, y)

        # Print only on change so the console stays readable and the loop is
        # not slowed down by hundreds of identical lines per second.
        if command != last_command:
            note = " (UNVERIFIED TURN)" if command.startswith("turn_") else ""
            print(f"{command.upper()}{note} x={x} y={y}")
            last_command = command

        COMMANDS[command]()
except KeyboardInterrupt:
    print("\nCtrl+C detected.")
finally:
    # Always attempt a software stop when the program exits. This is not a
    # substitute for the physical power switch.
    rover_pins.stop()
    print("All motors stopped safely.")
