"""Print simple movement words from the DualSense left analog stick."""

# evdev reads Linux input events. InputDevice opens one device file, while
# ecodes provides readable names for event types and joystick axes.
from evdev import InputDevice, ecodes


# event11 was the main controller during the verified session, but eventX is
# assigned dynamically. Re-check /proc/bus/input/devices after every reconnect
# or reboot and update this path before running the test.
GAMEPAD = "/dev/input/event11"
gamepad = InputDevice(GAMEPAD)

# In evdev, the observed DualSense ABS_X/ABS_Y range was approximately 0..255,
# with 128 at center. DEAD_ZONE prevents small resting noise from causing input.
CENTER = 128
DEAD_ZONE = 35
x = CENTER
y = CENTER

print("Connected to:")
print(gamepad)

# read_loop() waits for controller events until the program is interrupted.
for event in gamepad.read_loop():
    # Ignore buttons, touchpad data, and other event families; this test only
    # needs absolute analog-axis events.
    if event.type != ecodes.EV_ABS:
        continue

    # Store the newest X or Y value. Ignore all other absolute axes so triggers
    # and motion sensors cannot affect the printed movement word.
    if event.code == ecodes.ABS_X:
        x = event.value
    elif event.code == ecodes.ABS_Y:
        y = event.value
    else:
        continue

    # Vertical input is checked first: up is near 0 and down is near 255.
    # Horizontal input is used only while Y remains inside its dead zone.
    if y < CENTER - DEAD_ZONE:
        print("FORWARD")
    elif y > CENTER + DEAD_ZONE:
        print("BACKWARD")
    elif x < CENTER - DEAD_ZONE:
        print("LEFT")
    elif x > CENTER + DEAD_ZONE:
        print("RIGHT")
    else:
        print("STOP")
