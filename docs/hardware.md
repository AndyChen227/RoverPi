# Hardware / 硬件

[English](#english) · [中文](#中文)

---

<a id="english"></a>

## English

### Current physical layout

RoverPi now uses a two-level aluminum chassis.

- **Lower deck:** four motors and wheels, 3S LiPo motor battery, inline fuse, and dual-channel motor driver.
- **Upper deck:** Raspberry Pi 5 and a dedicated USB power bank for the Pi.
- **Between decks:** Raspberry Pi-to-motor-driver control ribbon/jumper wiring has been installed.

The separate upper deck creates a clearer physical boundary between the computing hardware and the motor-power hardware and provides space for cable routing.

### Power domains

| Domain | Source | Installed state |
|---|---|---|
| Motors and motor driver | 3S LiPo battery through the inline fuse | Physically installed |
| Raspberry Pi 5 | Dedicated USB power bank | Mounted on the upper deck |

> [!IMPORTANT]
> Installation does not mean functional validation. This configuration has not yet been documented as successfully powered on or moving.

> [!CAUTION]
> Do not connect the 11.1 V LiPo directly to the Raspberry Pi. Before powered testing, verify polarity, cable security, the driver control-interface voltage levels, and its ground/reference requirements.

### Completed on August 7–8, 2026

- Converted the chassis from one level to two levels.
- Mounted the Raspberry Pi 5 on the upper deck.
- Mounted a dedicated USB power bank for the Pi on the upper deck.
- Installed the control wiring between the Raspberry Pi and motor driver.

See the [combined development log](devlog/2026-08-07-08.md).

---

<a id="中文"></a>

## 中文

### 当前物理布局

RoverPi 目前采用双层铝合金底盘。

- **下层平台：** 四个电机与轮胎、3S LiPo 电机电池、串联保险丝和双路电机驱动板。
- **上层平台：** Raspberry Pi 5 和为树莓派单独供电的 USB 充电宝。
- **上下层之间：** 已安装 Raspberry Pi 至电机驱动板的排线/杜邦控制线。

上层平台把计算硬件与电机动力硬件在物理上分开，也为线路整理留出了空间。

### 供电区域

| 区域 | 电源 | 安装状态 |
|---|---|---|
| 电机与电机驱动板 | 3S LiPo 电池，经串联保险丝 | 已完成物理安装 |
| Raspberry Pi 5 | 独立 USB 充电宝 | 已固定在上层平台 |

> [!IMPORTANT]
> 完成安装不等于完成功能验证。目前尚未记录为已经成功通电或移动。

> [!CAUTION]
> 不得把 11.1 V LiPo 电池直接连接到 Raspberry Pi。通电测试前，应检查正负极、线缆固定、驱动板控制接口电平，以及其地线/参考地要求。

### 2026 年 8 月 7–8 日完成内容

- 将底盘从单层升级为双层。
- 将 Raspberry Pi 5 安装到上层平台。
- 将树莓派独立 USB 充电宝安装到上层平台。
- 安装 Raspberry Pi 与电机驱动板之间的控制线。

详见[合并开发日志](devlog/2026-08-07-08.md)。
