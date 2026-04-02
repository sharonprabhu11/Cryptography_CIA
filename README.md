# Gronsfeld Cipher with Polynomial Hash

Implementation of the Gronsfeld cipher with a custom polynomial hash function for integrity verification. Written in Python with no external or cryptography libraries.

---

## Files

| File | Purpose |
|---|---|
| `gronsfeld.py` | Encryption and decryption |
| `polynomial_hash.py` | Custom polynomial hash function |
| `test_script.py` | Full encrypt → hash → decrypt round-trip tests |

---

## How to Run

Requires Python 3.10 or later (for the `tuple[int, float]` type hint syntax). No pip installs needed.

```bash
python test_script.py
```

---

## Theory: The Gronsfeld Cipher

The Gronsfeld cipher is a **polyalphabetic substitution cipher** — a variant of the Vigenère cipher where the key is a sequence of digits (0–9) rather than letters.

### How it works

Each character in the plaintext is shifted by the ASCII value of the corresponding key digit. If the key is shorter than the plaintext, it repeats cyclically.

**Encryption:**
```
ciphertext[i] = (ASCII(plaintext[i]) + key_digit[i]) mod 256
```

**Decryption:**
```
plaintext[i] = (ASCII(ciphertext[i]) - key_digit[i]) mod 256
```

The `mod 256` operates over the full ASCII character set. This means any character — letters, digits, spaces, punctuation — can be encrypted and recovered correctly. The modulo on decryption also handles negative results: for example, `(2 - 5) mod 256 = 253`, which is a valid character rather than an error.

### Key behaviour

- Keys must contain only digits 0–9
- A key digit of `0` produces no shift (ciphertext character = plaintext character)
- A longer key increases security — more of the key is used before it repeats, making frequency analysis harder

---

## Theory: The Polynomial Hash Function

### Why a hash function at all?

The Gronsfeld cipher provides **confidentiality** — the ciphertext is unreadable without the key. But it provides no **integrity guarantee**. If someone intercepts and modifies the ciphertext, decryption still produces output — just corrupted output, with no indication that tampering occurred.

The hash function acts as a **fingerprint** of the original plaintext:

```
SENDER:   hash(plaintext) -> store hash
          encrypt(plaintext) -> send ciphertext

RECEIVER: decrypt(ciphertext) -> recovered
          hash(recovered) == stored hash?
          YES -> message is intact
          NO  -> message was tampered with
```

The hash is one-way — it cannot be reversed to recover the plaintext — so storing it alongside the ciphertext does not leak the original message.

### Why a polynomial hash?

The polynomial hash was chosen because:

1. **It can be implemented from scratch** — the algorithm is a loop of multiply-add operations with no internal tables, lookup arrays, or complex bitwise operations. Every step is mathematically explainable.

2. **Its design decisions are derivable from first principles** — the choice of base and modulus follows from number theory (explained below), not from memorising a standard.

3. **It satisfies the core requirements of a hash function** — deterministic, one-way, and sensitive to input changes.

### How the polynomial hash works

The input string is treated as a polynomial where each character is a coefficient, evaluated at the chosen base:

```
H = c[0]*base^(n-1) + c[1]*base^(n-2) + ... + c[n-1]*base^0   (mod p)
```

This is computed using **Horner's method** — an equivalent formulation that avoids computing large powers directly:

```
H = 0
for each character c in text:
    H = (H * base + ASCII(c)) mod p
```

Each step folds the running hash and adds the next character's contribution. A change at position `i` propagates through every multiplication that follows it.

### Parameter justification

**`base = 31`**  
A prime number. Prime bases reduce collision clustering because they share no common factors with the modulus, which improves the spread of hash values across the output space. 31 is a well-studied choice — it is the same base used in Java's `String.hashCode()`.

**`mod = 2^61 - 1`**  
This is a **Mersenne prime** — a prime of the form `2^p - 1`. Using a prime modulus ensures that hash outputs are evenly distributed across the output space (uniform distribution). The value `2^61 - 1 = 2,305,843,009,213,693,951` gives approximately `2.3 × 10^18` possible output values.

By the birthday paradox, collisions between distinct inputs become statistically likely only after roughly `sqrt(2^61) ≈ 2^30 ≈ 1 billion` inputs — far beyond any realistic use in this context.

### Known limitation

The avalanche effect is **position-dependent**: a change at the start of the string propagates through more multiplications than a change at the end, so it produces a larger change in the output. This is an inherent property of polynomial hashes. SHA-256 uses dedicated mixing rounds to eliminate this positional bias, at the cost of being much harder to implement from scratch.

---

## Worked Examples

### Example 1 — From the paper (UNIVERSITY / key 123456)

| Step | Value |
|---|---|
| Plaintext | `UNIVERSITY` |
| Key | `123456` |
| Extended key | `1 2 3 4 5 6 1 2 3 4` |
| Plaintext ASCII | `85 78 73 86 69 82 83 73 84 89` |
| Cipher ASCII | `86 80 76 90 74 88 84 75 87 93` |
| Ciphertext | `VPLZJXTKW]` |
| Hash of plaintext | `0x83a5f2832d68e` |
| Hash after decrypt | `0x83a5f2832d68e` |
| Integrity | PASS |

**Encryption step-by-step (first 3 characters):**

```
C[0] = (ASCII('U') + 1) mod 256 = (85 + 1) mod 256 = 86 = 'V'
C[1] = (ASCII('N') + 2) mod 256 = (78 + 2) mod 256 = 80 = 'P'
C[2] = (ASCII('I') + 3) mod 256 = (73 + 3) mod 256 = 76 = 'L'
...
```

---

### Example 2 — Mixed characters (Hello, World! / key 9031)

| Step | Value |
|---|---|
| Plaintext | `Hello, World!` |
| Key | `9031` |
| Extended key | `9 0 3 1 9 0 3 1 9 0 3 1 9` |
| Ciphertext | `Qeomx,#Xxroe*` |
| Hash of plaintext | `0x17eaa6435955b82e` |
| Hash after decrypt | `0x17eaa6435955b82e` |
| Integrity | PASS |

**Encryption step-by-step (first 3 characters):**

```
C[0] = (ASCII('H') + 9) mod 256 = (72  + 9) mod 256 = 81  = 'Q'
C[1] = (ASCII('e') + 0) mod 256 = (101 + 0) mod 256 = 101 = 'e'
C[2] = (ASCII('l') + 3) mod 256 = (108 + 3) mod 256 = 111 = 'o'
...
```

---

## Design Decisions

### Why split into three files?

- `gronsfeld.py` and `polynomial_hash.py` are **separate concerns** — encryption is about confidentiality, hashing is about integrity. Mixing them in one file would misrepresent what each layer does.
- `test_script.py` imports from both, representing the **pipeline** layer — where the two components are connected.

### Why `mod 256` for the cipher?

Using `mod 256` operates over the full extended ASCII range rather than just the 26 letters (`mod 26`). This allows any printable or non-printable character to be encrypted and recovered, making the cipher more general.

### Why return hex from the hash?

Hexadecimal gives a compact, consistent string representation of the integer hash value — conventional for cryptographic output and easy to store or compare as a string.