# RoverPi Roadmap / 项目路线图

Status key: `[x]` physically verified or completed; `[~]` implemented but not physically verified; `[ ]` pending.

## Dependency chains / 依赖关系

Two capabilities are frequently confused, so they are stated here explicitly:

- **"What is in front of me"** comes from the lidar. It needs no encoders.
- **"Where am I"** comes from the wheel encoders. The lidar contributes nothing to it.

A plot of the driven path therefore depends on Phase 2 and Phase 3, not on any
distance sensor. Neither chain substitutes for the other.

这两种能力经常被混淆,在此明确写出:**"我前面有什么"**来自激光,不需要编码器;
**"我在哪"**来自轮式编码器,激光对它没有任何贡献。因此轨迹图依赖第 2、3 阶段,
而不依赖任何测距传感器。两条链路不能互相替代。

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
- [x] Share one dead zone and one axis rule between the rehearsal and driving tests.
- [x] Hold both PWM channels at zero before every direction reversal.
- [x] Stop safely on controller disconnect.
- [x] Physically verify the disconnect watchdog by powering the controller off mid-drive.
- [x] Re-run every verified sequence against the refactored scripts, including turning under the dominant-axis rule.
- [x] Drive on the ground under controller command, beyond wheels-lifted testing. *(2026-08-16: about 10 continuous minutes on an indoor wood floor at 30% PWM, including a mid-drive disconnect test.)*
- [ ] Measure open-loop straight-line tracking over a fixed distance with no steering correction.
- [ ] Replace the fixed `/dev/input/eventX` path with controller discovery.
- [ ] Decide whether a stale-input timeout is safe, given that a held stick emits no events.
- [ ] Run independently after SSH disconnect and at planned startup.
- [ ] Define and verify safe startup, shutdown, and emergency-stop procedures.

### Obstacle stop / 障碍停车

The STP-23L single-point lidar enters here rather than in Phase 4 because an
obstacle stop is the same kind of behavior as the disconnect watchdog: it monitors
a condition and cuts motor output when it is met. It adds no autonomy — the
operator still drives. The autonomous behaviors stay in Phase 4.

单点激光在这里出现而不是在第 4 阶段,因为障碍停车和断线看门狗属于同一类行为:监测一个
条件,满足时切断电机输出,不增加任何自主性,驾驶的仍然是人。自主行为留在第 4 阶段。

- [ ] Read the STP-23L over USB serial and determine the baud rate empirically.
- [ ] Characterize it on the bench with no motors running: tape-measure accuracy, beam spot size at a working distance, behavior against dark and steeply angled surfaces, and what a low-confidence frame looks like in practice.
- [ ] Measure the offset between the sensor face and the front of the chassis, so a reading can be converted to bumper distance.
- [ ] Measure braking distance at 30% PWM on a wood floor, and set the stop threshold from that measurement rather than from a guess.
- [ ] Add an obstacle stop that vetoes a forward command while the operator retains control.
- [ ] Verify that a low-confidence reading and an absent reading both behave as *close*, never as *clear*.
- [ ] Verify the obstacle stop on the ground.

**Milestone exit:** the rover reliably drives forward, backward, left, and right; stops on command, on input failure, and before an obstacle directly ahead; and runs without an active SSH session. Driving in all four directions is done, on the ground and not only with the wheels lifted; the remaining work is controller independence, startup behavior, and the obstacle stop.

## Phase 2 — Encoder feedback / 编码器反馈

This phase gates the trajectory plot. Nothing downstream of it can report position.

本阶段是轨迹图的前置条件,在它之前没有任何东西能报告位置。

- [ ] Verify encoder power and voltage compatibility. **Do this before wiring anything:** Raspberry Pi 5 GPIO is not 5 V tolerant, and an encoder powered at 5 V may output 5 V logic.
- [ ] Read quadrature A/B signals from each wheel.
- [ ] Determine direction, RPM, and traveled distance.
- [ ] Compare all four wheels under the same command.

## Phase 3 — Closed-loop control / 闭环控制

- [ ] Implement per-side or per-wheel speed measurement.
- [ ] Add PID speed control.
- [ ] Improve straight-line tracking and repeatable turns.
- [ ] Begin wheel odometry.
- [ ] Log odometry to a file during a drive.
- [ ] Plot the driven trajectory offline. *(Depends on Phase 2. A trajectory plot needs position, and position comes from the encoders.)*
- [ ] Drive a closed square and use the closing error of the plot as the odometry accuracy figure.

## Phase 4 — Sensors / 传感器

- [x] Acquire a single-point lidar: LDROBOT STP-23L, with a CH9102F USB adapter. *(Purchased 2026-08-18, before a need had been measured — see [`devlog/2026-08-18-sensor-planning.md`](devlog/2026-08-18-sensor-planning.md). The rule below was skipped, not satisfied.)*
- [ ] Select any further distance sensors and an IMU based on measured needs.
- [ ] Integrate and validate one sensor at a time.
- [ ] Reactive escape: after an obstacle stop, back off, turn a fixed amount, and re-measure.
- [ ] Decide whether to mount the lidar on a servo. A fixed single beam cannot distinguish left from right; a sweep is what turns "something is ahead" into "go this way." Deferred until the fixed sensor has demonstrated where it falls short.
- [ ] Decide whether an IMU is needed, based on the heading error measured in the Phase 3 square test.

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

当前重点仍是第一阶段。四个方向的驾驶、断线安全停车和地面行驶都已实测通过，剩下的是手柄自动发现、无 SSH 独立运行、开环直线性的实际测量，以及新加入的障碍停车。编码器与自动驾驶不会在底盘可靠之前提前开始。

2026-08-18 购入单点激光测距模块。它的第一个功能（障碍停车）归入第 1 阶段，因为那是安全行为而非自主能力；真正的自主避障留在第 4 阶段。轨迹图依赖编码器，不依赖激光。

2026-08-16 的安全改动当天已在实车上全部验证，因此计入已完成项。当天的完整手柄驾驶测试是在地面上完成的（室内木地板，30% PWM，连续约 10 分钟），因此"地面行驶"也计入已完成项。
