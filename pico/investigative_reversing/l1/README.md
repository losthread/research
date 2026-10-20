# Investigative Reversing 0 — Write-up

## 1. Image Forensics

Identify the provided files:

```bash
  file investigative-reversing-0-mystery
  file investigative-reversing-0-mystery.png
```

Check the PNG structure:

```bash
  pngcheck -v investigative-reversing-0-mystery.png
```

The output reports additional data after the `IEND` chunk, indicating that data exists beyond the normal PNG structure.

Inspect the file's hexadecimal contents:

```bash
  xxd investigative-reversing-0-mystery.png | tail
```

Search for readable strings:

```bash
  strings investigative-reversing-0-mystery.png
```

Extract the bytes following the PNG's `IEND` chunk:

```bash
  python3 -c "d=open('investigative-reversing-0-mystery.png','rb').read(); print(repr(d[d.index(b'IEND')+8:]))"
```

Output:

```text
  b'academ~\x80k5zsid6q_aeebde6b}'
```

The data is encoded, so further analysis is required to recover the flag.

## 2. Prepare the Input

Save the extracted bytes to `flag.txt`:

```bash
  printf 'academ~\200k5zsid6q_aeebde6b}' > flag.txt
```

The `\200` escape represents the byte `0x80`.

## 3. Decompile the Binary Using Rizin ghidra

Open and analyze the executable:

```bash
  rizin -A investigative-reversing-0-mystery
  afl
  s main
  pdg
```
The decompiled code reveals that the program opens `flag.txt`, reads its contents, transforms selected bytes, and appends the result to `mystery.png`.

## 4. Disassemble and Identify the Transformation

Inspect the assembly for `main`:

```text
  pdf
```

The instructions reveal the following byte transformation:

| Byte indices  |      Operation     |
|---------------|--------------------|
| 0–5           | Unchanged          |
| 6–14          | Add 5 to each byte |
| 15            | Subtract 3         |
| 16 onward     | Unchanged          |

The program opens `mystery.png` in append mode (`"a"`), so each execution appends transformed data instead of replacing the file.

To recover the flag, reverse the transformation:

- Subtract 5 from bytes at indices 6–14.
- Add 3 to the byte at index 15.
- Leave all other bytes unchanged.

## 5. Write the Reverse Script

Create `script.py`:

```python
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
```

Run the script:

```bash
  python3 script.py
```

The script extracts the data following `IEND` and applies the inverse transformation to recover the flag.

## 6. Flag

```text
  academy{f0und_1t_aeebde6b}
```

## Key Takeaways

- Use `file`, `pngcheck`, `xxd`, and `strings` for initial file forensics.
- PNG files can contain data after the `IEND` chunk.
- Reverse byte transformations by applying their inverse operations.
- Be careful when running programs that open files in append mode.
```
