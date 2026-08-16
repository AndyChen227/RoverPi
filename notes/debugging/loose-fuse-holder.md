# A loose fuse looked exactly like a software bug — 2026-08-16

## Symptom

During a verification session, three motor tests were run in a row:

| Test | Result |
|---|---|
| `test_motor_channel2.py` — right side, two motors | ✅ moved |
| `test_motor_channel2_backward.py` — right side, two motors | ✅ moved |
| `test_all_motors.py` — all four motors | ❌ printed `FORWARD`, `STOP`, `BACKWARD` correctly, but no wheel turned |

The program produced no error and no traceback. Every print statement appeared
on schedule. Only the wheels were missing.

## Why it looked like software

The session was verifying freshly refactored code, and the two tests that
worked used a different code path from the one that failed: the single-channel
tests call `left_only()` / `right_only()`, while the four-wheel test calls
`forward()` and `backward()`, which go through `_apply()`. That function had
never run on hardware before. A brand-new code path failing while the older
ones worked is a very convincing false lead.

## How it was isolated

The deciding move was to bypass the new module entirely and drive the pins with
the original, already-verified pattern in a single inline command:

```bash
python3 -c "
from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep
PWM1=PWMOutputDevice(12); INA1=DigitalOutputDevice(23); INB1=DigitalOutputDevice(24)
PWM2=PWMOutputDevice(13); INA2=DigitalOutputDevice(5);  INB2=DigitalOutputDevice(6)
sleep(3)
INA1.off(); INB1.on(); INA2.on(); INB2.off()
PWM1.value=0.30; PWM2.value=0.30
sleep(1)
PWM1.value=0; PWM2.value=0
"
```

This also failed. Since that code was known-good, the fault had to be
electrical, not logical.

## Root cause

The inline fuse was loose in its holder. The contact was good enough to pass
the current two motors needed and intermittent enough to drop out under the
higher inrush of four. Reseating it fixed everything; all three tests then
passed.

## Lessons

**A hardware fault can select for load.** "Two motors work, four do not" reads
like a current-capacity problem, and it is — but the cause can be a bad contact
rather than a flat battery. Check connections before concluding the LiPo is
depleted.

**When new code fails, first re-run known-good code on the same hardware.** One
inline command separated "my new module is broken" from "the rover is not
powered". Without that step the next hour would have gone into reading a
function that was never at fault.

**Silence is a clue.** The motors made no sound at all. A driver that receives
its signals but cannot deliver current usually produces some noise; total
silence points upstream, toward power.

## 中文总结

现象：右侧两个电机的两个测试都正常，四轮测试打印全部正确却一个轮子都不转，且没有
任何报错。

误导之处：失败的测试走的是刚重构、从未在硬件上跑过的 `_apply()` 代码路径，而成功的
两个走的是 `left_only()` / `right_only()`。新代码路径失败、旧路径正常，看起来非常
像是新代码的 bug。

定位方法：用一条不依赖任何新模块的内联命令，按 8 月 10 日验证过的原始写法直接操作
引脚。它同样不转，于是可以断定问题在电路而不是逻辑。

真正原因：串联保险丝在保险丝座里松了。接触电阻在两个电机的电流下还能导通，在四个
电机的启动浪涌下就断开。重新插紧后三个测试全部通过。

经验：

1. 硬件故障会**挑负载**。"带得动两个带不动四个"确实是电流问题，但原因可能是接触
   不良而不是电池没电，先查接线再怀疑电池。
2. 新代码出问题时，**先在同一套硬件上重跑已知可用的旧代码**。一条内联命令就区分了
   "我的新模块坏了"和"车根本没通电"。
3. **完全没声音也是线索**。驱动板收到信号但供不上电流时通常会有轻微响动；一点声音
   都没有，说明问题在更上游的供电侧。
