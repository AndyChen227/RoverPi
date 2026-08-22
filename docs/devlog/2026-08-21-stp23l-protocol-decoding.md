# August 21, 2026 — Decoding the STP-23L serial protocol

# 2026 年 8 月 21 日——解出 STP-23L 串口协议

---

## 🇬🇧 English

### What this session set out to do

Bring up the LDROBOT STP-23L single-point laser rangefinder far enough to
produce trustworthy millimetre readings on the bench. No bracket had arrived
yet, so nothing was mounted on the rover and the motor supply stayed
disconnected for the whole session. This is deliberately the same rule the
project has used since the first motor test: verify one subsystem at a time,
with the other subsystems switched off.

### Electrical bring-up

The module was connected through the supplied USB-serial adapter rather than
the Raspberry Pi GPIO header. Two reasons, in order of importance:

1. A USB plug cannot be inserted incorrectly. The GPIO header can, and the
   cost of a mistake there is a damaged Pi.
2. The GPIO route also needs the serial console disabled, so a first attempt
   there would have had four possible causes of failure instead of one.

The datasheet resolved a concern recorded earlier in the roadmap: the module's
**supply** is 5 V, but its **TX line is 3.3 V logic** (3.5 V maximum), so the
data line is safe for the Pi's GPIO. The 5 V tolerance concern still applies to
the wheel encoders in Phase 2 and must not be confused with this.

| Item | Value |
| --- | --- |
| USB device | `1a86:55d4` QinHeng Electronics USB Single Serial |
| Kernel driver | `cdc_acm` (no vendor driver needed) |
| Device node | `/dev/ttyACM0`, group `dialout` |
| Serial settings | 230400 baud, 8N1, no flow control |
| Direction | Transmit only; the module's RX is factory-use and accepts no commands |

Because the module streams unprompted, the first test could be as simple as
opening the port and counting bytes.

### Finding the frame structure

`tests/lidar_raw_dump.py` captured two seconds of raw bytes and printed hex.
Three numbers agreed and gave the whole structure away:

- `AA AA AA AA` appeared at offset 0 and again at offset 195 → **frame length 195 bytes**
- 1945 bytes/second ÷ 195 = **9.97 frames per second**
- The datasheet states a 120 Hz sampling rate, and 120 ÷ 10 = **12 points per frame**

180 bytes of the 195 are therefore measurement data, at **15 bytes per point**.

### Which field is the distance

`tests/lidar_frame_probe.py` was pointed at a target at three measured
distances. Two `uint16` candidates were tracked:

| Tape measure | Candidate A | Candidate B |
| --- | --- | --- |
| 300 mm | 434.5 | **372.1** |
| 600 mm | 436.0 | **602.4** |
| 1000 mm | 439.8 | **995.7** |

Candidate B follows the tape measure. Candidate A is pinned near 435 regardless
of distance and is the `reftof` internal reference channel — a fixed-length
optical path inside the module used for temperature self-calibration.

Correcting the grid alignment (points begin at frame offset **10**, not 8)
produced a fully self-consistent layout:

```
frame[0:4]     AA AA AA AA        sync
frame[4:6]     00 02              packet type
frame[6:8]     00 00
frame[8:10]    B8 00 = 184        payload length
frame[10:190]  12 points x 15 B   measurement data
frame[190:194] uint32             timestamp
frame[194]     uint8              checksum
```

184 = 180 data bytes + 4 timestamp bytes, which is exactly the span between the
length field and the checksum. That the number falls out of the arithmetic is
the strongest evidence the layout is right.

Per point, `struct` format `<HHIBIH`:

| Offset | Size | Field | At 300 mm |
| --- | --- | --- | --- |
| 0 | 2 | distance, mm | 369 |
| 2 | 2 | noise | 37 |
| 4 | 4 | peak | 1193392 |
| 8 | 1 | confidence | 100 |
| 9 | 4 | intg | 17842 |
| 13 | 2 | reftof | 434 |

### Accuracy so far

600 mm read 602 (+0.3%) and 1000 mm read 996 (−0.4%). The 300 mm point read
372, which is 72 mm high. A wrong reference point would bias all three
equally, and it does not, so this is most likely a bad manual measurement
rather than short-range non-linearity. **It must be re-measured with a proper
tape once the bracket is fitted.**

Spread across the 12 points of a frame was 2–4 mm at all three distances.

### The twelve points are time samples, not directions

12 points per frame at 10 frames/second is the datasheet's 120 Hz sampling
rate. The points are twelve consecutive measurements of the same direction,
100 ms apart in total — not twelve angles. Taking their median is therefore a
100 ms temporal filter, and that, rather than the minimum, is the correct
default for the fusion step in the driver layer.

### Boundary testing: started, not finished

A first pass with `tests/lidar_live.py` produced four results, and on review
**three of them never reached a boundary at all**:

| Test | Observed | Assessment |
| --- | --- | --- |
| Aimed at "nothing" | 2000+, zeros 0/12, confidence 100 | Measured a real object ~2 m away; no-echo never achieved |
| Finger on the window | 1 mm, zeros 0/12, confidence 100 | Genuine sub-minimum behaviour; distinct from the above |
| Black bag at 1.2 m | Stable, confidence 100 | Limit not reached |
| Tilted target | Distance increased smoothly | Correct geometry, not a failure mode |

Only the near-contact test produced anything unusual, and it produced a value
(1 mm) clearly distinguishable from a long reading. **No invalid measurement
has yet been observed**, which is why the next session repeats this properly.

### Open questions carried forward

- **Is `confidence` usable?** It has read 100 in every condition tested so far,
  but every condition tested so far was a *successful* measurement. Concluding
  it is a dead field would be mistaking "no change observed" for "cannot
  change". Unresolved until a genuine failure is produced.
- **Does `intg` saturate?** It rose 17842 → 27926 → 40960 with distance, and at
  1000 mm all twelve points read exactly 40960 = 0xA000. Twelve independent
  adaptive measurements cannot land on the same round number by chance, so this
  looks like a ceiling. If it is, `intg` at maximum is an *early* warning that
  the reading is becoming unreliable — earlier than distance collapsing to zero.
- **What is the checksum algorithm?** Not yet identified. Frames are currently
  accepted on sync pattern and length alone.
- **What does a true no-echo return?** The single most important unknown. If
  no-echo and near-contact return the same value, the driver cannot distinguish
  "about to collide" from "clear road", and the two demand opposite responses.

### Design decision recorded now

Whatever the answer to the last question, the driver layer will treat any
unreadable, stale, or ambiguous measurement as **obstacle present, forward
motion refused**. Failing the other way would mean a dead sensor leaves the
rover unprotected while behaving indistinguishably from a healthy one. This is
the same reasoning as the disconnect watchdog added on August 16.

### Lesson

The first raw dump showed candidate A at 434 while the target happened to be
roughly 43 cm away. That coincidence made a constant internal reference look
exactly like a working distance field. Had it been accepted, the rover would
have believed an obstacle sat 43 cm ahead at all times, in every direction —
a fault that is very hard to diagnose once the sensor is bolted to a moving
vehicle. Three measurements at three distances took about ten minutes and
removed the possibility entirely.

See [`notes/debugging/lidar-reftof-mistaken-for-distance.md`](../../notes/debugging/lidar-reftof-mistaken-for-distance.md).

---

## 🇨🇳 中文

### 这次要做什么

把 LDROBOT STP-23L 单点激光测距模组调通到"能在桌面上输出可信的毫米读数"。
支架还没到，所以全程没有装到车上，电机供电也全程断开。这和第一次电机测试
以来的规则一致：每次只验证一个子系统，其他子系统全部关掉。

### 电气接通

模组通过配套的 USB 串口转接板连接，没有走树莓派 GPIO 排针。两个理由，按重要性排序：

1. USB 插头插不反，GPIO 排针可以，而且插错的代价是烧 Pi。
2. 走 GPIO 还需要先关掉串口控制台，第一次尝试就会有四个可能的失败原因而不是一个。

数据手册澄清了 roadmap 里记录的一个担心：模组的**供电**是 5 V，但它的
**TX 是 3.3 V 电平**（最高 3.5 V），所以数据线对 Pi 的 GPIO 是安全的。
5 V 电平的担心依然适用于阶段 2 的轮式编码器，两件事不能混淆。

| 项目 | 值 |
| --- | --- |
| USB 设备 | `1a86:55d4` 沁恒 USB Single Serial |
| 内核驱动 | `cdc_acm`，不需要厂商驱动 |
| 设备节点 | `/dev/ttyACM0`，属组 `dialout` |
| 串口参数 | 230400 波特率，8N1，无流控 |
| 方向 | 仅发送；模组的 RX 是厂内生产用，不接受命令 |

因为模组上电即持续输出，第一个测试可以简单到"打开串口数字节"。

### 找出帧结构

`tests/lidar_raw_dump.py` 采集 2 秒原始字节并打印十六进制。三个数字互相印证，
整个结构就出来了：

- `AA AA AA AA` 出现在偏移 0，又出现在偏移 195 → **帧长 195 字节**
- 1945 字节/秒 ÷ 195 = **9.97 帧/秒**
- 手册标称采样率 120 Hz，120 ÷ 10 = **每帧 12 个点**

所以 195 字节里有 180 字节是测量数据，**每点 15 字节**。

### 哪个字段是距离

`tests/lidar_frame_probe.py` 在三个量过的距离上各采一次，跟踪两个
`uint16` 候选：

| 卷尺 | 候选 A | 候选 B |
| --- | --- | --- |
| 300 mm | 434.5 | **372.1** |
| 600 mm | 436.0 | **602.4** |
| 1000 mm | 439.8 | **995.7** |

候选 B 跟着卷尺走。候选 A 不管距离多少都锁在 435 附近，它是 `reftof`
内部参考通道——模组里一条长度固定的光路，用于温度自校准。

修正网格对齐（点数据从帧偏移 **10** 开始，不是 8）之后，整个布局完全自洽：

```
frame[0:4]     AA AA AA AA        同步头
frame[4:6]     00 02              包类型
frame[6:8]     00 00
frame[8:10]    B8 00 = 184        负载长度
frame[10:190]  12 点 x 15 字节     测量数据
frame[190:194] uint32             时间戳
frame[194]     uint8              校验
```

184 = 180 数据字节 + 4 时间戳字节，正好是长度字段到校验之间的跨度。
这个数字能从算术里自己掉出来，是布局正确的最强证据。

每个点，`struct` 格式 `<HHIBIH`：

| 偏移 | 长度 | 字段 | 300 mm 时 |
| --- | --- | --- | --- |
| 0 | 2 | 距离，毫米 | 369 |
| 2 | 2 | 噪声 | 37 |
| 4 | 4 | 峰值 | 1193392 |
| 8 | 1 | 置信度 | 100 |
| 9 | 4 | 积分次数 | 17842 |
| 13 | 2 | 参考值 | 434 |

### 目前的精度

600 mm 读到 602（+0.3%），1000 mm 读到 996（−0.4%）。300 mm 读到 372，高了
72 mm。如果是量程参考点选错，三个距离应该偏得一样多，但并没有，所以更可能是
那次手工测量不准，而不是近距非线性。**装上支架后必须用卷尺重新标定近距。**

三个距离下，一帧内 12 个点的极差都在 2–4 mm。

### 12 个点是时间采样，不是方向

每帧 12 点、每秒 10 帧，正好是手册的 120 Hz 采样率。这 12 个点是同一个方向上
连续的 12 次测量，总共跨 100 ms，不是 12 个角度。所以对它们取中位数等于做了一个
**100 ms 的时间窗滤波**——驱动层的融合策略应当默认用中位数而不是最小值。

### 边界测试：开了头，没做完

用 `tests/lidar_live.py` 跑了第一轮，得到四个结果。复盘后发现
**其中三个根本没有触到边界**：

| 测试 | 观察到 | 判断 |
| --- | --- | --- |
| 对着"空" | 2000+，零值 0/12，置信 100 | 测到了 2 米外的真实物体，无回波并未发生 |
| 手指贴光窗 | 1 mm，零值 0/12，置信 100 | 真实的低于下限行为，且与上一行明显不同 |
| 黑背包 1.2 m | 稳定，置信 100 | 没到极限 |
| 倾斜靶面 | 距离平滑变大 | 几何上正确，不是失效 |

只有贴近测试产生了异常值，而那个值（1 mm）与远距读数明显可区分。
**目前还没有观察到任何一次无效测量**，所以下一次要把这项重做。

### 遗留的开放问题

- **置信度能不能用？** 到目前为止所有测试条件下它都是 100，但到目前为止的
  所有测试条件**都是成功的测量**。据此断言它是死字段，等于把"没观察到变化"
  当成了"不会变化"。在制造出一次真正的失败之前无法定论。
- **`intg` 是不是会饱和？** 它随距离从 17842 → 27926 → 40960 上升，
  且 1000 mm 时 12 个点**全部**精确等于 40960 = 0xA000。十二次独立的自适应
  测量不可能碰巧停在同一个整数上，所以这看起来是上限。如果确实如此，
  `intg` 顶格就是"读数开始不可信"的**提前**预警——比距离归零早得多。
- **校验算法是什么？** 尚未确定。目前仅凭同步头和帧长接收帧。
- **真正的无回波返回什么？** 最重要的未知项。如果无回波和贴脸返回同一个值，
  驱动层就无法区分"马上要撞"和"一路畅通"，而这两者要求相反的反应。

### 现在就定下的设计决定

无论最后一个问题的答案是什么，驱动层都将把任何读不到、过期或含义不明的测量
视为**前方有障碍，禁止前进**。反过来的设计意味着传感器一旦失效，小车就失去
全部保护，而且外在表现和正常时完全一样。这与 8 月 16 日加入的断线看门狗
是同一套推理。

### 教训

第一次原始 dump 时，候选 A 读数 434，而靶面恰好在 43 厘米左右。这个巧合让一个
恒定的内部参考值看起来完全像一个正常工作的距离字段。如果当时接受了它，小车会
在任何方向、任何时刻都认为正前方 43 厘米有障碍——而这种故障一旦装到会动的车上，
极难诊断。三个距离各测一次花了大约十分钟，把这个可能性彻底排除。

详见 [`notes/debugging/lidar-reftof-mistaken-for-distance.md`](../../notes/debugging/lidar-reftof-mistaken-for-distance.md)。
