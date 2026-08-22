#!/usr/bin/env python3
"""
lidar_raw_dump.py - 激光模组第一步：证明字节能收到。

只做一件事：以 230400 8N1 打开串口，采集 N 秒原始字节，
存成文件并打印前 256 字节的十六进制。不解析，不控制电机。

用法:  python3 lidar_raw_dump.py [端口]
默认端口 /dev/ttyACM0
"""

import sys
import time
import serial
from serial.tools import list_ports

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyACM0"
BAUD = 230400
SECONDS = 2.0
OUTFILE = "lidar_raw.bin"


def list_available():
    ports = list(list_ports.comports())
    if not ports:
        print("  (系统里一个串口都没有)")
        return
    for p in ports:
        print(f"  {p.device}  |  {p.description}")


try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
except serial.SerialException as exc:
    print(f"打不开 {PORT}: {exc}\n")
    print("当前可用串口：")
    list_available()
    sys.exit(1)

print(f"{PORT} @ {BAUD} 8N1，采集 {SECONDS}s ...")

ser.reset_input_buffer()
buf = bytearray()
t0 = time.monotonic()
while time.monotonic() - t0 < SECONDS:
    chunk = ser.read(4096)
    if chunk:
        buf.extend(chunk)
elapsed = time.monotonic() - t0
ser.close()

if not buf:
    print("一个字节都没收到。可能原因：波特率不对、TX/RX 接反、模组没供电。")
    sys.exit(2)

with open(OUTFILE, "wb") as f:
    f.write(buf)

rate = len(buf) / elapsed
print(f"收到 {len(buf)} 字节 / {elapsed:.2f}s = {rate:.0f} 字节/秒")
print(f"若采样率为 120 Hz，则一帧约 {rate / 120:.1f} 字节")
print(f"原始数据已存到 {OUTFILE}\n")

print("前 256 字节：")
head = buf[:256]
for i in range(0, len(head), 16):
    row = head[i:i + 16]
    print(f"{i:04X}  " + " ".join(f"{b:02X}" for b in row))
