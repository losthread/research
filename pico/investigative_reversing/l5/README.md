# Investigative Reversing 4 — Write-up

## 1. Analyze the Binary Using Rizin

Open the executable and analyze its functions:

```bash
rizin -A investigative-reversing-4-mystery
```

List the discovered functions:

```text
afl
```

Decompile the four relevant functions:

```text
pdg @ main
pdg @ sym.codedChar
pdg @ sym.encodeAll
pdg @ sym.encodeDataInFile
```

These functions reveal how the program reads the flag, constructs filenames, and embeds flag data into bitmap images.

## 2. Understand the Functions

### `main()`

The main function opens `flag.txt`, reads up to 50 bytes into a buffer, initializes the flag index, and calls `encodeAll()`.

### `encodeAll()`

This function constructs numbered input and output filenames and calls `encodeDataInFile()` repeatedly. The loop iterates over the characters `'5'` down to `'1'`, processing five file pairs.

### `encodeDataInFile()`

This function opens an input image and an output image. It copies the first `0x7E3` bytes (2019 bytes) unchanged, then processes the following bytes according to the encoding loop. Selected iterations encode flag characters, while other iterations copy image bytes unchanged. Finally, it copies the remaining image data.

### `codedChar()`

This function embeds one bit of a flag character into the least significant bit (LSB) of an image byte.

```c
uint8_t codedChar(unsigned long bit, int64_t character,
                  int64_t image_byte)
{
    uint8_t value = (uint8_t)character;
    value >>= bit;

    return ((uint8_t)image_byte & 0xFE) | (value & 1);
}
```

The expression `image_byte & 0xFE` clears the byte's least significant bit. The expression `value & 1` extracts the selected flag bit, which is then inserted using the bitwise OR operator.

## 3. Understand the Encoding Pattern

Each flag character contains eight bits. The encoder extracts these bits individually and stores them in the LSBs of eight image bytes.

The encoding loop uses the condition:

```c
if (i % 5 == 0)
```

When the condition is true, the program encodes one flag character across eight image bytes. Otherwise, it copies an image byte unchanged.

The flag is therefore hidden in the bitmap's byte data rather than encrypted. Since only the least significant bit changes, the image generally looks unchanged to a person viewing it.

## 4. Identify the Encoded Region

The decompiled function establishes the following initial layout:

| Byte offsets | Contents |
| --- | --- |
| 0–2018 | Original image data copied unchanged |
| Starting at 2019 | Flag-encoding loop and unchanged bytes interleaved |
| After the encoding loop | Remaining image data copied unchanged |

Unlike a scheme that stores all encoded bits in one contiguous region, this implementation interleaves encoded and unchanged bytes. The extraction script must therefore reproduce the loop's byte-consumption pattern.

The program processes five numbered image pairs. The exact output filenames and the ordering of the hidden flag segments should be verified from the filename constants and the shared flag index in the decompilation.

## 5. Write the Extraction Script

Create `script.py` in the directory containing the supplied files:

```python
from pathlib import Path

base = Path(__file__).parent
flag = bytearray()

for i in range(5, 0, -1):
    image = base / f"Item{i:02d}_cp.bmp"
    data = image.read_bytes()
    offset = 0x7E3

    for j in range(50):
        if j % 5 == 0:
            value = 0

            for bit in range(8):
                value |= (data[offset] & 1) << bit
                offset += 1

            flag.append(value)
        else:
            offset += 1

print(flag.decode(errors="replace"))
```

Run the script:

```bash
python3 script.py
```

The script skips the initial 2019 bytes, extracts the LSBs from the selected image bytes, and reconstructs characters in least-significant-bit-first order.

**Note:** This script follows the loop pattern visible in the decompilation. Confirm the actual filename construction, per-file loop behavior, and shared `flag_index` before treating the output as the final flag. If the result is incorrect, inspect the exact byte-consumption logic and whether the flag index continues across image files.

## 6. Flag

The flag is the string recovered by running the extraction script. Verify that the output matches the expected picoCTF flag format.

## Key Takeaways

- LSB steganography hides information by modifying the least significant bit of image bytes.
- Eight image bytes encode one character when one bit is stored per byte.
- Interleaved unchanged bytes must be accounted for during extraction.
- Correctly reversing the encoding requires matching the original offsets, loop conditions, bit order, and file-processing order.
