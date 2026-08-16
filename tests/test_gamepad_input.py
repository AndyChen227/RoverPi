"""Print simple movement words from the DualSense left analog stick.

This test never touches the motor pins, so it is the safe way to rehearse the
controller. Because it now shares rover_input with the driving test, the word
printed here is exactly the command the rover would execute.
"""

import rover_input


gamepad = rover_input.open_gamepad()

# Assume the stick is centered until the controller reports otherwise.
x = rover_input.CENTER
y = rover_input.CENTER
last_command = None

print("Move the left stick. Press Ctrl+C to exit.")

try:
    while True:
        try:
            axes = rover_input.read_axis_events(gamepad)
        except ConnectionError as error:
            print(f"CONTROLLER LOST ({error}).")
            break

        if not axes:
            # Silence just means the stick has not moved.
            continue

        # Store the newest value for each axis. Other absolute axes such as
        # triggers and motion sensors were already filtered out.
        for code, value in axes:
            if code == rover_input.ecodes.ABS_X:
                x = value
            else:
                y = value

        # classify() is the same function the driving test uses: vertical
        # input first, horizontal only while the vertical axis is centered.
        command = rover_input.classify(x, y)
        if command != last_command:
            print(f"{command.upper()} x={x} y={y}")
            last_command = command
except KeyboardInterrupt:
    print("\nCtrl+C detected. No motor pins were used by this test.")
