# DualSense input: `jstest`, `evdev`, and dynamic `eventX`

## Symptoms

- A script that previously used `/dev/input/event11` could no longer open the controller after reconnecting.
- A joystick direction appeared reversed when values observed in `jstest` were interpreted as though they came from Python `evdev`.

## Root causes

### 1. Linux event numbers are dynamic

`/dev/input/event11` described one session, not the controller's permanent identity. Reconnecting or rebooting can assign a different `eventX`. A DualSense also exposes separate main-controller, motion-sensor, and touchpad interfaces.

Inspect the current devices:

```bash
cat /proc/bus/input/devices | grep -A 8 "DualSense Wireless Controller"
```

Use the handler line for the main controller, normally the one containing both `js0` and `eventX`. Do not select the motion-sensor or touchpad event device.

### 2. `jstest` and `evdev` use different observed scales

| Reader | Up/forward | Center | Down/backward |
|---|---:|---:|---:|
| `jstest` Y | `-32767` | `0` | `+32767` |
| Python `evdev ABS_Y` | ≈ `0` | ≈ `128` | ≈ `255` |

The verified `evdev ABS_X` scale was left ≈ `0`, center ≈ `128`, right ≈ `255`.

Both observations can be correct: they come through different Linux interfaces and representations. Copying thresholds or sign assumptions from one tool into code that reads the other produces incorrect behavior.

## Current safe interpretation

The Python tests read `evdev`, so they use center `128` and a dead zone. A low `ABS_Y` value commands forward, a high value commands backward, and the center range commands stop.

## Differential-drive note

- Forward: both sides move rover-forward.
- Backward: both sides move rover-backward.
- Spin left: left side backward, right side forward.
- Spin right: left side forward, right side backward.
- A later analog mixing controller can make one side slower than the other for smoother turns.

Only forward, backward, and stop are physically verified. The current spin-turn combinations are derived from verified side polarities but remain unverified as complete rover movements.

## Future fix

Replace the fixed event path with device discovery based on the main controller's identity and capabilities. Add an input timeout or disconnect handler that stops both PWM channels immediately when controller events cease.

## 中文总结

`event11` 只是某一次连接的动态编号，不是永久路径；每次重连或重启后都需要重新检查。`jstest` 与 Python `evdev` 的数值范围不同，不能混用阈值。当前 Python 代码使用 `evdev` 的约 `0..255` 范围与中心值 `128`。未来应加入设备自动发现与断线安全停止。
