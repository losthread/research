# Investigative Reversing 2 — Write-up

## 1. Image Forensics

Identify the provided files:

```bash
file investigative-reversing-2-mystery
file investigative-reversing-2-encoded.bmp
```

Inspect the BMP metadata and contents:

```bash
exiftool investigative-reversing-2-encoded.bmp
binwalk investigative-reversing-2-encoded.bmp
strings -a investigative-reversing-2-encoded.bmp
xxd -g 1 investigative-reversing-2-encoded.bmp | head
```

Unlike the previous challenge, the image is a BMP rather than a PNG. Therefore, `pngcheck` and searching for a PNG `IEND` chunk are not applicable.

The challenge hints at LSB encoding, suggesting that the hidden flag is embedded in the least significant bits of the image bytes.

## 2. Analyze the Binary Using Rizin

Open and analyze the executable:

```bash
rizin -A investigative-reversing-2-mystery
```

List the discovered functions and inspect `main`:

```text
afl
s main
pdg
```

Inspect the `codedChar` function:

```text
pdf @ sym.codedChar
```

The decompiled `main()` reveals that the program opens `flag.txt`, `original.bmp`, and `encoded.bmp`.

It first copies 2,000 bytes from `original.bmp` unchanged. It then reads 50 bytes from the flag and encodes each character into eight consecutive BMP bytes.

## 3. Understand the Encoding

The `codedChar()` function is:

```c
uint8_t codedChar(unsigned long bit, int64_t character,
                  int64_t original)
{
  uint8_t value = (uint8_t)character;

  if (bit != 0)
  {
    value = (uint8_t)((int8_t)value >> (bit & 0x1F));
  }

  return ((uint8_t)original & 0xFE) | (value & 1);
}
```

The program first subtracts 5 from each flag character:

```c
character = flag[i] - 5;
```

It then extracts individual bits from the transformed character and embeds them into the least significant bits of consecutive BMP bytes.

The encoding works as follows:

- `value >> bit` shifts the selected bit to the least significant position.
- `value & 1` extracts that bit.
- `original & 0xFE` clears the original byte's least significant bit.
- `|` inserts the extracted flag bit into the original image byte.

Each encoded byte retains its original upper seven bits, so the modification is minimal.

## 4. Identify the Encoded Region

The relevant loops in `main()` establish the file layout:

| Byte offsets | Contents |
|---|---|
| 0–1999 | Original BMP data, unchanged |
| 2000–2399 | Encoded flag data |
| 2400 onward | Remaining original BMP data, unchanged |

The first 2,000 bytes are copied directly. Encoding starts at offset 2000.

Since the program encodes 50 characters using eight bits per character, the encoded region contains:

\[
50 \times 8 = 400 \text{ bytes}
\]

The flag can therefore be extracted by reading the least significant bit of each of those 400 bytes.

## 5. Write the Reverse Script

Create `reverse.py`:

```python
from pathlib import Path

base = Path(__file__).parent
image = base / "investigative-reversing-2-encoded.bmp"

with image.open("rb") as f:
  f.seek(2000)
  data = f.read(400)

if len(data) != 400:
  raise ValueError("Encoded region is incomplete")

flag = bytearray()

for i in range(0, 400, 8):
  value = 0

  for bit in range(8):
    value |= (data[i + bit] & 1) << bit

  flag.append((value + 5) & 0xff)

print(flag.decode(errors="replace"))
```

Run the script:

```bash
python3 reverse.py
```

The script skips the first 2,000 bytes, extracts the LSB from each subsequent byte, reconstructs each character in least-significant-bit-first order, and adds 5 to reverse the original transformation.

## 6. Flag

The flag is the reconstructed string printed by `reverse.py`.

## Key Takeaways

- Use `file`, `exiftool`, `binwalk`, and `xxd` to inspect unfamiliar image formats.
- PNG-specific tools and chunk structures do not apply to BMP files.
- LSB steganography can hide data by changing only the least significant bit of each byte.
- Reverse engineering reveals the encoding offset, bit order, and character transformation.
- Reversing an encoding requires undoing every transformation in the correct order.
