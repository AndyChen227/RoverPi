# August 16, 2026 — Safety consistency and shared modules

## 2026 年 8 月 16 日——安全一致性与共享模块

No hardware changed in this session. This was a code review of everything
written between August 6 and August 10, the fixes that review produced, and
then a physical verification session on the rover the same day. Tests 1–6 ran
with all four wheels lifted; the full gamepad driving test ran **on the
ground** for about ten continuous minutes. Results are in
[Verification session](#verification-session--same-day).

> [!NOTE]
> This paragraph originally said nothing had been physically re-tested. It was
> written before the verification session and was never updated afterwards, so
> for two days the log opened by contradicting its own results. Corrected on
> August 18 — see [`2026-08-18-repository-audit.md`](2026-08-18-repository-audit.md).

本次没有改动任何硬件，只做了 8 月 6 日到 8 月 10 日全部代码的复查与修复，并在当天
于实车上完成验证。第 1 到第 6 项为四轮架空运行，完整手柄驾驶测试则在**地面**上连续
行驶约 10 分钟。结果见下方验证测试一节。

> [!NOTE]
> 这一段原本写的是"所有改动都没有在实车上重新运行"。那句话写于上车验证之前，验证
> 完成后忘了回头修改，导致本文开头连续两天在否定自己的实测结果。已于 8 月 18 日
> 更正，见 [`2026-08-18-repository-audit.md`](2026-08-18-repository-audit.md)。

---

## English

### What the review found

**1. The rehearsal test did not predict the rover's behavior.**

`test_gamepad_input.py` prints movement words without touching a motor pin. It
is the safe way to learn the stick before driving. But it used a 35-count dead
zone and chose the axis the stick was pushed furthest along, while
`test_gamepad_all_motors.py` used a 20-count dead zone and gave the
*horizontal* axis absolute priority.

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
decision logic. The dead zone is 35 everywhere. `classify()` uses the
rehearsal script's dominant-axis rule everywhere: whichever axis the stick is
pushed furthest along decides the command, so neither axis can silently refuse
to do the obvious thing. `rover_pins` holds both PWM channels at zero for
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

### Recorded late: spin turns are verified

Spin left and spin right were physically verified in a driving session after
August 10, but the repository was never updated and still described them as
code-only. That is now corrected across the README, `docs/wiring.md`,
`docs/hardware.md`, `docs/setup.md`, `docs/roadmap.md`, `tests/README.md`, and
`notes/debugging/dualsense-input.md`. The August 10 devlog is deliberately left
untouched, because it is an accurate record of what was true on that date.

The exact date of the turning session was not logged and is recorded here as
"after August 10, 2026". Losing a date is the small cost of verifying on the
rover and updating the repository later; verifying and recording in the same
session avoids it.

One distinction is worth keeping. What the turning session verified is the
*pin combination* — those four direction inputs really do spin the rover the
stated way. Which stick region requests a turn is a separate question, and it
changed today: absolute horizontal priority was replaced by the dominant-axis
rule. The movement is verified; the new way of asking for it is not.

### Verification session — same day

Everything above was then run on the rover. Tests 1–6 ran with all four wheels
lifted. The final test, `test_gamepad_all_motors.py`, was run **on the ground**:
an indoor wood floor, 30% PWM, about ten continuous minutes of driving.

| Check | Result |
|---|---|
| Shared modules import and claim the correct pins | ✅ `GPIO12 23 24 13 5 6`, dead zone 35, thresholds 93/163 |
| `test_gamepad_input.py` — four directions | ✅ |
| Angled forward push resolves to forward, not a spin | ✅ `FORWARD x=172 y=83` |
| Released stick returns to stop and stays quiet | ✅ |
| Disconnect watchdog, no motors | ✅ `CONTROLLER LOST (Errno 19)` and clean exit |
| `test_motor_channel1.py` — corrected forward polarity | ✅ left side ran rover-forward |
| Channel 2 forward and backward | ✅ |
| `test_all_motors.py` — four wheels | ✅ after a hardware fault, see below |
| `test_gamepad_all_motors.py` — full driving, **on the ground** | ✅ forward, backward, stop, both spin turns |
| Ground drive endurance | ✅ about 10 continuous minutes on wood floor at 30% PWM |
| Spin turns under floor friction | ✅ rotates in place cleanly, no binding |
| Straight-line behavior | ✅ no drift noticed — but see the boundary note below |
| **Disconnect watchdog while driving, on the ground** | ✅ all four wheels stopped immediately |

The disconnect watchdog is the result that matters most, and it was triggered on
the ground rather than in the air — with the rover carrying its own weight and
real momentum, not four wheels free-spinning. Under the previous `read_loop()`
the same action left the last PWM command applied and the rover would have kept
driving until someone reached the power switch.

**Boundary on the straight-line result.** No drift was noticed, but the operator
was steering the whole time, so a human was closing the loop. This is not
evidence of open-loop straight-line tracking. Establishing that needs a
fixed-distance run with the forward command held and no steering correction, with
the lateral deviation measured rather than eyeballed.

### The four-wheel test that was not a code bug

`test_all_motors.py` printed its whole sequence correctly while no wheel moved,
immediately after both single-channel tests had passed. The failing test was
the only one using the newly written `_apply()` path, which made new code look
guilty. Re-running the original pre-refactor pin pattern as a one-line command
failed the same way, which cleared the software; the inline fuse was loose in
its holder, conducting well enough for two motors and dropping out under the
inrush of four. Full write-up in
[`notes/debugging/loose-fuse-holder.md`](../../notes/debugging/loose-fuse-holder.md).

### Considered and rejected

Hysteresis on the dominant-axis rule. Held at an exact 45 degrees, `|dx|` and
`|dy|` sit within one count and noise flips the command between forward and
turning. On the rover this does not happen in normal driving — the diagonal is
hard to hold by accident and any push past it resolves cleanly — so the extra
state was not added. Revisit only if a real drive stutters on diagonals.

### Next physical session

1. Discover the controller by identity instead of the fixed `event11` path.
2. Run without an active SSH session, then at planned startup.
3. Measure open-loop straight-line tracking over a fixed distance with no
   steering correction.

---

## 中文

### 复查发现的问题

**1. 预演脚本无法预测小车的真实行为。**

`test_gamepad_input.py` 只打印方向、不碰电机引脚，是驾驶前熟悉摇杆的安全方式。但它
使用 35 计数死区、按"哪个方向推得更多就听哪个"判断，而 `test_gamepad_all_motors.py`
使用 20 计数死区、**水平轴绝对优先**。

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
`classify()` 在所有地方都采用预演脚本的主导轴规则——摇杆往哪个方向推得更多就执行
哪个方向，任何一个轴都不会被另一个轴无声地压制；`rover_pins` 在任何换向前先把两路
PWM 归零并等待 50 毫秒，并跳过重复写入已经生效的命令。

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

### 补记：原地转向其实已经实测通过

原地左转和右转在 8 月 10 日之后的一次驾驶中已经实测通过，但仓库一直没更新，还写着
"只有代码"。现已在 README、`docs/wiring.md`、`docs/hardware.md`、`docs/setup.md`、
`docs/roadmap.md`、`tests/README.md` 和 `notes/debugging/dualsense-input.md` 中全部
更正。8 月 10 日那篇日志刻意不改——它准确记录了那一天的真实情况。

转向那次的具体日期没有记录，这里只能写成"2026 年 8 月 10 日之后"。丢掉一个日期，是
"先实测、后补文档"的小代价；实测完当场记录就不会有这个问题。

有一点需要区分清楚：那次实测验证的是**引脚组合**——这四个方向输入确实让小车按预期
原地转。而"摇杆的哪个区域触发转向"是另一回事，并且今天改了：水平轴的优先级让给了
规则：水平轴绝对优先被主导轴规则取代。动作已验证，请求动作的新方式尚未验证。

### 当天的验证测试

上述改动当天就在实车上跑完了。第 1 到第 6 项为四轮架空；最后一项
`test_gamepad_all_motors.py` 在**地面**上运行：室内木地板、30% PWM、连续约 10 分钟。

| 检查项 | 结果 |
|---|---|
| 共享模块导入并占用正确引脚 | ✅ `GPIO12 23 24 13 5 6`，死区 35，阈值 93/163 |
| `test_gamepad_input.py` 四个方向 | ✅ |
| 斜向前推判为前进而非原地转 | ✅ `FORWARD x=172 y=83` |
| 松手回到停止且不再刷屏 | ✅ |
| 断线看门狗（不带电机） | ✅ `CONTROLLER LOST (Errno 19)` 并干净退出 |
| `test_motor_channel1.py` 修正后的前进极性 | ✅ 左侧朝小车前进方向转 |
| Channel 2 前进与后退 | ✅ |
| `test_all_motors.py` 四轮 | ✅ 期间遇到一次硬件故障，见下 |
| `test_gamepad_all_motors.py` 完整驾驶（**地面**） | ✅ 前进、后退、停止、左右原地转 |
| 地面连续行驶 | ✅ 木地板 30% PWM 连续约 10 分钟 |
| 地面摩擦下原地转向 | ✅ 干脆旋转，无卡滞 |
| 直线行驶 | ✅ 未观察到跑偏——但见下方边界说明 |
| **地面行驶中断线停车** | ✅ 四轮立即停止 |

其中最重要的是最后一项，而且它是在地面上触发的，不是架空——小车承载自身重量、带着真实
惯性，而不是四个轮子空转。旧的 `read_loop()` 在同样操作下会保持上一条 PWM 命令，小车
会一直跑到有人去按总开关。

**关于直线行驶结果的边界。** 没有观察到跑偏，但全程有人在打方向，闭环其实是操作者完成的。
因此这不能作为开环直线性的证据。要确立这一点，需要一次固定距离、保持前进命令、不做任何
修正的实测，并真正测量横向偏移，而不是靠肉眼判断。

### 那次"四轮不转"其实不是代码问题

两个单通道测试刚刚通过，`test_all_motors.py` 却打印全部正确而一个轮子不转。偏偏失败
的这个是唯一走新写的 `_apply()` 路径的测试，看起来非常像新代码的锅。用一条内联命令
按重构前的原始写法直接操作引脚，同样不转——软件因此洗清嫌疑。真正原因是串联保险丝
在保险丝座里松了，两个电机的电流还能导通，四个电机的启动浪涌下就断开。完整记录见
[`notes/debugging/loose-fuse-holder.md`](../../notes/debugging/loose-fuse-holder.md)。

### 考虑过但没有采用

给主导轴规则加迟滞。摇杆停在正好 45 度时 `|dx|` 与 `|dy|` 只差一个计数，噪声会让命令
在前进和转向之间反复跳变。但实车上正常驾驶不会出现——那个对角位置很难无意中保持住，
稍微推过去判断就很干脆。为一个没人会停留的位置增加状态不划算。除非以后地面行驶时
真的在斜向出现顿挫，否则不重新考虑。

### 下次实车任务

1. 按设备身份自动发现手柄，不再写死 `event11`。
2. 验证无 SSH 连接时运行，再做开机自启动。
3. 实测开环直线性：固定距离内不做任何修正，测量横向偏移。
