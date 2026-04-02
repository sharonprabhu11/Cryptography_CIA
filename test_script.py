"""
test_script.py
==============
Demonstrates the full encrypt -> hash -> decrypt round-trip
for the Gronsfeld cipher with the polynomial hash function.

Covers:
  - 2 worked examples with plaintext, key, ciphertext, and hash output
  - A tampering simulation showing the hash catching corruption
  - Edge cases: single character, long key, key shorter than plaintext
"""

from gronsfeld       import encrypt, decrypt
from polynomial_hash import polynomial_hash, verify_integrity

def separator(title: str = ""):
    line = "=" * 60
    if title:
        print(f"\n{line}")
        print(f"  {title}")
        print(line)
    else:
        print(line)


def show_round_trip(label: str, plaintext: str, key: str):
    print(f"\n  Plaintext  : {plaintext!r}")
    print(f"  Key        : {key!r}")

    # Step 1: Hash the plaintext BEFORE encryption
    # This fingerprints the original message so we can verify it later.
    original_hash = polynomial_hash(plaintext)
    print(f"\n  [1] Hash plaintext (before encryption)")
    print(f"      polynomial_hash -> {original_hash}")

    # Step 2: Encrypt
    ciphertext = encrypt(plaintext, key) 
    print(f"\n  [2] Encrypt")
    print(f"      Ciphertext -> {ciphertext!r}")
    print(f"      ASCII vals -> {[ord(c) for c in ciphertext]}")

    # Step 3: Decrypt (simulating the receiver's side)
    recovered = decrypt(ciphertext, key)
    print(f"\n  [3] Decrypt")
    print(f"      Recovered  -> {recovered!r}")

    # Step 4: Verify integrity — hash the recovered text, compare to original
    intact = verify_integrity(original_hash, recovered)
    status = "PASS - message is intact" if intact else "FAIL - message was altered"
    print(f"\n  [4] Integrity check")
    print(f"      polynomial_hash(recovered) == original_hash -> {status}")

    # Confirm full round-trip
    match = plaintext == recovered
    print(f"\n  Round-trip match: {'YES' if match else 'NO'}")

separator("EXAMPLE 1: UNIVERSITY / key=123456  (from the paper)")
show_round_trip(
    label     = "Example 1",
    plaintext = "UNIVERSITY",
    key       = "123456"
)

separator("EXAMPLE 2: Mixed characters / key=9031")
show_round_trip(
    label     = "Example 2",
    plaintext = "Hello, World!",
    key       = "9031"
)

# TAMPERING SIMULATION
# Shows the hash catching a modification to the ciphertext.
# Without hashing, the receiver would get a corrupted message with no warning.

separator("TAMPERING SIMULATION")

plaintext = "UNIVERSITY"
key       = "123456"

original_hash = polynomial_hash(plaintext)
ciphertext    = encrypt(plaintext, key)

# Simulate an attacker flipping the last byte of the ciphertext
tampered = ciphertext[:-1] + chr((ord(ciphertext[-1]) + 1) % 256)

print(f"\n  Original ciphertext : {ciphertext!r}")
print(f"  Tampered ciphertext : {tampered!r}  (last byte changed by +1)")

tampered_recovered = decrypt(tampered, key)
print(f"\n  Decrypted (tampered): {tampered_recovered!r}")

caught = not verify_integrity(original_hash, tampered_recovered)
print(f"  Integrity check     : {'FAIL - tampering detected!' if caught else 'PASS (tampering missed)'}")


separator("EDGE CASES")

# Case 1: Key longer than plaintext
print("\n  [A] Key longer than plaintext")
pt  = "HI"
k   = "9999999"
ct  = encrypt(pt, k)
rec = decrypt(ct, k)
print(f"      plaintext={pt!r}  key={k!r}")
print(f"      ciphertext={ct!r}  recovered={rec!r}  match={pt == rec}")

# Case 2: Key of length 1 (same shift applied to every character)
print("\n  [B] Single-digit key (same shift repeated)")
pt  = "HELLO"
k   = "3"
ct  = encrypt(pt, k)
rec = decrypt(ct, k)
print(f"      plaintext={pt!r}  key={k!r}")
print(f"      ciphertext={ct!r}  recovered={rec!r}  match={pt == rec}")

# Case 3: Key digit 0 (no shift — ciphertext should equal plaintext)
print("\n  [C] Key of all zeros (shift = 0, ciphertext equals plaintext)")
pt  = "TEST"
k   = "0000"
ct  = encrypt(pt, k)
rec = decrypt(ct, k)
print(f"      plaintext={pt!r}  key={k!r}")
print(f"      ciphertext={ct!r}  recovered={rec!r}  match={pt == rec}")

# Case 4: Non-alphabetic characters
print("\n  [D] Special characters and digits in plaintext")
pt  = "P@55w0rd!"
k   = "42"
ct  = encrypt(pt, k)
rec = decrypt(ct, k)
print(f"      plaintext={pt!r}  key={k!r}")
print(f"      ciphertext={ct!r}  recovered={rec!r}  match={pt == rec}")

separator()
print("  All tests complete.")
separator()