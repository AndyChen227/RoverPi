# RoverPi Roadmap / 项目路线图

Status key: `[x]` physically verified or completed; `[~]` implemented but not physically verified; `[ ]` pending.

## Phase 0 — Mechanical assembly / 机械组装

- [x] Assemble the four-wheel chassis.
- [x] Install four motors, wheels, and upper deck.
- [x] Mount the Raspberry Pi, motor driver, battery, and protected power path.

## Phase 1 — Basic movement and safety / 基础移动与安全

- [x] Verify Channel 1 forward, backward, and stop.
- [x] Verify Channel 2 forward, backward, and stop.
- [x] Verify four-wheel forward, backward, and stop at 30% PWM.
- [x] Read DualSense input through Linux and Python `evdev`.
- [x] Verify DualSense-controlled forward, backward, and stop.
- [x] Implement differential spin-left and spin-right functions.
- [x] Physically verify left and right turns.
- [~] Share one dead zone and one axis priority between the rehearsal and driving tests.
- [~] Hold both PWM channels at zero before every direction reversal.
- [~] Stop safely on controller disconnect.
- [ ] Physically verify the disconnect watchdog by powering the controller off mid-drive.
- [ ] Re-run every verified sequence against the refactored scripts, including turning under the new vertical-priority mapping.
- [ ] Replace the fixed `/dev/input/eventX` path with controller discovery.
- [ ] Decide whether a stale-input timeout is safe, given that a held stick emits no events.
- [ ] Run independently after SSH disconnect and at planned startup.
- [ ] Define and verify safe startup, shutdown, and emergency-stop procedures.

**Milestone exit:** the rover reliably drives forward, backward, left, and right; stops on command and on input failure; and runs without an active SSH session. Driving in all four directions is done; the remaining work is failure behavior and independence.

## Phase 2 — Encoder feedback / 编码器反馈

- [ ] Verify encoder power and voltage compatibility.
- [ ] Read quadrature A/B signals from each wheel.
- [ ] Determine direction, RPM, and traveled distance.
- [ ] Compare all four wheels under the same command.

## Phase 3 — Closed-loop control / 闭环控制

- [ ] Implement per-side or per-wheel speed measurement.
- [ ] Add PID speed control.
- [ ] Improve straight-line tracking and repeatable turns.
- [ ] Begin wheel odometry.

## Phase 4 — Sensors / 传感器

- [ ] Select distance sensors and an IMU based on measured needs.
- [ ] Integrate and validate one sensor at a time.

## Phase 5 — Computer vision / 计算机视觉

- [ ] Integrate a Raspberry Pi camera.
- [ ] Add OpenCV perception experiments after the base is dependable.

## Phase 6 — ROS 2

- [ ] Separate motors, encoders, sensors, and vision into maintainable nodes.
- [ ] Publish commands, wheel state, and sensor data.

## Phase 7 — Autonomous navigation / 自主导航

- [ ] Localization and sensor fusion.
- [ ] Mapping/SLAM.
- [ ] Path planning and obstacle avoidance.
- [ ] Controlled autonomous navigation experiments.

当前重点仍是第一阶段：四个方向的驾驶已经全部实测通过，剩下的是失效行为与独立运行——先实测断线看门狗，再完成手柄自动发现和无 SSH 运行。编码器与自动驾驶不会在底盘可靠之前提前开始。

2026-08-16 新增的三项 `[~]` 是代码层面的安全改动，尚未在实车上运行，因此不能计入已完成项。
