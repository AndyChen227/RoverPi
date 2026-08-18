# DualSense directional input validation — 2026-08-09

[English](#english) · [中文](#中文)

---

<a id="english"></a>

## English

PS5 DualSense directional input parsing was successfully validated through
`evdev` for all five states: `FORWARD`, `BACKWARD`, `LEFT`, `RIGHT`, and `STOP`.

The test tracks `ABS_X` and `ABS_Y`, using `CENTER = 128` and `DEAD_ZONE = 35`.
The verified left-stick values were approximately:

- X: left `0`, center `128`, right `255`
- Y: up `0`, center `128`, down `255`

During this session, the main controller was available at
`/dev/input/event11`. Linux event numbers can change after a reconnect or
reboot, so this path must not be treated as permanent.

This validates directional input parsing only. The gamepad does not control
the rover motors yet.

---

<a id="中文"></a>

## 中文

已通过 `evdev` 成功验证 PS5 DualSense 手柄的方向输入解析，五种状态
`FORWARD`、`BACKWARD`、`LEFT`、`RIGHT` 和 `STOP` 均已测试正确。

测试程序持续记录 `ABS_X` 和 `ABS_Y`，并使用 `CENTER = 128` 与
`DEAD_ZONE = 35`。左摇杆的实测值约为：

- X：左 `0`、中间 `128`、右 `255`
- Y：上 `0`、中间 `128`、下 `255`

本次会话中主控制器路径为 `/dev/input/event11`。Linux 的 event 编号在
重新连接或重启后可能变化，因此不能把这个路径视为永久固定值。

本次只验证了方向输入解析；手柄尚未控制小车电机。
