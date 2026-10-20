# Investigative Reversing 1 — Write-up

## 1. Image Forensics

Identify the provided files:

```bash
file investigative-reversing-1-mystery
file investigative-reversing-1-mystery.png
file investigative-reversing-1-mystery2.png
file investigative-reversing-1-mystery3.png
```

Check the PNG structures:

```bash
pngcheck -v investigative-reversing-1-mystery.png
pngcheck -v investigative-reversing-1-mystery2.png
pngcheck -v investigative-reversing-1-mystery3.png
```

Look for additional data after the PNG `IEND` chunks:

```bash
xxd investigative-reversing-1-mystery.png | tail
xxd investigative-reversing-1-mystery2.png | tail
xxd investigative-reversing-1-mystery3.png | tail
```

Extract the trailing data from each image:

```bash
python3 -c "from pathlib import Path; [(lambda d: print(d[d.index(b'IEND')+8:]))(Path(f).read_bytes()) for f in ['investigative-reversing-1-mystery.png','investigative-reversing-1-mystery2.png','investigative-reversing-1-mystery3.png']]"
```

The trailing bytes contain fragments of the hidden flag. These fragments must be mapped back to their original positions.

## 2. Analyze the Binary Using Rizin

Open and analyze the executable:

```bash
rizin -A investigative-reversing-1-mystery
```

List the discovered functions and inspect `main`:

```text
afl
s main
pdg
```

Inspect the assembly:

```text
pdf
```

The decompiled code shows that the program reads 26 bytes from `flag.txt` and distributes selected bytes across three PNG files.

## 3. Identify the Byte Transformations

The program opens the files using `fopen()` and writes individual bytes using `fputc()`.

The output mapping is:

| Input byte indices | Output file | Operation |
|---|---|---|
| 0 | `mystery3.png` | Unchanged |
| 0 | `mystery2.png` | Add `0x15` (21) |
| 2 | `mystery3.png` | Unchanged |
| 5 | `mystery3.png` | Unchanged |
| 4 | `mystery.png` | Unchanged |
| 6–9 | `mystery.png` | Unchanged |
| 3 | `mystery2.png` | Add 4 |
| 10–14 | `mystery3.png` | Unchanged |
| 15–25 | `mystery.png` | Unchanged |

The program does not write every input byte to the output images. For example, byte 1 is not written, while byte 0 is written twice, with one copy modified.

To reverse the transformations:

- Subtract `0x15` from the transformed copy of byte 0.
- Subtract 4 from the transformed value derived from byte 3.
- Place the remaining bytes at their original indices according to the decompiled mapping.

The files are opened in append mode (`"a"`), meaning repeated executions can append more data to the same files.

## 4. Write the Reverse Script

Create `reverse.py` to extract the trailing data from the three provided images and reconstruct the original 26-byte input.

```python
from pathlib import Path

base = Path(__file__).parent

def extract(name):
  data = (base / name).read_bytes()
  offset = data.index(b"IEND") + 8
  return data[offset:]

m1 = extract("investigative-reversing-1-mystery.png")
m2 = extract("investigative-reversing-1-mystery2.png")
m3 = extract("investigative-reversing-1-mystery3.png")

flag = bytearray(26)

i1 = i2 = i3 = 0

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

print(flag.decode(errors="replace"))
```

Run the script:

```bash
python3 reverse.py
```

The script extracts the appended bytes, reverses the two transformations, and places the recovered bytes back into their original positions.

## 5. Flag

The flag is the reconstructed string printed by `reverse.py`.

## Key Takeaways

- Use `file`, `pngcheck`, `xxd`, and `strings` for initial file forensics.
- PNG files can contain additional data after the `IEND` chunk.
- Reverse byte transformations using inverse arithmetic.
- Reconstruct scattered data using the binary's actual write order.
- Be careful with append-mode file operations because repeated executions can change the output files.
