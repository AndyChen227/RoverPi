# Wiring / 接线

[English](#english) · [中文](#中文)

---

<a id="english"></a>

## English

### Current wiring state

| Connection | State | Validation |
|---|---|---|
| 3S LiPo → inline fuse → motor driver | Physically installed | Power-on validation pending |
| Motor driver Channel 1 → two left-side motors | Connected | Both left-side motors moved at 30% PWM and stopped after about 1 second |
| Motor driver Channel 2 → two right-side motors | Connected | Movement validation pending |
| Dedicated USB power bank → Raspberry Pi 5 | Installed as the Pi power source | System power-on validation pending |
| Raspberry Pi 5 → motor driver Channel 1 | BCM GPIO12 = PWM1, GPIO23 = INA1, GPIO24 = INB1 | Channel 1 response and stop behavior verified |

The Channel 1 map above is verified for the current build. Channel 1 controls the two left-side motors. Their observed direction appeared forward, but that direction is provisional until full-rover validation confirms orientation and polarity.

### Power and signal boundaries

- The 3S LiPo battery powers the motor side.
- The dedicated USB power bank powers the Raspberry Pi 5.
- Do not bridge positive power rails.
- Before powering the system, confirm from the motor-driver documentation whether and how the control interface requires a shared signal ground/reference.
- Check every control wire against the final GPIO map before running software.

> [!WARNING]
> Only Channel 1 and the two left-side motors have passed a powered movement test. This does not claim right-side motor control or full-rover forward, backward, or turning behavior.

### Next verification steps

1. Record and verify the Channel 2 GPIO-to-driver pin map.
2. Confirm driver logic-voltage compatibility and ground/reference requirements.
3. Inspect polarity, strain relief, and exposed conductors.
4. Lift the wheels clear of the ground.
5. Test Channel 2 and then validate full-rover directions and stopping.

---

<a id="中文"></a>

## 中文

### 当前接线状态

| 连接 | 状态 | 验证情况 |
|---|---|---|
| 3S LiPo → 串联保险丝 → 电机驱动板 | 已完成物理安装 | 等待通电验证 |
| 电机驱动板 Channel 1 → 左侧两个电机 | 已连接 | 两个左侧电机已在 30% PWM 下转动，并在约 1 秒后停止 |
| 电机驱动板 Channel 2 → 右侧两个电机 | 已连接 | 等待移动验证 |
| 独立 USB 充电宝 → Raspberry Pi 5 | 已作为树莓派电源安装 | 等待系统通电验证 |
| Raspberry Pi 5 → 电机驱动板 Channel 1 | BCM GPIO12 = PWM1，GPIO23 = INA1，GPIO24 = INB1 | 已验证 Channel 1 响应和停止行为 |

上表中的 Channel 1 引脚映射已在当前硬件上验证。Channel 1 控制左侧两个电机。观察到的转动方向看起来是前进，但在整车方向和极性验证完成之前，这一判断仍为暂定、未完全验证。

### 电源与信号边界

- 3S LiPo 电池为电机侧供电。
- 独立 USB 充电宝为 Raspberry Pi 5 供电。
- 不要连接两个电源的正极母线。
- 通电前，根据驱动板资料确认控制接口是否需要以及如何连接信号地/参考地。
- 运行软件前，对照最终 GPIO 引脚表逐根检查控制线。

> [!WARNING]
> 目前只有 Channel 1 和左侧两个电机完成了通电移动测试。这不代表右侧电机控制或整车前进、后退、转向已经完成。

### 下一步验证

1. 记录并验证 Channel 2 的准确 GPIO 引脚映射。
2. 确认驱动板逻辑电平兼容性及地线/参考地要求。
3. 检查正负极、线缆应力释放和裸露导体。
4. 将车轮架空。
5. 测试 Channel 2，然后验证整车方向和停止行为。
