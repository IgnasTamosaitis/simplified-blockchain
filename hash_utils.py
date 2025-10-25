"""

my_hash(data: str) -> str grazina heksadine eilute (0-9,a-f),
naudojama:
- transakciju ID generavimui
- bloko antrastes hash'ui (Proof-of-Work)

"""

MASK64 = (1 << 64) - 1

def rl(x: int, r: int) -> int:
    r &= 63
    return ((x << r) & MASK64) | (x >> (64 - r))

def my_hash(data: str) -> str:

    a = 0x1A2B3C4D5E6F7788
    b = 0x8899AABBCCDDEEFF
    c = 0x0123456789ABCDEF
    d = 0xF0E1D2C3B4A59687

    data_bytes = data.encode("utf-8")

    for ch in data_bytes:
        # miksavimas i a
        a ^= ch
        a = rl(a, 7)
        a = (a * 33 + (ch ^ (ch >> 2))) & MASK64

        # miksavimas i b
        b ^= rl(ch, 11)
        b = (b * 29 + (ch ^ (ch >> 4))) & MASK64

        # miksavimas i c
        c ^= rl(ch, 19)
        c = (c * 35 + (ch ^ (ch >> 6))) & MASK64

        # miksavimas i d
        d ^= rl(ch, 23)
        d = (d * 39 + (ch ^ (ch >> 8))) & MASK64

    a ^= rl(b, 13);  a = (a + c) & MASK64
    b ^= rl(c, 17);  b = (b + d) & MASK64
    c ^= rl(d, 29);  c = (c + a) & MASK64
    d ^= rl(a, 31);  d = (d + b) & MASK64

    return f"{a:016x}{b:016x}{c:016x}{d:016x}"