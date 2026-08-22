#!/usr/bin/env python3
"""
lidar_live.py - 阶段 A4：实时显示距离，用于边界条件测试。

按已确认的帧结构解析并连续刷新：
  帧头 10 字节 (AA AA AA AA 00 02 00 00 B8 00)
  12 个点 x 15 字节，点内 = 距离u16 噪声u16 峰值u32 置信u8 积分u32 参考u16
  时间戳 4 字节 + 校验 1 字节

只读取和显示，不控制电机。Ctrl+C 退出。

用法: python3 lidar_live.py [端口]
"""

import struct
import sys
import time

import serial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD = 230400

SYNC = b"\xAA\xAA\xAA\xAA"
FRAME_LEN = 195
POINT_OFF = 10
POINT_LEN = 15
POINTS = 12
POINT_FMT = "<HHIBIH"          # 距离 噪声 峰值 置信 积分 参考 = 15 字节

REFRESH = 0.2                  # 屏幕刷新间隔（秒）


def parse_frame(frame):
    """把一帧的 12 个点解析成 dict 列表。"""
    pts = []
    for k in range(POINTS):
        off = POINT_OFF + k * POINT_LEN
        dist, noise, peak, conf, intg, reftof = struct.unpack(
            POINT_FMT, frame[off:off + POINT_LEN])
        pts.append({"dist": dist, "noise": noise, "peak": peak,
                    "conf": conf, "intg": intg, "reftof": reftof})
    return pts


def median(vals):
    s = sorted(vals)
    n = len(s)
    if n == 0:
        return 0
    mid = n // 2
    return s[mid] if n % 2 else (s[mid - 1] + s[mid]) // 2


try:
    ser = serial.Serial(PORT, BAUD, timeout=0.05)
except serial.SerialException as exc:
    print(f"打不开 {PORT}: {exc}")
    sys.exit(1)

print(f"{PORT} @ {BAUD}  —  Ctrl+C 退出\n")
print("  距离(中位)   范围        零值   置信  噪声   参考   帧率")
print("  " + "-" * 62)

ser.reset_input_buffer()
buf = bytearray()
last_pts = None
frame_count = 0
total_frames = 0
last_refresh = time.monotonic()
t_start = last_refresh

try:
    while True:
        chunk = ser.read(4096)
        if chunk:
            buf.extend(chunk)

        # 按帧头切帧
        while True:
            i = buf.find(SYNC)
            if i == -1:
                if len(buf) > 4 * FRAME_LEN:
                    del buf[:-4]          # 没帧头就只留尾巴，防止无限增长
                break
            if len(buf) - i < FRAME_LEN:
                del buf[:i]               # 帧不完整，等下一批
                break
            last_pts = parse_frame(buf[i:i + FRAME_LEN])
            frame_count += 1
            total_frames += 1
            del buf[:i + FRAME_LEN]

        now = time.monotonic()
        if now - last_refresh >= REFRESH and last_pts:
            hz = frame_count / (now - last_refresh)
            frame_count = 0
            last_refresh = now

            dists = [p["dist"] for p in last_pts]
            good = [d for d in dists if d > 0]
            zeros = len(dists) - len(good)

            med = median(good) if good else 0
            lo = min(good) if good else 0
            hi = max(good) if good else 0
            conf = min(p["conf"] for p in last_pts)
            noise = median([p["noise"] for p in last_pts])
            reftof = median([p["reftof"] for p in last_pts])

            line = (f"  {med:6d} mm   {lo:5d}..{hi:<5d}  "
                    f"{zeros:2d}/12   {conf:3d}  {noise:4d}  "
                    f"{reftof:5d}  {hz:4.1f}Hz")
            print("\r" + line, end="", flush=True)

except KeyboardInterrupt:
    elapsed = time.monotonic() - t_start
    print(f"\n\n共 {total_frames} 帧 / {elapsed:.1f}s "
          f"= {total_frames / elapsed:.1f} 帧每秒")
finally:
    ser.close()
