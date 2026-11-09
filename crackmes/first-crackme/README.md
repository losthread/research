# agigatorx's Simple Easy CrackMe — Writeup

**Tools:** Rizin (with rz-ghidra plugin) 
**Method:** Static analysis (no patching)

## Steps

```bash
rizin -A <filename>
afl
s main
pdg
```

In `main`, the input check used a `switch` statement. Reading the `case` branches in order revealed the expected character sequence.

## Password

```text
<password>
```

## Result

The CrackMe accepts `<password>`. Solved statically; no patch needed.
