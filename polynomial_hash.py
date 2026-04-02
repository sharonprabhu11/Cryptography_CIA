BASE = 31             # Prime base for the polynomial
MOD  = 2**61 - 1      # Mersenne prime modulus (~2.3 * 10^18 possible outputs)


def polynomial_hash(text: str) -> str:
    hash_value = 0

    for char in text:
        # Horner's method — one step:
        #   hash_value = hash_value * BASE + ASCII(char)   (mod MOD)
        #
        # This is mathematically equivalent to evaluating the polynomial
        #   c[0]*BASE^(n-1) + c[1]*BASE^(n-2) + ... + c[n-1]
        # but without ever computing a large power of BASE directly.
        hash_value = (hash_value * BASE + ord(char)) % MOD

    return hex(hash_value)


def verify_integrity(original_hash: str, text: str) -> bool:
    return polynomial_hash(text) == original_hash