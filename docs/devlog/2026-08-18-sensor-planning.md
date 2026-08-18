# August 18, 2026 — Planning the lidar: what a single beam can and cannot do

## 2026 年 8 月 18 日——激光规划:一束光能做什么,不能做什么

No hardware was installed and no code was written in this session. A single-point
lidar was acquired, and this entry records the planning decisions made around it
and the reasoning behind each one — including one decision that contradicts a rule
this project set for itself.

本次没有安装任何硬件,也没有写任何代码。购入了一个单点激光测距模块,本文记录围绕它做出的
规划决策和每条决策的理由——包括一条与本项目自己定下的规则相冲突的决定。

---

## English

### The hardware

LDROBOT STP-23L single-point time-of-flight ranging module, sold through WHEELTEC —
the same vendor as the motor driver already on the rover. Range 0.07–7.5 m,
120 Hz, sub-centimeter stated accuracy, 60 kLux ambient light rejection. It ships
with a CH9102F TTL-to-USB adapter, so it can be read over USB serial without
touching the Pi's GPIO at all.

That last point decided the first integration step. Wiring it to the Pi's UART
pins would require confirming its output logic level first, because Raspberry Pi 5
GPIO is not 5 V tolerant. The USB path sidesteps the question entirely. GPIO wiring
can be considered later, once there is a reason to want it.

### Two goals, very different difficulty

The stated goals were obstacle avoidance and a plot of the driven path. They turn
out to sit on completely different dependency chains.

**Obstacle avoidance** is achievable with one beam, but only in a specific and
limited form. A single-point sensor returns one number for one narrow cone
directly ahead. It does not scan. It therefore cannot answer the question that
avoidance actually requires — *which way is clear* — because it has no information
about left or right. It is blind to a chair leg 30 cm off-axis, blind to anything
below the mounting height, and returns unreliable data from surfaces at a steep
angle where the beam reflects away rather than back.

What one beam can do well is answer *is something directly ahead, and how far*.
That is enough for stop, and for a crude back-up-and-turn escape. It is not enough
for steering around an obstacle.

**A trajectory plot** cannot be built from the lidar at all. Drawing a path requires
knowing position, and the rover currently has no position sense of any kind. The
only source of position available is the quadrature encoders already built into all
four motors and still unwired. So:

> The trajectory plot is a product of Phase 2 (encoders) and Phase 3 (odometry).
> The lidar contributes nothing to it.

These are two independent chains. The lidar answers *what is in front of me*; the
encoders answer *where am I*. Neither substitutes for the other.

### Why the obstacle stop belongs in Phase 1, not Phase 4

The roadmap files sensors under Phase 4. The first lidar feature is nonetheless
being placed in Phase 1, on this reasoning:

An obstacle stop is the same *kind* of thing as the disconnect watchdog. Both
monitor a condition and cut motor output when it is met. Neither adds any autonomy —
the operator still drives. Phase 1 is titled "basic movement and safety," and its
exit criterion is that the rover "stops on command and on input failure." Refusing
to drive into a wall is squarely inside that.

The autonomous behaviors — backing off, turning, re-measuring, choosing a direction —
are genuinely new capability and stay in Phase 4.

### Why a veto layer before an autonomous mode

The first lidar feature will not be an autonomous driving mode. It will be a layer
that sits between the gamepad and the motors and vetoes a forward command when the
measured distance is below a threshold. The operator keeps driving.

Three reasons:

1. **Testing stays safe.** The controller is in hand the whole time. If the layer
   misbehaves, the existing disconnect fail-safe is still there underneath it.
2. **It composes with what is already verified** rather than replacing it. The
   disconnect watchdog handles "the operator is gone." The obstacle stop handles
   "the operator is about to hit something." They stack.
3. **It produces a number that cannot be guessed:** the braking distance of this
   rover at 30% PWM on a wood floor. That number sets the threshold. Choosing a
   threshold before measuring it would be inventing a specification.

### Two failure modes to design against from the start

**A bad reading must not read as "clear."** A beam hitting a wall at a steep angle
reflects away and may return nothing, or a garbage value. If the code treats a
failed measurement as a large distance, the rover drives into the wall *because* it
could not see it. The sensor's frame carries a `confidence` field alongside the
distance, plus `noise` and `peak`. The rule is that any frame failing the
confidence check must be treated as *unknown*, and unknown must behave like *close*,
not like *far*.

**Silence is a failure too.** If the sensor stops sending frames — cable knocked
loose, USB disconnect — the last distance value must not persist. This is exactly
the failure the disconnect watchdog was written for on the gamepad side, and the
same pattern applies: a staleness timeout, and stop on expiry.

### The rule this purchase broke

The roadmap's Phase 4 reads: *"Select distance sensors and an IMU based on measured
needs."* The sensor was bought before any such need was measured — no test has yet
shown that the rover cannot be driven safely without one.

This is recorded rather than quietly reconciled. In practice the purchase is
defensible: a distance sensor was going to be needed eventually, and having the
hardware in hand is what made this planning session concrete. But the roadmap said
"measured needs" for a reason, and the honest description is that the rule was
skipped, not satisfied.

The related decision was *not* skipped: no servo has been bought. Mounting the
lidar on a servo to sweep would turn one beam into a crude one-dimensional scan and
convert "something is ahead" into "go this way" — a genuine step change. That
purchase is deliberately deferred until the fixed sensor has demonstrated where it
falls short, so the servo can be justified by a measurement rather than by
anticipation.

### Mounting

Front center of the upper deck, level and pointing forward. Two consequences follow
from that position and both need numbers before any threshold is set:

- The sensor face sits behind the front of the chassis. The reading is the distance
  from the *sensor*, not from the *bumper*. That offset must be measured and
  subtracted.
- At roughly 10 cm off the ground, the beam passes over books, thresholds, and rug
  edges. This is a hard limitation of a fixed single beam, to be documented rather
  than papered over in software.

The mount must also be rigid. A sensor that shifts by two degrees between test runs
invalidates every calibration measurement taken before it moved.

### Planned sequence

Each stage is independently verifiable, in keeping with the project's rule of
changing one subsystem at a time.

| Stage | Work | Depends on |
|---|---|---|
| A | Bench-characterize the sensor over USB. No motors. | — |
| B | Obstacle stop that vetoes the gamepad. Measure braking distance. | A |
| C | Reactive escape: stop, back off, turn, re-measure. | B |
| D | Wire and read the encoders (Phase 2). | Encoder output voltage check |
| E | Odometry, trajectory logging, and plotting. | D |
| F | Optional: servo sweep, if B and C show the fixed beam is the limit. | B |

Stage A resolves the open unknowns: the actual baud rate (sources disagree — 230400
and 921600 both appear for this family), the frame layout, what a low-confidence
reading looks like in practice, the real beam spot size at a working distance, and
the behavior against dark and angled surfaces.

---

## 中文

### 硬件

LDROBOT(乐动)STP-23L 单点飞行时间测距模块,由轮趣科技 WHEELTEC 经销——和车上那块
电机驱动板同一个渠道。量程 0.07~7.5 m,120 Hz,标称精度亚厘米级,抗环境光 60 kLux。
出厂带 CH9102F 的 TTL 转 USB 模块,因此可以走 USB 串口读取,完全不碰树莓派的 GPIO。

最后这一点决定了第一步怎么接。如果直连 Pi 的 UART 引脚,必须先确认它的输出逻辑电平,
因为 Raspberry Pi 5 的 GPIO 不耐 5 V。走 USB 就完全绕开了这个问题。等以后真有理由需要
直连 GPIO 时再考虑。

### 两个目标,难度完全不同

提出的两个目标是自动避障和绘制行驶轨迹图。结果发现它们挂在两条完全不同的依赖链上。

**避障**用一束光能做,但只能做成一种受限的形式。单点传感器对正前方一个窄锥返回一个数字,
它不扫描。因此它回答不了避障真正需要的那个问题——**哪边是空的**——因为它对左右一无所知。
偏离轴线 30 cm 的桌腿它看不见,低于安装高度的东西它看不见,而对大角度斜面它会得到不可靠
的数据,因为光被反射走了而不是反射回来。

一束光能做好的事是回答**正前方有没有东西、有多远**。这足以支撑"停",以及粗糙的"后退加
转向"脱困。但不足以支撑"绕过去"。

**轨迹图则根本不能由激光产生。** 画路径需要知道位置,而小车目前没有任何位置感知。唯一
可用的位置来源,是四个电机里已经自带、但还没接线的正交编码器。所以:

> 轨迹图是第 2 阶段(编码器)和第 3 阶段(里程计)的产物,激光对它没有任何贡献。

这是两条独立的链路。激光回答"我前面有什么",编码器回答"我在哪"。谁也替代不了谁。

### 为什么障碍停车归第 1 阶段,而不是第 4 阶段

路线图把传感器归在第 4 阶段。但第一个激光功能仍被放进第 1 阶段,理由如下:

障碍停车和断线看门狗是**同一类东西**。两者都是监测一个条件,满足时切断电机输出。两者都
不增加任何自主性——驾驶的仍然是人。第 1 阶段的标题是"基础移动与安全",其结束标准是小车
"能按命令停车,也能在输入失效时停车"。拒绝撞墙完全落在这个范围内。

那些自主行为——后退、转向、重测、选方向——才是真正的新能力,仍留在第 4 阶段。

### 为什么先做"否决层"而不是"自动驾驶模式"

第一个激光功能不会是一个自动驾驶模式,而是一层夹在手柄和电机之间的逻辑:当测得距离低于
阈值时,否决前进命令。人照常驾驶。

三个理由:

1. **测试安全。** 手柄全程在手里。就算这一层出问题,底下还压着已经验证过的断线 fail-safe。
2. **它与已验证的东西叠加,而不是取代。** 断线看门狗处理"操作者不在了",障碍停车处理
   "操作者要撞了"。两者可以并存。
3. **它会产出一个编不出来的数字**:这台车在木地板上 30% PWM 的制动距离。这个数字决定
   阈值该设多少。没量就先定阈值,那是在编规格。

### 从一开始就要防的两种失效

**坏读数不能被当成"前方空旷"。** 光束打在大角度斜面上会被反射走,可能什么都收不到,也可能
返回一个垃圾值。如果代码把失败的测量当成"很远",小车就会**因为看不见而撞上去**。传感器的
数据帧里除了距离,还带 `confidence` 置信度,以及 `noise` 和 `peak`。规则是:任何未通过
置信度检查的帧一律视为**未知**,而未知必须表现得像**很近**,不能像**很远**。

**沉默同样是一种失效。** 如果传感器不再发送数据帧——线被碰松、USB 掉了——上一个距离值绝
不能继续沿用。这正是手柄那边写断线看门狗要防的同一种失效,做法也一样:加一个过期超时,超时
即停。

### 这次购买违反了一条自己定的规则

路线图第 4 阶段写的是:**"根据实测需求选择测距传感器和 IMU。"** 而这个传感器是在任何这类
需求被测量出来之前买的——目前还没有任何测试表明,没有它小车就无法被安全驾驶。

这一条选择记录下来,而不是悄悄圆过去。实际上这次购买是站得住脚的:测距传感器早晚都要用,
而硬件到手才让这次规划变得具体。但路线图写"实测需求"是有原因的,诚实的描述是:这条规则被
跳过了,不是被满足了。

与之相关的另一个决定**没有**跳过:舵机没有买。把激光装在舵机上左右扫,能把一束光变成粗糙的
一维扫描,把"前面有东西"变成"往这边走"——那是质变。这笔购买被刻意推迟,直到固定安装的
传感器实际暴露出它的不足为止,这样舵机就能由一次测量来论证,而不是由预期来论证。

### 安装

上层平台车头正中,水平朝前。这个位置带来两个后果,都必须在设定任何阈值之前拿到数字:

- 探头面在底盘最前端的后方。读数是**探头**到障碍的距离,不是**车头**到障碍的距离。这个偏移
  必须量出来减掉。
- 离地大约 10 cm,光束会从书本、门槛、地毯边缘上方掠过。这是固定单点光束的硬限制,应当写进
  文档,而不是指望软件遮掩。

安装还必须刚性。传感器如果在两次测试之间歪了两度,它移动之前做的全部标定数据都作废。

### 计划顺序

每个阶段都可独立验证,符合本项目"一次只改一个子系统"的规则。

| 阶段 | 内容 | 依赖 |
|---|---|---|
| A | 走 USB 台面标定传感器,不接电机 | — |
| B | 否决手柄的障碍停车,并测制动距离 | A |
| C | 反应式脱困:停、后退、转向、重测 | B |
| D | 接线并读取编码器(第 2 阶段) | 编码器输出电压确认 |
| E | 里程计、轨迹记录与绘图 | D |
| F | 可选:舵机扫描,若 B 和 C 表明固定光束是瓶颈 | B |

阶段 A 要解决目前的未知项:真实波特率(资料互相矛盾,这一系列 230400 和 921600 都出现过)、
数据帧结构、低置信度读数在实际中长什么样、工作距离上真实的光斑大小,以及对深色和斜面的表现。
