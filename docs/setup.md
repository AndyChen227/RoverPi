# Setup Notes / 设置说明

## Required Python packages

The current tests use `gpiozero` for GPIO output and `evdev` for DualSense input. The Linux joystick tools provide `jstest` for independent controller inspection.

## Reconnect the DualSense / 重新连接 DualSense

1. Put the controller into pairing/connection mode if necessary.
2. Start `bluetoothctl`.
3. Run `power on`, `agent on`, and `default-agent`.
4. Use `devices` or `paired-devices` to find the controller without publishing a private MAC address in this repository.
5. Run `trust <controller-address>` and `connect <controller-address>`.
6. Run `info <controller-address>` and confirm `Paired: yes`, `Trusted: yes`, and `Connected: yes`.
7. Exit `bluetoothctl`.

如有需要，先让手柄进入配对状态，再在 `bluetoothctl` 中打开电源与 agent，通过 `devices` 找到手柄地址，执行 `trust`、`connect`，最后用 `info` 确认已配对、已信任且已连接。本仓库不记录私人设备 MAC 地址。

## Find the current Linux input device

Run:

```bash
cat /proc/bus/input/devices | grep -A 8 "DualSense Wireless Controller"
```

Find the main controller line containing both `eventX` and `js0`. Motion-sensor and touchpad event devices are separate and should not be substituted for the main controller. Update the `GAMEPAD` path in [`tests/rover_input.py`](../tests/rover_input.py) before running any gamepad test — it is now defined in one place instead of three.

`/dev/input/eventX` is dynamically assigned after reconnects and reboots. `event11` was the main controller during the verified session, but it is not a permanent identifier.

## Do not mix `jstest` and `evdev` scales

| Tool/API | Forward/up | Center | Backward/down |
|---|---:|---:|---:|
| `jstest` Y | `-32767` | `0` | `+32767` |
| Python `evdev` `ABS_Y` | approximately `0` | approximately `128` | approximately `255` |

`ABS_X` in the verified `evdev` session followed the same `0..255` scale: left ≈ `0`, center ≈ `128`, right ≈ `255`.

两个工具读取的是同一个摇杆，但数值范围不同。`jstest` 的前推是负值；当前 Python `evdev` 的前推则接近 0。排错时必须先确认使用的是哪套 API。

## Current driving status

- DualSense input detection: verified.
- Left-side control from `ABS_Y`: verified.
- Four-wheel forward, backward, and stop from `ABS_Y`: verified at 30% PWM.
- Left/right spin turns: verified in a driving session after 2026-08-10.
- Dominant-axis rule for choosing a command: unified and verified 2026-08-16.
- Disconnect fail-safe: verified 2026-08-16 by powering the controller off mid-drive.
- Automatic controller discovery: not implemented.

The shared dead zone is 35 counts either side of `128`, so the driving range is
below `93` for forward and above `163` for backward.
Whichever axis the stick is pushed furthest along decides the command.

统一死区为中心值 `128` 两侧各 35 计数。摇杆往哪个方向推得更多，就执行哪个方向的
命令。

Always lift the wheels for the first run, confirm the current event path, keep the main power switch reachable, and use Ctrl+C only as a software stop—not as a substitute for a hardware power cutoff.
