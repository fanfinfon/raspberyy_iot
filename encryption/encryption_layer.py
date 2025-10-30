import os
from .present_cipher import Present80

DEFAULT_KEY = b'\x00' * 10  # default placeholder key

def _int_from_bytes(b: bytes) -> int:
    return int.from_bytes(b, byteorder='big')

def _int_to_bytes(i: int, length: int) -> bytes:
    return i.to_bytes(length, byteorder='big')

def encrypt_payload(plaintext: bytes, key: bytes = DEFAULT_KEY) -> bytes:
    """
    Encrypt arbitrary-length plaintext using PRESENT-80 in CTR mode.
    Output: nonce(8) || ciphertext
    """
    if not isinstance(plaintext, (bytes, bytearray)):
        raise TypeError("plaintext must be bytes")
    if len(key) != 10:
        raise ValueError("PRESENT-80 key must be 10 bytes")

    cipher = Present80(key)
    nonce = os.urandom(8)
    nonce_int = _int_from_bytes(nonce)

    ciphertext = bytearray()
    block_size = 8
    counter = 0
    for i in range(0, len(plaintext), block_size):
        block_plain = plaintext[i:i+block_size]
        ctr_input = (nonce_int ^ counter) & ((1 << 64) - 1)
        ctr_bytes = _int_to_bytes(ctr_input, 8)
        keystream = cipher.encrypt_block(ctr_bytes)
        ks = keystream[:len(block_plain)]
        ct_block = bytes(a ^ b for a, b in zip(block_plain, ks))
        ciphertext.extend(ct_block)
        counter += 1

    return nonce + bytes(ciphertext)

def decrypt_payload(ciphertext: bytes, key: bytes = DEFAULT_KEY) -> bytes:
    """
    Decrypt ciphertext produced by encrypt_payload.
    Input: nonce(8) || ciphertext
    Returns plaintext bytes.
    """
    if len(ciphertext) < 8:
        raise ValueError("Ciphertext too short")
    if len(key) != 10:
        raise ValueError("PRESENT-80 key must be 10 bytes")

    cipher = Present80(key)
    nonce = ciphertext[:8]
    data = ciphertext[8:]
    nonce_int = _int_from_bytes(nonce)

    plaintext = bytearray()
    block_size = 8
    counter = 0
    for i in range(0, len(data), block_size):
        block_ct = data[i:i+block_size]
        ctr_input = (nonce_int ^ counter) & ((1 << 64) - 1)
        ctr_bytes = _int_to_bytes(ctr_input, 8)
        keystream = cipher.encrypt_block(ctr_bytes)
        ks = keystream[:len(block_ct)]
        pt_block = bytes(a ^ b for a, b in zip(block_ct, ks))
        plaintext.extend(pt_block)
        counter += 1

    return bytes(plaintext)
