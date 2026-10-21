with open("investigative-reversing-2-encoded.bmp", "rb") as f:
    f.seek(2000)
    data = f.read(400)

flag = ""

for i in range(0, 400, 8):
    value = 0

    for bit in range(8):
        value |= (data[i + bit] & 1) << bit

    flag += chr(value + 5)

print(flag)
