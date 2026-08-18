# August 18, 2026 — Repository audit: the docs understated the rover

## 2026 年 8 月 18 日——仓库校对：文档低估了小车

No hardware and no runtime behavior changed in this session. The whole repository
was read end to end against what had actually happened on the rover, and the
documentation was corrected where the two disagreed. Every disagreement pointed
the same way: **the repository claimed less than the rover had done.**

本次没有改动任何硬件，也没有改动任何运行行为。把整个仓库从头到尾读了一遍，与实车上
真正发生过的事情逐条比对，并修正了不一致之处。所有不一致都指向同一个方向：
**仓库记录的成果，比小车实际做到的要少。**

---

## English

### The finding that mattered most

The August 16 devlog opened with this sentence:

> Nothing was physically re-tested, so every change below is recorded as
> implemented but unverified.

Further down, the same file contained a section titled *Verification session —
same day*, with a table in which every row passed.

The opening paragraph had been written before the rover session and was never
revisited afterwards. For two days the most important log in the repository began
by denying its own results — and it is the paragraph a reader sees first.

**Lesson:** a document written in two sittings needs a re-read of the first
sitting before it is committed. The failure mode is not writing something false;
it is writing something that was true at 2pm and committing it at 8pm.

### The ground drive was never recorded

Across the README, `docs/hardware.md`, `docs/wiring.md`, `docs/setup.md`,
`docs/roadmap.md`, `tests/README.md`, and the August 16 devlog, every description
of the August 16 verification said the wheels were lifted. One item on three
separate to-do lists read *"move from wheels-lifted testing to a controlled
ground drive."*

That had already happened. On August 16, tests 1–6 ran with the wheels lifted, and
then `test_gamepad_all_motors.py` was run **on the ground**: an indoor wood floor,
30% PWM, about ten continuous minutes of driving. Forward, backward, stop, and both
spin turns all behaved on the floor as they had in the air. The rover rotates in
place cleanly under real friction. And the disconnect fail-safe — powering the
controller off mid-drive — was triggered on the ground, with the rover carrying its
own weight and real momentum, not with four wheels free-spinning in the air.

That last point is the strongest safety result the project has, and the repository
was filing it as a weaker one.

**Lesson:** the same habit that produced the lost turning date produced this. If a
session is not written up before the tools are put away, the record drifts toward
whatever the previous session said. Test, then write, in that order, in the same
sitting.

### What "no drift" is and is not

No drift was noticed during the ten-minute drive. That observation has been
recorded — and explicitly fenced.

The operator was steering the whole time. A human holding a stick corrects a slow
drift without noticing they are doing it, which means the loop was closed by the
driver, not by the machine. "No drift observed while being driven" is not
"tracks straight open-loop."

Establishing the real result needs its own test: a fixed distance, the forward
command held, no steering correction, and the lateral deviation measured rather
than eyeballed. That test is now a Phase 1 item. Its outcome decides how much of
the Phase 3 case for PID rests on straight-line tracking versus on odometry and
repeatable distances — and it is worth knowing before building the argument
around it.

### Stale comments in the code

`rover_pins.py` still described `turn_left()` and `turn_right()` as awaiting a
confirmation run, and the module docstring of `test_gamepad_all_motors.py` listed
all three August 16 changes as unverified. Both were written the morning of the
16th and were obsolete by that evening.

Docstrings that carry verification status are genuinely useful — the status is
right next to the pin values it applies to. But they age exactly like
documentation, and they are easy to forget because they live in files that are
opened to be run, not to be read.

### Corrections applied

| File | Correction |
|---|---|
| `docs/devlog/2026-08-16-...md` | Opening paragraph corrected; ground drive and its details added to the verification table; a note left in place explaining what the paragraph used to say |
| `README.md` | Ground-driving row added to both status tables; turning and fail-safe rows made specific; test-table note corrected to exclude `test_gamepad_motor_left.py`; ground-drive results added to the verification boundary; a new "observed but not yet measured" section for the straight-line question; milestone trail and next actions updated |
| `tests/README.md` | Entry 7 marked as the ground-drive test; wheels-lifted/ground split stated; the stale "awaits a run" boundary removed |
| `docs/wiring.md` | Turn-row boundary rewritten: both the pin combination and the stick region are now confirmed |
| `docs/hardware.md` | New verified-behavior section for the August 16 ground drive |
| `docs/setup.md` | Driving status updated with ground drive and the unmeasured straight-line item |
| `docs/roadmap.md` | Ground drive checked off with its conditions; straight-line measurement added as a new open item; closing summary corrected |
| `tests/rover_pins.py` | `turn_left()` / `turn_right()` docstrings updated |
| `tests/test_gamepad_all_motors.py` | Module docstring updated; ground-drive status and a run-in-the-air-first warning added |

The August 10 devlog was deliberately left untouched. It is an accurate record of
what was true on August 10, including its correct statement that turning was
implemented but not yet verified. A log is a record of a day, not a live status
page.

### Empty scaffolding removed

Eleven directories existed containing nothing but a `.gitkeep`: six under `src/`,
plus `scripts/`, `references/`, `hardware/datasheets/`, `hardware/diagrams/`, and
five topic folders under `notes/`. They were created on day one as a plan.

A repository whose stated principle is *document what physically happened* should
not ship a `src/vision/` before it has a camera. The folders were removed and will
be created when there is something to put in them. The README's repository map was
already drawn without them, so the map is now accurate as written.

### What this audit is worth

Finding that your own documentation understated your work is a more useful
outcome than finding it overstated it, but only slightly — both are the same
defect, which is that the record and the machine were allowed to drift apart. The
fix is procedural, not textual: **write the session up before leaving the bench.**

---

## 中文

### 最重要的一处发现

8 月 16 日的开发日志开头写着：

> 所有改动都没有在实车上重新运行，因此一律记为"已实现、未验证"。

而同一个文件的后半部分有整整一节"当天的验证测试"，表格里每一行都是通过。

开头那段写于上车验证之前，验证完成后没有回头修改。于是仓库里最重要的一篇日志，连续
两天以否定自己的实测结果开场——而那恰恰是读者最先看到的一段。

**教训：** 分两次写成的文档，提交前必须重读第一次写的部分。问题不在于写了假话，而在于
下午两点为真的句子被晚上八点原样提交了。

### 地面行驶从来没被记录

README、`docs/hardware.md`、`docs/wiring.md`、`docs/setup.md`、`docs/roadmap.md`、
`tests/README.md` 和 8 月 16 日的日志，所有关于当天验证的描述都写着"四轮架空"。而
"从架空测试过渡到受控的地面行驶"这一条，同时出现在三份待办清单里。

但它已经完成了。8 月 16 日第 1 到第 6 项确实是架空运行的，随后
`test_gamepad_all_motors.py` 在**地面**上运行：室内木地板、30% PWM、连续约 10 分钟。
前进、后退、停止和左右原地转在地面上的表现与架空一致，真实摩擦下小车能干脆地原地旋转。
而断线安全停车——行驶中关闭手柄电源——也是在地面上触发的，小车承载自身重量、带着真实
惯性，不是四个轮子在空中空转。

最后这一点是整个项目目前最有分量的安全成果，而仓库把它记成了较弱的那一种。

**教训：** 造成转向日期丢失的，和造成这次的是同一个习惯。如果一次实测在收工前没有写完，
记录就会向上一次的说法漂移。先测，再写，同一次坐下来完成。

### "没跑偏"是什么，不是什么

10 分钟的行驶中没有观察到跑偏。这条观察已经记录下来了——并且明确划了边界。

全程有人在打方向。人握着摇杆时会在毫无察觉的情况下修正缓慢的偏移，也就是说闭环是驾驶员
完成的，不是机器完成的。"有人驾驶时没看到跑偏"不等于"开环能走直线"。

要得到真正的结论需要一次专门的测试：固定距离、保持前进命令、不做任何修正，并**测量**
横向偏移而不是靠肉眼判断。这条现在已列入第一阶段。它的结果决定了第三阶段上 PID 的理由，
有多少落在直线性上、有多少落在里程计和可重复距离上——在围绕它建立论证之前，值得先知道
答案。

### 代码里的过期注释

`rover_pins.py` 里 `turn_left()` 和 `turn_right()` 仍写着"等待确认性实跑"，
`test_gamepad_all_motors.py` 的模块 docstring 把 8 月 16 日的三项改动全部列为未验证。
两处都写于 16 号上午，到当天傍晚就已经过期。

在 docstring 里携带验证状态是有价值的——状态就紧挨着它所描述的引脚数值。但它和文档一样
会过期，而且更容易被忘记，因为这些文件通常是被打开来"运行"的，不是被打开来"读"的。

### 已完成的修正

| 文件 | 修正内容 |
|---|---|
| `docs/devlog/2026-08-16-...md` | 修正开头段落；验证表补入地面行驶及其细节；保留一条说明记录原文写过什么 |
| `README.md` | 中英状态表各增"地面行驶"一行；转向与断线停车行写具体；测试表注释更正为排除 `test_gamepad_motor_left.py`；验证边界补入地面行驶结果；新增"观察到但尚未测量"一节；更新里程碑轨迹与下一步 |
| `tests/README.md` | 第 7 项标记为地面测试；写明架空/地面的分界；删除过期的"待实跑"边界说明 |
| `docs/wiring.md` | 重写转向行的验证边界：引脚组合与摇杆区域现均已确认 |
| `docs/hardware.md` | 新增 8 月 16 日地面行驶的已验证行为一节 |
| `docs/setup.md` | 驾驶状态补入地面行驶与尚未测量的直线性 |
| `docs/roadmap.md` | 勾选地面行驶并附条件；新增开环直线性测量为待办项；更正结尾总结 |
| `tests/rover_pins.py` | 更新 `turn_left()` / `turn_right()` docstring |
| `tests/test_gamepad_all_motors.py` | 更新模块 docstring；补入地面验证状态与"改动后先架空再落地"的提醒 |

8 月 10 日的日志刻意不动。它准确记录了 8 月 10 日的真实情况，包括当时正确写下的"转向
已实现、尚未实测"。日志是某一天的记录，不是实时状态页。

### 删除空脚手架

有 11 个目录里只有一个 `.gitkeep`：`src/` 下六个，加上 `scripts/`、`references/`、
`hardware/datasheets/`、`hardware/diagrams/`，以及 `notes/` 下五个主题文件夹。它们是
第一天作为计划建出来的。

一个把"只记录物理上真正发生的事"写进原则的仓库，不应该在还没有摄像头的时候就先摆一个
`src/vision/`。这些目录已删除，等真有东西要放进去时再建。README 的仓库结构图本来就没有
画它们，所以现在结构图与实际完全一致。

### 这次校对的价值

发现自己的文档**低估**了自己的工作，比发现它高估了要好一点，但也只好一点点——两者是同一个
缺陷：记录和机器之间被允许产生了漂移。修复方式是流程上的，不是文字上的：
**离开工作台之前，把这次实测写完。**
