# Setup Notes / 设置说明

[English](#english) · [中文](#中文)

---

<a id="english"></a>

## English

### DualSense validation environment

The PS5 DualSense Wireless Controller was paired, trusted, and connected through Bluetooth. The `python3-evdev` and joystick packages were installed/used for validation.

During the verified session Linux reported:

| Interface | Device |
|---|---|
| Main controller | `js0`, `/dev/input/event11` |
| Motion sensors | `js1`, `/dev/input/event12` |
| Touchpad | `/dev/input/event13` |

The left stick reported Axis 0 as horizontal and Axis 1 as vertical. On Axis 1, `+32767` was a forward push and `-32767` was a backward pull.

Run `python3 tests/test_gamepad_input.py` to print the device currently configured in the test. Event numbers are assigned dynamically and can change after reconnecting or rebooting, so update the path or add device discovery when needed.

This confirms input access only; gamepad-controlled rover driving is not implemented yet.

---

<a id="中文"></a>

## 中文

### DualSense 验证环境

PS5 DualSense 无线手柄已通过蓝牙完成配对、信任和连接。验证过程中安装并使用了 `python3-evdev` 与 joystick 软件包。

在已验证的会话中，Linux 显示：

| 接口 | 设备 |
|---|---|
| 主控制器 | `js0`、`/dev/input/event11` |
| 运动传感器 | `js1`、`/dev/input/event12` |
| 触摸板 | `/dev/input/event13` |

左摇杆 Axis 0 为水平方向，Axis 1 为垂直方向。Axis 1 的 `+32767` 表示向前推，`-32767` 表示向后拉。

运行 `python3 tests/test_gamepad_input.py` 可打印测试文件当前指定的设备。event 编号由系统动态分配，重新连接或重启后可能变化，因此需要按实际情况更新路径，后续也应加入设备自动发现。

目前只验证了输入读取；尚未实现手柄控制小车行驶。
