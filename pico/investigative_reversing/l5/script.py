from pathlib import Path

flag = bytearray()

for i in range(5, 0, -1):
    filename = Path(f"Item{i:02d}_cp.bmp")
    data = filename.read_bytes()
    offset = 0x7E3

    for j in range(50):
        if j % 5 == 0:
            char = 0

            for bit in range(8):
                char |= (data[offset] & 1) << bit
                offset += 1

            flag.append(char)
        else:
            offset += 1

print(flag)
print(flag.decode(errors="replace"))
