# Bill of Materials / 物料清单

Everything listed here is physically installed on the rover. Items that are
planned but not yet purchased or mounted are kept in a separate section so this
file never implies hardware that does not exist.

本清单只记录实际装在小车上的元件。计划购买但尚未安装的部分单独列出，避免让清单看起来比实车更完整。

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

| Component | 元件 | Phase |
|---|---|---|
| Distance sensors | 测距传感器 | Phase 4 |
| IMU | 惯性测量单元 | Phase 4 |
| Raspberry Pi camera | 树莓派摄像头 | Phase 5 |
