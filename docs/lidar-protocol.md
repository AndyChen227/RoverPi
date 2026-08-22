# STP-23L Serial Protocol / STP-23L 串口协议

Reverse-engineered from captured data on **August 21, 2026**. The public
LDROBOT datasheet documents the electrical interface but **not** the frame
format; everything below was derived from bytes actually produced by this unit.

本文档由 **2026 年 8 月 21 日**实际抓包反推得出。LDROBOT 公开数据手册只提供
电气接口，**没有**帧格式；以下全部内容来自这台模组实际输出的字节。

> **Status / 状态**: frame layout and the distance field are confirmed against
> a tape measure. The checksum algorithm and the failure-mode behaviour of
> `confidence` and `intg` are **not yet confirmed**.
>
> 帧布局和距离字段已用卷尺验证。校验算法、以及 `confidence` 和 `intg` 在
> 失效条件下的行为**尚未确认**。

---

## 1. Link layer / 链路层

| Item / 项目 | Value / 值 |
| --- | --- |
| Baud rate / 波特率 | 230400 |
| Frame format / 帧格式 | 8 data bits, 1 stop bit, no parity, no flow control |
| Direction / 方向 | Module → host only. The module's RX is factory-use and accepts no commands. |
| Supply / 供电 | 4.5–5.5 V, typically 5 V. 33 mA running, 95 mA starting. |
| Logic level / 逻辑电平 | TX is 3.3 V typical, 3.5 V maximum — safe for Raspberry Pi GPIO |
| Range / 量程 | 0.03 – 7.5 m |
| Sampling rate / 采样率 | 120 Hz |

The module transmits continuously from power-on. No initialisation is required.

模组上电后持续发送，不需要任何初始化。

### Verified connection / 已验证的连接方式

Via the bundled USB-serial adapter:

| Item / 项目 | Value / 值 |
| --- | --- |
| USB ID | `1a86:55d4` QinHeng Electronics USB Single Serial |
| Kernel driver / 内核驱动 | `cdc_acm` (in-tree; no vendor driver required) |
| Device node / 设备节点 | `/dev/ttyACM0` |
| Permissions / 权限 | `crw-rw----  root dialout` — the user must be in `dialout` |

**Note / 注意**: the node is `ttyACM0`, not `ttyUSB0`. The adapter declares
itself as a standard CDC device, so no CH34x driver is needed.

### Not yet used: direct GPIO UART / 尚未使用：直连 GPIO 串口

Also possible and likely to be the final on-vehicle wiring, since it removes
the adapter and USB cable from the chassis. Only three wires are needed because
the module's RX is unused:

| Module / 模组 | Raspberry Pi |
| --- | --- |
| P5V | 5 V (physical pin 2 or 4) |
| GND | GND (physical pin 6) |
| TX | GPIO15 / RXD (physical pin 10) |
| RX | not connected / 悬空 |

Before wiring this way, **verify the JST pin order with a multimeter**. The
datasheet numbers the connector's physical positions (1 = TX, 2 = RX, 3 = GND,
4 = P5V); it does not promise which colour goes where, and the two ends of a
JST cable can be reversed. This route also requires the Linux serial console
to be disabled first.

接线前**必须用万用表确认 JST 线序**。手册标注的是接头的物理位置，不保证颜色
对应关系，而 JST 线两端完全可能是反的。此外这条路还需要先关闭串口控制台。

---

## 2. Frame layout / 帧结构

**Total 195 bytes. All multi-byte fields are little-endian.**

**每帧 195 字节，所有多字节字段均为小端。**

| Offset | Size | Content | Observed value |
| --- | --- | --- | --- |
| 0 | 4 | Sync header / 同步头 | `AA AA AA AA` |
| 4 | 2 | Packet type / 包类型 | `00 02` |
| 6 | 2 | Unknown, constant / 未知，恒定 | `00 00` |
| 8 | 2 | Payload length / 负载长度 | `B8 00` = 184 |
| 10 | 180 | 12 measurement points / 12 个测量点 | 15 bytes each |
| 190 | 4 | Timestamp / 时间戳 | uint32, increments |
| 194 | 1 | Checksum / 校验 | **algorithm unknown** |

The length field is self-consistent: 184 = 180 payload + 4 timestamp, i.e. the
span between the length field and the checksum.

长度字段自洽：184 = 180 负载 + 4 时间戳，正好是长度字段到校验之间的跨度。

### Frame rate / 帧率

Measured at 1945 bytes/s ÷ 195 = **9.97 frames/s**. Twelve points per frame at
ten frames per second is the datasheet's 120 Hz sampling rate.

### ⚠️ The twelve points are consecutive time samples, not directions

### ⚠️ 12 个点是连续的时间采样，不是方向

They are twelve measurements of the same direction spanning 100 ms — this is a
single-point rangefinder, not a scanner. Taking the median of a frame is
therefore a 100 ms temporal filter. Median is preferred over minimum, which
would amplify noise spikes.

这是单点测距，不是扫描仪。对一帧取中位数等于做 100 ms 时间窗滤波。
应优先用中位数而非最小值，后者会放大噪声毛刺。

---

## 3. Point structure / 点结构

**15 bytes per point.** Python `struct` format: `<HHIBIH`

| Offset | Size | Type | Field | 300 mm | 600 mm | 1000 mm |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 2 | uint16 | **distance, mm / 距离，毫米** | 369 | 601 | 997 |
| 2 | 2 | uint16 | noise / 噪声 | 37 | 53 | 96 |
| 4 | 4 | uint32 | peak / 峰值 | 1193392 | 1365556 | 1236821 |
| 8 | 1 | uint8 | confidence / 置信度 | 100 | 100 | 100 |
| 9 | 4 | uint32 | intg / 积分次数 | 17842 | 27926 | **40960** |
| 13 | 2 | uint16 | reftof / 参考值 | 434 | 435 | 439 |

```python
import struct
POINT_FMT = "<HHIBIH"   # 15 bytes, no padding
dist, noise, peak, conf, intg, reftof = struct.unpack(POINT_FMT, point_bytes)
```

### Field notes / 字段说明

**`distance`** — the only field validated against a physical measurement.

**`confidence`** — has read exactly 100 (`0x64`) in every condition tested so
far. However, every condition tested so far was a *successful* measurement, so
this does not establish that the field is constant. Treat as **unknown**, not
as unusable, until a genuine failure is observed.

到目前为止所有条件下都恒为 100，但**所有测过的条件都是成功的测量**，
因此不能据此断定它是常量。在观察到真正的失败之前，按**未知**处理。

**`intg`** — the number of laser pulses accumulated for one measurement.
Returned echo power falls roughly with the square of distance, so weak returns
must be averaged over more pulses to lift the signal out of ambient infrared
noise; N accumulations improve signal-to-noise by roughly √N. Higher `intg`
therefore means "this measurement was harder to make".

At 1000 mm all twelve points read exactly 40960 = `0xA000`. Twelve independent
adaptive measurements landing on the same round number indicates a **ceiling**,
not a coincidence. **Hypothesis, not yet verified**: `intg` at maximum is an
early indication that the reading is becoming unreliable — available before
`distance` collapses.

`intg` 是这次测量累加了多少个激光脉冲。回波功率大致按距离平方衰减，弱回波必须
靠多次累加把信号从环境红外噪声里提出来，累加 N 次信噪比约提升 √N 倍。所以
`intg` 越高代表"这次测量越吃力"。1000 mm 时 12 个点全部精确等于 0xA000，说明
撞到了上限。**假说，尚未验证**：`intg` 顶格是读数开始不可信的提前信号。

**`reftof`** — an internal reference channel. Part of the laser never leaves
the module and strikes the receiver over a fixed-length path, so this value is
constant by design. Its purpose is self-calibration: electronic delays drift
with temperature, and a shift in the reference indicates the main measurement
needs the same correction.

模组内部有一条固定长度的参考光路，一小部分激光不出射直接打到接收端，
所以这个值天生恒定。它的用途是自校准：电子延迟随温度漂移，参考通道一旦变化，
主测量值需要按同样比例修正。

**⚠️ `reftof` reads ≈ 434, which is a plausible distance in millimetres.**
During the first capture the target happened to be about 43 cm away, and the
field was initially mistaken for the distance. See
[`notes/debugging/lidar-reftof-mistaken-for-distance.md`](../notes/debugging/lidar-reftof-mistaken-for-distance.md).

---

## 4. Accuracy / 精度

Bench measurement, target normal to the optical axis, 110 points per distance:

| Reference | Median reading | Error | Spread across 12 points |
| --- | --- | --- | --- |
| 300 mm | 372 mm | **+72 mm** ⚠️ | 11 mm |
| 600 mm | 602 mm | +2 mm | 7 mm |
| 1000 mm | 996 mm | −4 mm | 4 mm |

The 300 mm point is an outlier. A wrong reference point would bias all three
distances equally, and it does not, so the reference distance itself was
probably measured badly. **Re-measure short range with a proper tape once the
bracket is fitted.**

300 mm 那一项是离群值。若是参考点选错，三个距离应偏移相同的量，但并没有，
所以更可能是那次参考距离量得不准。**装上支架后用卷尺重新标定近距。**

---

## 5. Known unknowns / 已知未知

These must be resolved before the driver layer is written:

| Question / 问题 | Why it matters / 为什么重要 |
| --- | --- |
| What does a true no-echo return? | If no-echo and near-contact return the same value, the driver cannot distinguish "about to collide" from "clear road". These demand opposite responses. |
| Does `confidence` ever leave 100? | If it does, it is the validity flag and the driver becomes simple. |
| Does `intg` saturation predict bad data? | If so, it gives warning earlier than a distance collapse. |
| Checksum algorithm? | Frames are currently accepted on sync pattern and length alone. |
| Maximum usable range on dark and oblique surfaces? | Sets the real detection envelope, which will be shorter than the 7.5 m specification. |

---

## 6. Fail-safe policy / 失效处理原则

**Decided in advance of the measurements, and not contingent on them.**

Any measurement that is unreadable, stale, or ambiguous is treated as
**obstacle present, forward motion refused**.

The alternative — permitting motion when the sensor cannot be trusted — means a
failed sensor silently removes all protection while the rover behaves exactly
as it does when healthy. Same reasoning as the controller disconnect watchdog
added on August 16.

任何读不到、过期或含义不明的测量，一律按**前方有障碍、禁止前进**处理。

反过来的设计意味着传感器失效后小车静默地失去全部保护，而外在表现与正常时
完全一致。这与 8 月 16 日加入的手柄断线看门狗是同一套推理。
