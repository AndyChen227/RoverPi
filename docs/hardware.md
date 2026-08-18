# Hardware / 硬件

## Current physical layout / 当前物理布局

RoverPi uses a two-level aluminum 4WD chassis.

- **Lower deck:** four 12 V encoder gear motors and wheels, 3S LiPo motor battery, inline fuse, main switch, and dual-channel motor driver.
- **Upper deck:** Raspberry Pi 5 and its dedicated USB power bank.
- **Between decks:** verified PWM/direction wiring between the Pi and both driver channels.

RoverPi 使用双层铝合金四驱底盘。下层放置四个电机、电机电池、保险丝、总开关和双路驱动板；上层放置 Raspberry Pi 5 与独立 USB 充电宝；上下层之间连接两路已验证的控制信号线。

## Power domains / 供电区域

| Domain | Source | Verified state |
|---|---|---|
| Motors and motor driver | 3S LiPo, 11.1 V, through protected motor-power path | Both channels powered and moved under Pi control |
| Raspberry Pi 5 | Dedicated USB power bank | Powered independently during tests |

> [!CAUTION]
> Never connect the 3S LiPo directly to the Raspberry Pi. Keep the two positive power domains separate and retain the verified signal-ground arrangement. Stop immediately if wiring heats, insulation moves, or motor behavior differs from the documented direction table.

## Verified physical behavior — August 10, 2026

- Channel 1 drove both left-side motors forward, backward, and stop.
- Channel 2 drove both right-side motors forward, backward, and stop.
- All four wheels completed a forward → stop → backward → stop sequence.
- The four-wheel tests used 30% PWM and short controlled intervals.
- The DualSense controlled four-wheel forward, backward, and stop.
- Left/right spin turns were verified in a later driving session: the rover spins in the commanded direction under gamepad control.

## Verified physical behavior — August 16, 2026 (ground drive)

- The full gamepad driving test ran on an indoor wood floor at 30% PWM for about ten continuous minutes.
- Forward, backward, stop, and both spin turns behaved on the ground as they had with the wheels lifted.
- The rover rotates in place cleanly under floor friction, without the binding a four-wheel skid-steer platform can show.
- The disconnect fail-safe was triggered mid-drive on the ground: all four wheels stopped immediately.
- No drift was noticed on straight runs, but the operator was steering throughout, so open-loop straight-line tracking remains unmeasured.

以上前进、后退和停止为 8 月 10 日实测结果；原地左右转在其后的一次驾驶中实测通过。
8 月 16 日的完整手柄驾驶测试在室内木地板上以 30% PWM 连续行驶约 10 分钟，地面表现与架空一致，
地面摩擦下能干脆原地旋转，断线安全停车也在地面行驶中验证通过。直线未见跑偏，但全程有人打方向，
开环直线性仍未测量。

## Safety checklist

1. Inspect LiPo condition, fuse, switch, polarity, insulation, and cable strain relief.
2. Lift all wheels before a new or changed motor test. Ground driving is only for sequences already verified in the air.
3. Confirm the BCM pin map and current DualSense event path.
4. Start stopped and keep the documented three-second warning delay.
5. Use 30% PWM until the next stage is separately validated.
6. Keep a physical power cutoff within reach.
