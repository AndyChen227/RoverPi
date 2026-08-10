# RoverPi Hardware Tests

These files are focused hardware-validation scripts, not an automated unit-test suite. Run them manually on the Raspberry Pi, one at a time.

## Safety before every run

1. Read [`docs/wiring.md`](../docs/wiring.md) and confirm the BCM map.
2. Inspect the LiPo, fuse, switch, wiring polarity, insulation, and strain relief.
3. Lift all four wheels clear of people, cables, and the floor.
4. Keep the physical power switch reachable.
5. Use the documented 30% PWM; do not increase speed during validation.
6. For gamepad tests, discover the current main-controller `eventX` and update `GAMEPAD` first.
7. Treat Ctrl+C and the `finally` cleanup as software protection, not a replacement for physical power removal.

## Recommended order and status

| Order | File | Purpose | Physical status |
|---:|---|---|---|
| 1 | `test_gamepad_input.py` | Print directions without moving motors | Verified |
| 2 | `test_motor_channel1.py` | Left side forward for one second | Verified |
| 3 | `test_gamepad_motor_left.py` | DualSense controls left forward/backward/stop | Verified |
| 4 | `test_motor_channel2.py` | Right side forward for one second | Verified |
| 5 | `test_motor_channel2_backward.py` | Right side backward for one second | Verified |
| 6 | `test_all_motors.py` | Four-wheel forward/stop/backward/stop | Verified |
| 7 | `test_gamepad_all_motors.py` | Full left-stick driving test | Forward/backward/stop verified; turns unverified |

Run a test from the repository root, for example:

```bash
python3 tests/test_all_motors.py
```

## Important boundaries

- Every Python file contains detailed teaching comments while retaining the verified pin states, 30% PWM, timing, thresholds, and movement priority.
- The left/right functions in `test_gamepad_all_motors.py` are deliberately labeled unverified.
- The fixed `/dev/input/event11` value documents the verified session but must be changed when Linux assigns a different number.
- These tests do not yet implement automatic controller discovery, controller-disconnect fail-safe, or production startup behavior.

这些脚本用于手动硬件验证，不是自动单元测试。运行前必须架空轮子并确认当前手柄 `eventX`。前进、后退和停止已实测；左右转仅完成代码实现，尚未实测。
