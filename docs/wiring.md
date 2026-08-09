# Wiring / 接线

[English](#english) · [中文](#中文)

---

<a id="english"></a>

## English

### Current wiring state

| Connection | State | Validation |
|---|---|---|
| 3S LiPo → inline fuse → motor driver | Physically installed | Power-on validation pending |
| Motor driver outputs → four motors | Connected | Direction and movement validation pending |
| Dedicated USB power bank → Raspberry Pi 5 | Installed as the Pi power source | System power-on validation pending |
| Raspberry Pi 5 → motor driver control interface | Ribbon/jumper control wiring installed | GPIO mapping, signal behavior, and motor response pending |

No exact GPIO pin map is recorded here yet because the pin assignments and driver-interface details have not been verified in the documented build.

### Power and signal boundaries

- The 3S LiPo battery powers the motor side.
- The dedicated USB power bank powers the Raspberry Pi 5.
- Do not bridge positive power rails.
- Before powering the system, confirm from the motor-driver documentation whether and how the control interface requires a shared signal ground/reference.
- Check every control wire against the final GPIO map before running software.

> [!WARNING]
> “Connected” in this document means the physical wiring was installed. It does not claim that the rover has been powered on, that the GPIO mapping is correct, or that any motor has moved.

### Next verification steps

1. Record the exact Raspberry Pi GPIO-to-driver pin map.
2. Confirm driver logic-voltage compatibility and ground/reference requirements.
3. Inspect polarity, strain relief, and exposed conductors.
4. Lift the wheels clear of the ground.
5. Test one motor channel at a time and verify stop behavior first.

---

<a id="中文"></a>

## 中文

### 当前接线状态

| 连接 | 状态 | 验证情况 |
|---|---|---|
| 3S LiPo → 串联保险丝 → 电机驱动板 | 已完成物理安装 | 等待通电验证 |
| 电机驱动板输出 → 四个电机 | 已连接 | 等待方向与移动验证 |
| 独立 USB 充电宝 → Raspberry Pi 5 | 已作为树莓派电源安装 | 等待系统通电验证 |
| Raspberry Pi 5 → 电机驱动板控制接口 | 已安装排线/杜邦控制线 | 等待 GPIO 映射、信号与电机响应验证 |

目前不在此处记录具体 GPIO 引脚表，因为文档中尚未确认最终引脚分配与驱动板接口细节。

### 电源与信号边界

- 3S LiPo 电池为电机侧供电。
- 独立 USB 充电宝为 Raspberry Pi 5 供电。
- 不要连接两个电源的正极母线。
- 通电前，根据驱动板资料确认控制接口是否需要以及如何连接信号地/参考地。
- 运行软件前，对照最终 GPIO 引脚表逐根检查控制线。

> [!WARNING]
> 本文中的“已连接”只表示物理接线已经安装，并不表示小车已经通电、GPIO 映射正确或电机已经转动。

### 下一步验证

1. 记录 Raspberry Pi GPIO 与驱动板之间的准确引脚映射。
2. 确认驱动板逻辑电平兼容性及地线/参考地要求。
3. 检查正负极、线缆应力释放和裸露导体。
4. 将车轮架空。
5. 先验证停止行为，再逐个测试电机通道。
