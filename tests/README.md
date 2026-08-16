# RoverPi Hardware Tests

These files are focused hardware-validation scripts, not an automated unit-test
suite. Run them manually on the Raspberry Pi, one at a time.

## Safety before every run

1. Read [`docs/wiring.md`](../docs/wiring.md) and confirm the BCM map.
2. Inspect the LiPo, fuse, switch, wiring polarity, insulation, and strain relief.
3. Lift all four wheels clear of people, cables, and the floor.
4. Keep the physical power switch reachable.
5. Use the documented 30% PWM; do not increase speed during validation.
6. For gamepad tests, discover the current main-controller `eventX` and update
   `GAMEPAD` in [`rover_input.py`](rover_input.py) first.
7. Treat Ctrl+C and the `finally` cleanup as software protection, not a
   replacement for physical power removal.

## Shared modules

The pin numbers, polarities, and controller thresholds used to be copied into
every test file. They now live in two modules that the tests import, so a
wiring change or a threshold change is made once.

| File | Contents |
|---|---|
| `rover_pins.py` | Verified BCM pin map, verified direction polarities, 30% test speed, and the movement commands |
| `rover_input.py` | DualSense device path, the observed `0..255` calibration, the shared dead zone, and the reading loop |

Both are plain modules in `tests/`, not a `src/` package. Runtime code moves
into `src/` only after turning, controller discovery, and fail-safe behavior
are stable enough to deserve a reusable control layer.

## Recommended order and status

| Order | File | Purpose | Physical status |
|---:|---|---|---|
| 1 | `test_gamepad_input.py` | Print directions without moving motors | Verified 2026-08-10; re-run after the 2026-08-16 changes |
| 2 | `test_motor_channel1.py` | Left side forward for one second | Verified 2026-08-10 |
| 3 | `test_gamepad_motor_left.py` | DualSense controls left forward/backward/stop | Verified 2026-08-10; dead zone changed 2026-08-16 |
| 4 | `test_motor_channel2.py` | Right side forward for one second | Verified 2026-08-10 |
| 5 | `test_motor_channel2_backward.py` | Right side backward for one second | Verified 2026-08-10 |
| 6 | `test_all_motors.py` | Four-wheel forward/stop/backward/stop | Verified 2026-08-10 |
| 7 | `test_gamepad_all_motors.py` | Full left-stick driving test | Forward/backward/stop verified 2026-08-10; turns unverified; dead zone, axis priority, and disconnect watchdog changed 2026-08-16 |

Run a test from the repository root, for example:

```bash
python3 tests/test_all_motors.py
```

## Changes made on 2026-08-16 (not yet physically re-run)

These changes were made for safety and consistency. The movement sequences,
verified pin states, and the 30% test speed are unchanged, but the scripts in
their current form have not been executed on the rover.

1. **One dead zone instead of two.** The read-only rehearsal test used 35
   counts while the test that actually drove four wheels used 20. The narrower
   value was on the more dangerous script. Both now use 35.
2. **One axis priority instead of two.** The rehearsal test gave the vertical
   axis priority; the driving test gave the horizontal axis priority. A
   slightly angled forward push therefore printed `FORWARD` in rehearsal but
   would have spun the rover in place. Vertical now has priority everywhere.
3. **Protected direction reversal.** Reversing used to flip a direction pin
   while the motors were still turning. Both PWM channels are now held at zero
   for 50 ms before any direction change.
4. **Disconnect watchdog.** `read_loop()` blocked forever, so a dropped
   Bluetooth link left the last PWM command applied and the rover kept driving.
   The loop now polls with a timeout, checks that the controller device node
   still exists, and stops both channels when the controller is gone.
5. **No redundant GPIO writes.** An unchanged command no longer rewrites pins
   on every controller event.

Item 4 protects against a real disconnect. It deliberately does **not** stop
the rover merely because the controller has been quiet, because a DualSense
sends no events while the stick is held perfectly still. A stale-input timeout
would need its own physical test to confirm it does not interrupt normal
driving.

## Important boundaries

- Every Python file keeps detailed teaching comments alongside the verified pin
  states, 30% PWM, timing, thresholds, and movement priority.
- The turn functions in `rover_pins.py` are deliberately labeled unverified.
- The fixed `/dev/input/event11` value documents the verified session but must
  be changed when Linux assigns a different number. Automatic controller
  discovery is still not implemented.
- These tests do not yet implement production startup behavior or standalone
  operation without an SSH session.

这些脚本用于手动硬件验证，不是自动单元测试。运行前必须架空轮子并确认当前手柄
`eventX`。前进、后退和停止已实测；左右转仅完成代码实现，尚未实测。

2026-08-16 的改动统一了死区（35）与轴优先级（垂直优先）、为换向加入 50 毫秒断电
保护、并加入手柄断线自动停车。这些改动本身尚未在实车上重新运行，属于"已实现、
等待实体测试"。
