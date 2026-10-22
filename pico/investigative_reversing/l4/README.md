# Investigative Reversing 3 — Write-up

## 1. Image Forensics

Identify the provided files:

```bash
file investigative-reversing-3-mystery
file investigative-reversing-3-encoded.bmp
```

Inspect the BMP metadata and contents:

```bash
exiftool investigative-reversing-3-encoded.bmp
binwalk investigative-reversing-3-encoded.bmp
strings -a investigative-reversing-3-encoded.bmp
xxd -g 1 investigative-reversing-3-encoded.bmp | head
```

The encoded file is a BMP image. Since the challenge involves a BMP rather than a PNG, PNG-specific tools and searching for an `IEND` chunk are not applicable.

The likely approach is LSB steganography, where secret data is embedded in the least significant bits of image bytes.

## 2. Analyze the Binary Using Rizin

Open and analyze the executable:

```bash
rizin -A investigative-reversing-3-mystery
```

List the discovered functions:

```text
afl
```

Inspect `main()`:

```text
s main
pdg
```

Inspect `codedChar()`:

```text
s sym.codedChar
pdg
```

The decompiled `main()` reveals that the program opens `flag.txt`, `original.bmp`, and `encoded.bmp`.

It copies the first `0x2D3` bytes of the original image unchanged. Since `0x2D3` is 723 in decimal, the encoding begins at offset 723.

The program then reads 50 bytes from the flag and processes them in a loop.

## 3. Understand the Encoding

The `codedChar()` function is:

```c
uint8_t codedChar(unsigned long bit, int64_t character,
                  int64_t original)
{
    uint8_t value = (uint8_t)character;

    if (bit != 0)
    {
        value = (uint8_t)((int32_t)(char)value >> (bit & 0x1F));
    }

    return ((uint8_t)original & 0xFE) | (value & 1);
}
```

The function extracts a single bit from `character` and embeds it into the least significant bit of `original`.

- `value >> bit` shifts the selected bit into the least significant position.
- `value & 1` extracts that bit.
- `original & 0xFE` clears the original byte's least significant bit.
- `|` inserts the selected character bit into the original image byte.

The upper seven bits of each original image byte remain unchanged.

## 4. Identify the Encoded Region

The decompiled `main()` reveals the following file layout:

| Byte offsets | Size | Contents |
|:---|---:|:---|
| `0–722` | 723 bytes | Original BMP data, copied unchanged |
| `723–1122` | 400 bytes | Bytes containing the encoded flag bits |
| `1123–1172` | 50 bytes | Unchanged image bytes interleaved with the encoding |
| `1173` onward | Remaining bytes | Original BMP data, copied unchanged |

The encoding loop runs 100 iterations. On every even iteration, it encodes one flag character using eight consecutive image bytes. On every odd iteration, it copies one image byte unchanged.

Therefore, each character occupies nine bytes in the output: eight bytes containing its encoded bits, followed by one unchanged byte.

The total size of the processed region after the initial 723 bytes is:

\[
50 \times (8 + 1) = 450 \text{ bytes}
\]

The first encoded character begins at offset 723. After extracting eight bits, the decoder must skip one byte before processing the next character.

## 5. Write the Reverse Script

Create `reverse.py`:

```python
from pathlib import Path

image = Path(__file__).parent / "investigative-reversing-3-encoded.bmp"
data = image.read_bytes()

offset = 0x2D3
flag = bytearray()

for _ in range(50):
    value = 0

    for bit in range(8):
        value |= (data[offset] & 1) << bit
        offset += 1

    flag.append(value)
    offset += 1  # Skip the unchanged image byte

print(flag.decode(errors="replace"))
```

Run the script:

```bash
python3 reverse.py
```

The script skips the initial 723 bytes, extracts the least significant bit from each of the next eight bytes, and reconstructs one character in least-significant-bit-first order. It then skips the unchanged byte and repeats the process for all 50 characters.

The provided decompilation does not show a subtraction of 5 before `codedChar()` is called, so the script does not add 5 during decoding.

## 6. Flag

The flag is the reconstructed string printed by `reverse.py`.

## Key Takeaways

- Use `file`, `exiftool`, `binwalk`, and `xxd` to inspect unfamiliar image files.
- LSB steganography hides information by modifying only the least significant bit of each byte.
- Carefully inspect loop conditions to identify interleaved bytes that must be skipped during decoding.
- Reconstruct bits in the same order used by the encoding function.
