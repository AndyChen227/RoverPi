from evdev import InputDevice, ecodes


# Event numbers are session-specific and can change after reconnecting/rebooting.
gamepad = InputDevice("/dev/input/event11")

CENTER = 128
DEAD_ZONE = 35

x = CENTER
y = CENTER

print("Connected to:")
print(gamepad)

for event in gamepad.read_loop():
    if event.type != ecodes.EV_ABS:
        continue

    if event.code == ecodes.ABS_X:
        x = event.value
    elif event.code == ecodes.ABS_Y:
        y = event.value
    else:
        continue

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
