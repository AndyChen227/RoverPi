# RoverPi

A Raspberry Pi 5-powered four-wheel robotic rover, built and documented in small, verifiable stages.

基于 Raspberry Pi 5 的四轮机器人小车，以小步验证的方式持续开发和记录。

> RoverPi is an active learning project. Completed tests and future plans are kept explicitly separate.
>
> RoverPi 是一个持续开发中的学习项目；文档会明确区分已实测成果与未来计划。

## Current milestone / 当前里程碑

As of **August 10, 2026**:

| Area | Status | Evidence |
|---|---:|---|
| Mechanical chassis | Complete | Four-wheel, two-level aluminum chassis assembled |
| Motor driver Channel 1 | Verified | Left-side forward, backward, and stop at 30% PWM |
| Motor driver Channel 2 | Verified | Right-side forward, backward, and stop at 30% PWM |
| Four-wheel movement | Verified | Forward, backward, and stop sequence |
| DualSense driving | Partly verified | Forward, backward, and stop controlled from the left stick |
| Differential turning | Code only | Left/right spin-turn logic implemented; physical test pending |
| Robust controller discovery | Pending | Test scripts still require the current `/dev/input/eventX` path |
| Standalone operation and fail-safe | Pending | No-SSH startup and controller-disconnect safety still required |

Phase 1 remains **in progress** until turning, controller discovery, standalone operation, and fail-safe behavior are physically verified.

截至 **2026 年 8 月 10 日**，两路电机驱动、四轮前进/后退/停止以及 DualSense 控制前进/后退/停止均已完成实测。左转与右转的原地差速逻辑已经写入代码，但尚未进行实车验证，因此第一阶段仍未完成。

## Verified GPIO map / 已验证 GPIO

All GPIO values use BCM numbering.

| Side | Driver channel | PWM | A | B | Rover-forward polarity |
|---|---|---:|---:|---:|---|
| Left | Channel 1 | GPIO12 | GPIO23 | GPIO24 | `INA1 off`, `INB1 on` |
| Right | Channel 2 | GPIO13 | GPIO5 | GPIO6 | `INA2 on`, `INB2 off` |

The opposite polarity produces rover-backward motion. See [wiring documentation](docs/wiring.md) before changing any pin or direction logic.

## DualSense input / 手柄输入

- Python `evdev` observed `ABS_X`/`ABS_Y` at approximately `0..255`, center `128`.
- `evdev ABS_Y`: forward/up ≈ `0`, center ≈ `128`, backward/down ≈ `255`.
- `jstest` Y axis: forward push `-32767`, center `0`, backward pull `+32767`.
- `/dev/input/eventX` is dynamic. `event11` was valid for one session, not a permanent device path.

See [setup notes](docs/setup.md) and the [DualSense debugging note](notes/debugging/dualsense-input.md).

## Safety / 安全

> [!CAUTION]
> Never connect the 11.1 V 3S LiPo directly to the Raspberry Pi. The motor side uses the LiPo through the protected motor-power path; the Pi uses a separate USB power bank. Lift all wheels before running a test, keep the main power switch accessible, and begin at the documented 30% PWM.

绝对不要把 11.1 V 3S LiPo 直接连接到 Raspberry Pi。运行测试前先架空四轮，确保总电源开关可以立即操作，并保持已验证的 30% PWM 低速测试设置。

## Repository guide / 仓库导航

- [`tests/`](tests/) — focused hardware checks; start with [tests/README.md](tests/README.md)
- [`docs/devlog/`](docs/devlog/) — build history and verified milestones
- [`docs/wiring.md`](docs/wiring.md) — pin map, physical pins, and motor polarity
- [`docs/setup.md`](docs/setup.md) — Raspberry Pi and DualSense setup notes
- [`docs/hardware.md`](docs/hardware.md) — physical layout and power domains
- [`docs/roadmap.md`](docs/roadmap.md) — detailed phase checklist
- [`notes/debugging/`](notes/debugging/) — causes, fixes, and reusable lessons

## Latest development log / 最新开发日志

The August 10 session verified both motor channels, four-wheel forward/backward/stop, and DualSense-controlled forward/backward/stop. It also preserved differential turning logic as explicitly unverified code.

8 月 10 日完成了双通道、四轮前后移动、停止以及 DualSense 控制的实测，并把尚未实测的差速转向逻辑单独标明。

Read the [full bilingual development log](docs/devlog/2026-08-10.md).

## Roadmap summary / 路线图概览

1. Basic movement and safety — in progress
2. Encoder feedback
3. Closed-loop wheel-speed control
4. Sensors
5. Computer vision
6. ROS 2 integration
7. Localization and autonomous navigation

The next practical step is a wheels-lifted physical validation of left/right turning, followed by dynamic controller discovery and a controller-disconnect fail-safe.
