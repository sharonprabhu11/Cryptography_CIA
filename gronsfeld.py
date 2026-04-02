
def validate_key(key: str) -> None:
    if not key:
        raise ValueError("Key cannot be empty.")
    if not key.isdigit():
        raise ValueError(f"Key must contain digits only (0-9). Got: '{key}'")


def extend_key(key: str, length: int) -> list:
    repeated = (key * ((length // len(key)) + 1))[:length]
    return [int(digit) for digit in repeated]


def encrypt(plaintext: str, key: str) -> str:
    validate_key(key)
    extended_key = extend_key(key, len(plaintext))

    cipher_chars = []
    for i, char in enumerate(plaintext):
        plain_ascii  = ord(char)                        # character -> ASCII number
        key_digit    = extended_key[i]                  # digit at this position
        cipher_ascii = (plain_ascii + key_digit) % 256  # shift forward, wrap at 256
        cipher_chars.append(chr(cipher_ascii))          # ASCII number -> character

    return "".join(cipher_chars)


def decrypt(ciphertext: str, key: str) -> str:
    validate_key(key)
    extended_key = extend_key(key, len(ciphertext))

    plain_chars = []
    for i, char in enumerate(ciphertext):
        cipher_ascii = ord(char)                         # character -> ASCII number
        key_digit    = extended_key[i]                   # digit at this position
        plain_ascii  = (cipher_ascii - key_digit) % 256  # shift backward, wrap at 256
        plain_chars.append(chr(plain_ascii))             # ASCII number -> character

    return "".join(plain_chars)