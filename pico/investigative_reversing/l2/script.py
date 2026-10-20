
from pathlib import Path

def extract(name):
  data = (Path(__file__).parent / name).read_bytes()
  offset = data.index(b"IEND") + 8
  return data[offset:]

m1 = extract("investigative-reversing-1-mystery.png")
m2 = extract("investigative-reversing-1-mystery2.png")
m3 = extract("investigative-reversing-1-mystery3.png")

flag = bytearray(26)

i1 = i2 = i3 = 0

flag[1] = m3[i3]
i3 += 1

flag[0] = (m2[i2] - 0x15) & 0xff
i2 += 1

flag[2] = m3[i3]
i3 += 1

flag[5] = m3[i3]
i3 += 1

flag[4] = m1[i1]
i1 += 1

for i in range(6, 10):
  flag[i] = m1[i1]
  i1 += 1

flag[3] = (m2[i2] - 4) & 0xff
i2 += 1

for i in range(10, 15):
  flag[i] = m3[i3]
  i3 += 1

for i in range(15, 26):
  flag[i] = m1[i1]
  i1 += 1

print(flag.decode())
