# August 16, 2026 — Safety consistency and shared modules

## 2026 年 8 月 16 日——安全一致性与共享模块

No hardware changed in this session. This was a code review of everything
written between August 6 and August 10, plus the fixes that review produced.
Nothing was physically re-tested, so every change below is recorded as
implemented but unverified.

本次没有改动任何硬件，只做了 8 月 6 日到 8 月 10 日全部代码的复查与修复。所有改动
都没有在实车上重新运行，因此一律记为"已实现、未验证"。

---

## English

### What the review found

**1. The rehearsal test did not predict the rover's behavior.**

`test_gamepad_input.py` prints movement words without touching a motor pin. It
is the safe way to learn the stick before driving. But it used a 35-count dead
zone and gave the vertical axis priority, while `test_gamepad_all_motors.py`
used a 20-count dead zone and gave the *horizontal* axis priority.

Two consequences followed. A slightly angled forward push printed `FORWARD`
during rehearsal but would have made the rover spin in place. And the narrower
dead zone was on the script that actually moved four wheels, which is exactly
the wrong way round: if 35 counts was the value needed to keep a released stick
quiet, then 20 counts meant a released stick could still command movement.

**2. Direction reversals flipped a pin under load.**

`forward()` followed immediately by `backward()` changed the direction inputs
while the motors were still turning. At 30% PWM the driver survives this, but
it puts an avoidable current spike through the MOSFETs and the LiPo.

**3. A dropped controller left the rover driving.**

`gamepad.read_loop()` blocks. When a Bluetooth link drops, no exception is
raised and no further events arrive — the loop simply waits forever while the
last PWM value and the last direction pins stay applied. The rover would have
kept moving at 30% until someone reached the physical switch.

**4. Six pin objects were defined seven times.**

Every test file repeated `PWM1 = PWMOutputDevice(12)` and its own copy of
`stop()`, `forward()`, and `backward()`. Changing one wire meant editing seven
files, on the part of the project where a mistake moves a physical machine.

**5. Every controller event rewrote pins that were already correct.**

The stick emits many events per second; each one rewrote four direction pins
and two PWM values to the states they already held.

### What was changed

Two shared modules were added under `tests/`:

| Module | Contents |
|---|---|
| `rover_pins.py` | The verified BCM pin map, the verified polarity tuples, the 30% test speed, and every movement command |
| `rover_input.py` | The DualSense path, the observed `0..255` calibration, the single dead zone, and the reading loop |

They are plain modules, not a `src/` package. Runtime code moves to `src/` only
after turning, controller discovery, and fail-safe behavior are stable.

The seven test scripts now import from those modules and contain only their own
decision logic. The dead zone is 35 everywhere. `classify()` gives the vertical
axis priority everywhere. `rover_pins` holds both PWM channels at zero for
50 ms before any direction reversal, and skips writing a command that is
already applied.

The disconnect watchdog replaces `read_loop()` with a `select()` poll:

- events available → read and act, exactly as before;
- timeout, controller device node still present → hold the current command, because a DualSense held perfectly still sends nothing;
- timeout, device node gone → raise, stop both channels, exit.

That last distinction is deliberate. A stale-input timeout — stopping simply
because the controller has been quiet — was **not** implemented, because a
stick held at full deflection may emit no events at all, and a watchdog that
interrupts normal driving teaches the operator to distrust it.

### What was not changed

No verified pin state, no polarity, no movement sequence, and no test speed.
The August 10 direction truth table in [`docs/wiring.md`](../wiring.md) still
describes the code exactly.

### Supporting files added

`LICENSE` (MIT, with an explicit note that it covers software and documentation
only and makes no claim about physical safety), `requirements.txt`,
`.gitignore`, and a filled-in `hardware/bom.md`, which the README had linked to
while it was empty.

### Next physical session

1. Re-run the August 10 sequences against the refactored scripts and confirm identical behavior.
2. Lift all four wheels and verify spin-left and spin-right for the first time.
3. Power the controller off mid-drive and confirm both channels stop.
4. Confirm the wider dead zone still allows comfortable driving.

---

## 中文

### 复查发现的问题

**1. 预演脚本无法预测小车的真实行为。**

`test_gamepad_input.py` 只打印方向、不碰电机引脚，是驾驶前熟悉摇杆的安全方式。但它
使用 35 计数死区、垂直轴优先，而 `test_gamepad_all_motors.py` 使用 20 计数死区、
**水平轴优先**。

由此产生两个后果：斜着往前推摇杆时，预演显示 `FORWARD`，实车却会原地转向；而更窄的
死区偏偏用在真正驱动四个轮子的脚本上——如果 35 才是让松开的摇杆保持安静所需的值，
那么 20 就意味着松手后仍可能有输出。

**2. 换向时在带载情况下翻转引脚。**

`forward()` 之后紧接 `backward()`，会在电机仍在转动时改变方向输入。30% PWM 下驱动板
扛得住，但这是可以避免的电流冲击，对 MOS 管和 LiPo 都是负担。

**3. 手柄断线后小车仍在行驶。**

`gamepad.read_loop()` 是阻塞的。蓝牙断开时不会抛异常，也不会再有事件——循环就一直
等下去，而上一次的 PWM 值和方向电平仍然保持。小车会以 30% 一直跑，直到有人去按物理
总开关。

**4. 六个引脚对象被定义了七遍。**

每个测试文件都重复 `PWM1 = PWMOutputDevice(12)`，并各自复制一份 `stop()`、
`forward()`、`backward()`。改一根线要改七个文件，而这恰恰是出错就会让实体机器动起来
的地方。

**5. 每个手柄事件都在重写已经正确的引脚。**

摇杆每秒产生大量事件，每个事件都把四个方向引脚和两路 PWM 重写成它们本来就是的状态。

### 具体改动

在 `tests/` 下新增两个共享模块：

| 模块 | 内容 |
|---|---|
| `rover_pins.py` | 已验证的 BCM 引脚映射、方向极性元组、30% 测试速度与全部运动命令 |
| `rover_input.py` | DualSense 路径、实测 `0..255` 标定、统一死区与读取循环 |

它们只是普通模块，不是 `src/` 包。等转向、设备发现和安全停止稳定后，才把运行代码
正式迁到 `src/`。

七个测试脚本现在从这两个模块导入，自身只保留各自的决策逻辑。死区统一为 35；
`classify()` 在所有地方都让垂直轴优先；`rover_pins` 在任何换向前先把两路 PWM 归零并
等待 50 毫秒，并跳过重复写入已经生效的命令。

断线看门狗用 `select()` 轮询替代 `read_loop()`：

- 有事件 → 照常读取并执行；
- 超时、设备节点还在 → 保持当前命令，因为摇杆保持不动时 DualSense 不发任何事件；
- 超时、设备节点消失 → 抛出异常，停止两路电机并退出。

最后一条区分是刻意的。**没有**实现"输入超时即停车"，因为摇杆推到底时可能完全不产生
事件；一个会打断正常驾驶的看门狗，只会让操作者学会不信任它。

### 没有改动的部分

任何已验证的引脚电平、极性、运动顺序和测试速度都没有改。8 月 10 日记录在
[`docs/wiring.md`](../wiring.md) 的方向真值表仍然与代码完全一致。

### 补充文件

新增 `LICENSE`（MIT，并明确写出只覆盖软件与文档、不对实体安全作担保）、
`requirements.txt`、`.gitignore`，并补齐了 README 一直链接却是空文件的
`hardware/bom.md`。

### 下次实车任务

1. 用重构后的脚本重跑 8 月 10 日的流程，确认行为完全一致。
2. 架空四轮，首次实测原地左转和右转。
3. 行驶中关闭手柄电源，确认两路电机立即停止。
4. 确认放宽后的死区不影响正常驾驶手感。
