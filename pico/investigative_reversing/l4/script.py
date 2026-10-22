from pathlib import Path

data = Path("investigative-reversing-3-encoded.bmp").read_bytes()

offset = 0x2D3
flag = bytearray()

for _ in range(50):
    value = 0

    for bit in range(8):
        value |= (data[offset] & 1) << bit
        offset += 1

    flag.append(value)
    offset += 1

print(flag.decode(errors="replace"))
