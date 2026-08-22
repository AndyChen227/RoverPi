#!/usr/bin/env python3
"""
lidar_frame_probe.py - 第二步：验证帧结构，确认哪个字段是距离。

采集 1 秒，按 AA AA AA AA 切帧，打印帧长分布、单帧字节表，
以及两个候选距离字段的统计。不解析全部字段，不控制电机。

用法: python3 lidar_frame_probe.py [端口] [实测距离标注]
例:   python3 lidar_frame_probe.py /dev/ttyACM0 300mm
"""

import sys
import time
import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "(未标注)"

BAUD = 230400
SECONDS = 1.0
SYNC = b"\xAA\xAA\xAA\xAA"
HEADER_LEN = 8
POINT_LEN = 15
POINTS = 12
FRAME_LEN = 195


def u16(b, i):
    return b[i] | (b[i + 1] << 8)


ser = serial.Serial(PORT, BAUD, timeout=0.1)
ser.reset_input_buffer()
buf = bytearray()
t0 = time.monotonic()
while time.monotonic() - t0 < SECONDS:
    buf.extend(ser.read(4096))
ser.close()

starts = []
i = buf.find(SYNC)
while i != -1:
    starts.append(i)
    i = buf.find(SYNC, i + 1)

print(f"标注距离: {LABEL}")
print(f"收到 {len(buf)} 字节，找到 {len(starts)} 个帧头")

if len(starts) < 2:
    print("帧头不足两个，没法判断帧长。")
    sys.exit(1)

gaps = [b - a for a, b in zip(starts, starts[1:])]
counts = {g: gaps.count(g) for g in set(gaps)}
print(f"帧间隔统计: {counts}")

frames = [buf[s:s + FRAME_LEN] for s in starts
          if s + FRAME_LEN <= len(buf)]
print(f"完整帧数: {len(frames)}\n")

first = frames[0]
print(f"第一帧帧头 8 字节: {' '.join(f'{b:02X}' for b in first[:HEADER_LEN])}")
print(f"第一帧末尾 7 字节: "
      f"{' '.join(f'{b:02X}' for b in first[HEADER_LEN + POINTS * POINT_LEN:])}\n")

print("第一帧的 12 个点（每行 15 字节）:")
for k in range(POINTS):
    off = HEADER_LEN + k * POINT_LEN
    pt = first[off:off + POINT_LEN]
    a = u16(pt, 0)
    b = u16(pt, 2)
    print(f"  点{k:2d}  {' '.join(f'{x:02X}' for x in pt)}   A={a:5d}  B={b:5d}")

print()
a_all, b_all, a_p0 = [], [], []
for f in frames:
    for k in range(POINTS):
        off = HEADER_LEN + k * POINT_LEN
        pt = f[off:off + POINT_LEN]
        if k == 0:
            a_p0.append(u16(pt, 0))
        else:
            a_all.append(u16(pt, 0))
            b_all.append(u16(pt, 2))


def stat(name, vals):
    if not vals:
        return
    avg = sum(vals) / len(vals)
    print(f"  {name}: 均值 {avg:7.1f}  最小 {min(vals):5d}  "
          f"最大 {max(vals):5d}  极差 {max(vals) - min(vals):4d}  n={len(vals)}")


print("跨所有帧的统计（点 1-11）:")
stat("候选 A (点内偏移 0)", a_all)
stat("候选 B (点内偏移 2)", b_all)
print("点 0 单独看:")
stat("点 0 的候选 A     ", a_p0)
