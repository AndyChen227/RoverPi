from evdev import InputDevice, ecodes

gamepad = InputDevice("/dev/input/event11")

CENTER = 128
DEAD_ZONE = 35

x = CENTER
y = CENTER

print("Connected to:")
print(gamepad)
print("Move the left stick. Press Ctrl+C to stop.")

for event in gamepad.read_loop():
    if event.type == ecodes.EV_ABS:

        if event.code == ecodes.ABS_X:
            x = event.value

        elif event.code == ecodes.ABS_Y:
            y = event.value

        else:
            continue

        dx = x - CENTER
        dy = y - CENTER

        if abs(dx) < DEAD_ZONE and abs(dy) < DEAD_ZONE:
            print("STOP")

        elif abs(dy) > abs(dx):
            if dy < -DEAD_ZONE:
                print("FORWARD")
            elif dy > DEAD_ZONE:
                print("BACKWARD")

        else:
            if dx < -DEAD_ZONE:
                print("LEFT")
            elif dx > DEAD_ZONE:
                print("RIGHT")