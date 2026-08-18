# Bill of Materials / 物料清单

Everything in the first table is physically installed on the rover. Hardware that
has been acquired but not yet mounted, and hardware that is only planned, are kept
in separate sections below, so this file never implies more than the rover actually
carries.

第一张表只记录实际装在小车上的元件。已购买但尚未安装的硬件、以及仅在计划中的硬件，分别列在下方独立小节，避免让清单看起来比实车更完整。

## Installed / 已安装

| # | Component | 元件 | Specification / 规格 | Qty | Role / 用途 |
|---:|---|---|---|---:|---|
| 1 | Main computer | 主控 | Raspberry Pi 5 | 1 | Motor commands and future robotics software |
| 2 | Chassis | 底盘 | 305 × 230 mm dual-level aluminum, 4WD | 1 | Mechanical platform |
| 3 | Gear motors | 减速电机 | 12 V, 320 RPM, 30:1, integrated quadrature encoder | 4 | Four-wheel propulsion |
| 4 | Wheels | 车轮 | 65 mm high-friction | 4 | Traction and ground contact |
| 5 | Motor driver | 电机驱动板 | WHEELTEC MOS high-current dual channel | 1 | Converts PWM + direction into motor power |
| 6 | Motor battery | 电机电池 | G-Tech 3S LiPo, 11.1 V, 5200 mAh, 50C | 1 | Motor-side power source |
| 7 | Pi power | 树莓派电源 | Dedicated USB power bank | 1 | Independent Raspberry Pi supply |
| 8 | Inline fuse | 保险丝 | Series fuse on the motor-power path | 1 | Overcurrent protection |
| 9 | Main switch | 总开关 | Physical motor-power cutoff | 1 | Emergency power removal |
| 10 | Controller | 遥控器 | PS5 DualSense | 1 | Manual driving input over Bluetooth |
| 11 | Control wiring | 控制线 | Pi header to driver Channel 1 and Channel 2 | 7 | PWM, direction, and signal reference |

The encoders in item 3 are physically present but not yet wired to the Pi.
They belong to Phase 2 of the roadmap.

第 3 项电机自带的编码器已经在车上，但尚未接到树莓派，属于路线图第 2 阶段。

## Acquired, not yet installed / 已购买，尚未安装

| Component | 元件 | Specification / 规格 | Qty | Intended role / 计划用途 |
|---|---|---|---:|---|
| Single-point lidar | 单点激光测距模块 | LDROBOT STP-23L, 0.07–7.5 m, 120 Hz, UART | 1 | Obstacle stop, then reactive escape |
| USB serial adapter | USB 转串口模块 | CH9102F, with Type-C cable and 20 cm harness | 1 | Reads the lidar over USB, bypassing GPIO logic levels |

Acquired 2026-08-18. Not yet mounted, not yet wired, not yet read. Intended
position is the front center of the upper deck, level and pointing forward. See
[`docs/devlog/2026-08-18-sensor-planning.md`](../docs/devlog/2026-08-18-sensor-planning.md)
for what it can and cannot do, and why the first feature is an obstacle stop
rather than obstacle avoidance.

2026-08-18 购入。尚未安装、尚未接线、尚未读取数据。计划安装位置为上层平台车头正中，水平朝前。它能做什么、不能做什么，以及为什么第一个功能是障碍停车而不是自动避障，见上述开发日志。

## Power domains / 供电区域

| Domain | Source | Note |
|---|---|---|
| Motors and driver | 3S LiPo 11.1 V, through fuse and main switch | Never connect to the Pi |
| Raspberry Pi 5 | Dedicated USB power bank | Separate positive rail |

> [!CAUTION]
> The two positive rails must never be bridged. See [`docs/wiring.md`](../docs/wiring.md)
> for the verified control map and the signal-reference arrangement.
>
> 两路正极禁止连接。已验证的控制映射和信号参考地见 [`docs/wiring.md`](../docs/wiring.md)。

## Planned, not yet purchased / 计划中，尚未购买

| Component | 元件 | Phase | Note |
|---|---|---|---|
| Servo for lidar sweep | 激光扫描舵机 | Phase 4 | Deliberately deferred until the fixed sensor shows where it falls short |
| IMU | 惯性测量单元 | Phase 4 | Decide from the heading error measured in the Phase 3 square test |
| Raspberry Pi camera | 树莓派摄像头 | Phase 5 | — |
