from evdev import InputDevice


# event numbers are session-specific and can change after reconnecting/rebooting.
gamepad = InputDevice("/dev/input/event11")

print("Connected to:")
print(gamepad)
