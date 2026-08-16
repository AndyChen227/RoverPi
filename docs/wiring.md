# Wiring / 接线

## Verified control map / 已验证控制映射

The following map was physically verified on August 10, 2026. GPIO numbers are BCM numbers.

| Driver label | BCM GPIO | Raspberry Pi physical pin | Function | Status |
|---|---:|---:|---|---|
| P1 / PWM1 | 12 | 32 | Channel 1 speed, left side | Verified |
| A1 / INA1 | 23 | 16 | Channel 1 direction A | Verified |
| B1 / INB1 | 24 | 18 | Channel 1 direction B | Verified |
| P2 / PWM2 | 13 | 33 | Channel 2 speed, right side | Verified |
| A2 / INA2 | 5 | 29 | Channel 2 direction A | Verified |
| B2 / INB2 | 6 | 31 | Channel 2 direction B | Verified |
| G | Ground | 39 | Control-signal reference | Installed and used in verified tests |

### Direction truth table / 方向真值表

| Rover command | INA1 | INB1 | INA2 | INB2 | Verification |
|---|---|---|---|---|---|
| Stop | off | off | off | off | Verified |
| Forward | off | on | on | off | Verified |
| Backward | on | off | off | on | Verified |
| Spin left | on | off | on | off | Verified |
| Spin right | off | on | off | on | Verified |

Because the left and right motors face opposite directions, their rover-forward input polarities are opposite. Do not replace this table with a generic software `forward` assumption.

左右电机在底盘上的安装方向相反，因此“小车前进”所需的两侧输入极性也相反。左侧前进为 `INA1 off / INB1 on`，右侧前进为 `INA2 on / INB2 off`。不要用通用库中的函数名称替代已实测的电平组合。

## Power boundaries / 电源边界

- The 3S LiPo supplies the motor driver through the protected motor-power path.
- The Raspberry Pi 5 uses a dedicated USB power bank.
- Never bridge the positive rails or connect the 11.1 V LiPo directly to the Pi.
- The control-signal ground/reference must remain consistent with the verified wiring.
- Inspect polarity, exposed conductors, strain relief, and the accessible main switch before testing.

3S LiPo 只为电机侧供电，Raspberry Pi 5 使用独立 USB 充电宝。禁止连接两路正极母线，也禁止把 11.1 V 直接送入树莓派。每次测试前检查极性、裸露导体、线缆固定和总电源开关。

## Validation boundary / 验证边界

All five rows above have now passed low-speed physical tests at 30% PWM. Forward, backward, and stop were verified on August 10, 2026; spin left and spin right were verified in a driving session after that date.

What the turn rows confirm is the *pin combination*: with those four direction inputs, the rover spins in the stated direction. Which stick region requests a turn is a separate question, and it changed on August 16 when absolute horizontal priority was replaced by the dominant-axis rule. See [`tests/README.md`](../tests/README.md).

上表五行的引脚组合均已在 30% PWM 下实测通过。前进、后退、停止于 2026 年 8 月 10 日验证，原地左右转在其后的一次驾驶中验证。

需要区分的是：转向行已验证的是**引脚组合**——这四个方向输入确实让小车按预期原地转。至于"摇杆的哪个区域触发转向"是另一回事，8 月 16 日已从"水平轴绝对优先"改为"主导轴优先"。
