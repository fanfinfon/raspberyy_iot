from typing import Tuple

SBOX = [
    0xC, 0x5, 0x6, 0xB,
    0x9, 0x0, 0xA, 0xD,
    0x3, 0xE, 0xF, 0x8,
    0x4, 0x7, 0x1, 0x2
]

SBOX_INV = [SBOX.index(x) for x in range(16)]

# pLayer permutation table for 64-bit block
P = [0] * 64
for i in range(63):
    P[i] = (16 * i) % 63
P[63] = 63


def _sbox_layer(state: int) -> int:
    out = 0
    for i in range(16):
        nibble = (state >> (i * 4)) & 0xF
        out |= (SBOX[nibble] << (i * 4))
    return out


def _p_layer(state: int) -> int:
    out = 0
    for i in range(64):
        bit = (state >> i) & 1
        if bit:
            out |= (1 << P[i])
    return out


def _rotate_left(bits: int, shift: int, width: int) -> int:
    shift %= width
    return ((bits << shift) & ((1 << width) - 1)) | (bits >> (width - shift))


class Present80:
    """Manual PRESENT-80 cipher implementation (64-bit block, 80-bit key)."""
    def __init__(self, key: bytes):
        if len(key) != 10:
            raise ValueError("PRESENT-80 requires 10 bytes (80-bit) key")
        self.key_register = int.from_bytes(key, byteorder='big')
        self.round_keys = self._generate_round_keys()

    def _generate_round_keys(self):
        rk = []
        key = self.key_register
        for round_counter in range(1, 33):
            round_key = (key >> 16) & ((1 << 64) - 1)
            rk.append(round_key)
            key = _rotate_left(key, 61, 80)
            top_nibble = (key >> 76) & 0xF
            top_nibble = SBOX[top_nibble]
            key &= ~(0xF << 76)
            key |= (top_nibble << 76)
            rc = round_counter & 0x1F
            key ^= (rc << 15)
        return rk

    def encrypt_block(self, block: bytes) -> bytes:
        if len(block) != 8:
            raise ValueError("Block must be 8 bytes")
        state = int.from_bytes(block, byteorder='big')
        for round_idx in range(31):
            state ^= self.round_keys[round_idx]
            state = _sbox_layer(state)
            state = _p_layer(state)
        state ^= self.round_keys[31]
        return state.to_bytes(8, byteorder='big')

    def decrypt_block(self, block: bytes) -> bytes:
        if len(block) != 8:
            raise ValueError("Block must be 8 bytes")
        state = int.from_bytes(block, byteorder='big')
        state ^= self.round_keys[31]
        for round_idx in reversed(range(31)):
            tmp = 0
            for i in range(64):
                bit = (state >> P[i]) & 1
                if bit:
                    tmp |= (1 << i)
            state = tmp
            out = 0
            for i in range(16):
                nibble = (state >> (i * 4)) & 0xF
                out |= (SBOX_INV[nibble] << (i * 4))
            state = out
            state ^= self.round_keys[round_idx]
        return state.to_bytes(8, byteorder='big')
