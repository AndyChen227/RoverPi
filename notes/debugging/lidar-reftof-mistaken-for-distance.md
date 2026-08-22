# A constant field that looked exactly like a distance

# 一个恒定字段，看起来完全像距离

**Date / 日期**: August 21, 2026
**Subsystem / 子系统**: STP-23L laser rangefinder, protocol decoding
**Cost / 代价**: caught in ten minutes; would have been very expensive later

---

## 🇬🇧 English

### What happened

The first raw capture from the STP-23L was taken with the module pointed at a
wall roughly 40–45 cm away. Slicing the frame on a 15-byte grid and reading the
first `uint16` of each point produced this:

```
point 0 : 184
point 1 : 434
point 2 : 435
point 3 : 433
...
point 11: 433
```

Eleven of twelve points agreed within 3 mm, and the value matched the estimated
distance to the wall. The grid alignment looked confirmed and the field looked
identified. The reading was announced as the distance.

### Why it was wrong

The field was `reftof` — an internal reference channel. A fraction of the laser
never leaves the module and travels a fixed-length path to the receiver, so the
value is constant by design and used for temperature self-calibration.

It reads about 434. The wall happened to be about 43 cm away.

Two further details made the mistake look well supported:

- **The stability was convincing.** A 3 mm spread across twelve points is
  exactly what a good measurement of a stationary flat target looks like. It is
  also what a hardware constant looks like. The evidence did not discriminate.
- **The grid was misaligned by two bytes**, which put `reftof` at the start of
  each slice instead of the end. The misalignment and the coincidence
  reinforced each other: the wrong offset produced a plausible number, and the
  plausible number confirmed the wrong offset.

The real distance field sits two bytes further along. Points actually begin at
frame offset 10, not 8, and the two bytes at offset 8 are the payload length
field — which had been read as a twelfth measurement of 184.

### How it was caught

Three measurements at three distances, taking about ten minutes:

| Tape measure | Candidate A | Candidate B |
| --- | --- | --- |
| 300 mm | 434.5 | 372.1 |
| 600 mm | 436.0 | 602.4 |
| 1000 mm | 439.8 | 995.7 |

One row proves nothing. Three rows settle it immediately: candidate A does not
move, candidate B tracks the tape.

### What it would have cost

A rover whose obstacle stop reads a constant 434 believes an obstacle sits
43 cm ahead permanently, in every direction, indoors and outdoors. It would
either refuse to move at all, or — if the threshold were set below 434 —
appear to work perfectly while providing no protection whatsoever.

The second case is far worse. It fails silently, it fails on a moving vehicle,
and every attempted diagnosis would start by suspecting the mounting, the
threshold, or the control loop, because the sensor readings look healthy.

### Lessons

1. **A single measurement cannot identify a field. It can only fail to
   contradict one.** Identification requires varying the input and confirming
   the output follows.

2. **Stability is not correctness.** A constant and a good measurement of a
   stationary target are indistinguishable while the target does not move. The
   test must move the target.

3. **A plausible value confirming a guessed offset is circular.** The
   misalignment survived because it produced a number that looked right. Two
   errors that support each other are harder to see than one error alone.

4. **Sensor fields are cheap to verify before mounting and expensive after.**
   Ten minutes on a desk, or hours chasing a phantom fault on a rover that
   looks fine.

---

## 🇨🇳 中文

### 发生了什么

STP-23L 的第一次原始抓包是把模组对着大约 40–45 厘米外的墙做的。按 15 字节网格
切帧、读每个点的第一个 `uint16`，得到：

```
点 0 : 184
点 1 : 434
点 2 : 435
点 3 : 433
...
点 11: 433
```

12 个点里有 11 个落在 3 毫米以内，而且数值和估计的墙距吻合。网格对齐看起来
被确认了，字段看起来被认出来了。于是这个读数被当作距离宣布了出去。

### 为什么错了

这个字段是 `reftof`——内部参考通道。一小部分激光不出射，沿一条固定长度的
光路直接打到接收端，所以这个值天生恒定，用于温度自校准。

它的读数大约是 434。而那面墙恰好在 43 厘米左右。

还有两个细节让这个错误看起来证据充分：

- **稳定性很有说服力。** 12 个点极差 3 毫米，这正是"对静止平面做一次好测量"
  应有的样子。但它同时也是"一个硬件常量"应有的样子。这份证据无法区分两者。
- **网格整体偏移了 2 字节**，把 `reftof` 从每个点的末尾挪到了开头。
  错位和巧合互相加固：错误的偏移产生了一个看着合理的数字，而这个合理的数字
  又反过来确认了错误的偏移。

真正的距离字段在再往后 2 字节的位置。点数据实际从帧偏移 10 开始而不是 8，
偏移 8 处那两个字节是负载长度字段——它当时被读成了"第 12 个测量值 184"。

### 怎么发现的

三个距离各测一次，大约十分钟：

| 卷尺 | 候选 A | 候选 B |
| --- | --- | --- |
| 300 mm | 434.5 | 372.1 |
| 600 mm | 436.0 | 602.4 |
| 1000 mm | 439.8 | 995.7 |

一行数据什么都证明不了。三行数据当场定案：候选 A 纹丝不动，候选 B 跟着卷尺走。

### 如果没发现，代价是什么

一台障碍停车读数恒为 434 的小车，会认为正前方 43 厘米永远有障碍，
在任何方向、室内室外都一样。它要么根本不动，要么——如果阈值设在 434 以下——
看起来完美工作，实际上提供零保护。

第二种情况糟糕得多。它静默失效，在一台会动的车上失效，而且任何一次排查都会
先怀疑安装、阈值或控制循环，因为传感器读数看起来健康得很。

### 教训

1. **单次测量无法确认一个字段，只能"没有推翻"它。** 确认必须改变输入，
   并确认输出跟着走。

2. **稳定不等于正确。** 只要靶面不动，一个常量和一次好测量就无法区分。
   测试必须让靶面动起来。

3. **用一个合理的数值去确认一个猜出来的偏移，是循环论证。** 那个错位之所以
   活了下来，正是因为它产出了一个看着对的数字。两个互相支撑的错误，
   比单独一个错误难发现得多。

4. **传感器字段在装车前验证很便宜，装车后很贵。** 桌面上十分钟，
   或者在一台外表正常的车上追几个小时的幽灵故障。
