from pathlib import Path

png = Path(__file__).parent / "investigative-reversing-0-mystery.png"
data = png.read_bytes()

offset = data.index(b"IEND") + 8
flag = bytearray(data[offset:])

if len(flag) < 16:
  raise ValueError("Not enough trailing data to decode")

for i in range(6, 15):
  flag[i] = (flag[i] - 5) % 256

flag[15] = (flag[15] + 3) % 256

print(flag.decode())
