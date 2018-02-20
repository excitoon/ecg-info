def from_bytes(bytes):
    return int.from_bytes(bytes, byteorder='little')

def read_block(bytes, offset, size):
    assert len(bytes) >= offset + size
    return bytes[offset:offset+size]

def read_block_until_end(bytes, offset):
    assert len(bytes) >= offset
    return bytes[offset:]

def read_null_terminated(bytes, offset):
    zero = bytes.find(b'\x00', offset)
    if zero == -1:
        return bytes[offset:]
    else:
        return bytes[offset:zero] 

def read_byte(bytes, offset):
    return from_bytes(read_block(bytes, offset, 1))

def read_word(bytes, offset):
    return from_bytes(read_block(bytes, offset, 2))

def read_dword(bytes, offset):
    return from_bytes(read_block(bytes, offset, 4))

class Pipe(object):
    def __init__(self, bytes):
        self.bytes = bytes
        self.offset = 0

    def eof(self):
        return self.offset == len(self.bytes)

    def read_block(self, size):
        result = read_block(self.bytes, self.offset, size)
        self.offset += size
        return result        

    def read_byte(self):
        result = read_byte(self.bytes, self.offset)
        self.offset += 1
        return result

    def read_word(self):
        result = read_word(self.bytes, self.offset)
        self.offset += 2
        return result

    def read_dword(self):
        result = read_dword(self.bytes, self.offset)
        self.offset += 4
        return result

class DeltaReader(object):
    def __init__(self, data, max_value):
        self.__data = Pipe(data)
        self.__max_value = max_value
        self.__bits = 0
        self.__word = 0
        self.__last = 0

    def _load_word(self):
        assert self.__bits < 16
        self.__word <<= self.__bits
        self.__bits += 16
        self.__word |= self.__data.read_word() & 0xffff
        self.__word &= 0x7fffffff

    def _read_bit(self):
        if self.__bits == 0:
            self._load_word()
        result = self.__word >> 15 + max(0, self.__bits - 16) & 1
        if self.__bits <= 16:
            self.__word <<= 1
        self.__bits -= 1
        return result

    def _read_three_bits(self):
        if self.__bits < 3:
            self._load_word()
        result = self.__word >> 13 + max(0, self.__bits - 16) & 7
        self.__word <<= 3 if self.__bits <= 16 else 19 - self.__bits
        self.__bits -= 3
        return result

    def _read_byte(self):
        if self.__bits < 8:
            self._load_word()
        result = self.__word >> 8 + max(0, self.__bits - 16) & 0xff
        self.__word <<= 8 if self.__bits <= 16 else 24 - self.__bits
        self.__bits -= 8
        return result

    def _read_word(self):
        if self.__bits < 16:
            self._load_word()
        result = self.__word >> max(0, self.__bits - 16) & 0xffff
        self.__word <<= 32 - self.__bits
        self.__bits -= 16
        return result

    def _read_packed(self):
        part = self._read_bit()
        if part == 0:                            # 0          ->   0
            return 0                             # 1000       ->   1
        part = self._read_three_bits()           # 1001       ->  -1
        if part < 5:                             # 1010       ->   2
            return [1, -1, 2, -2, 98][part]      # 1011       ->  -2
        part = part << 1 & 7 | self._read_bit()  # 1100       ->  98
        if part < 6:                             # 11010      ->   3
            return [4, -4, 3, -3][part & 3]      # 11011      ->  -3
        part = part << 1 & 3 | self._read_bit()  # 11100      ->   4
        if part & 2 == 0:                        # 11101      ->  -4
            return [5, -5][part & 1]             # 111100     ->   5
        part = part << 1 & 3 | self._read_bit()  # 111101     ->  -5
        if part & 2 == 0:                        # 1111100    ->   6
            return [6, -6][part & 1]             # 1111101    ->  -6
        part = part << 1 & 3 | self._read_bit()  # 11111100   ->   7
        if part & 2 == 0:                        # 11111101   ->  -7
            return [7, -7][part & 1]             # 111111100  ->   8
        part = part << 1 & 3 | self._read_bit()  # 111111101  ->  -8
        if part & 2 == 0:                        # 1111111100 ->   9
            return [8, -8][part & 1]             # 1111111101 ->  -9
        part = part << 1 & 3 | self._read_bit()  # 1111111110 ->  99
        return [9, -9, 99, 100][part]            # 1111111111 -> 100

    def _read_signed_byte(self):
        byte = self._read_byte()
        if byte & 0x80 == 0x80:
            return (byte & 0x7f) - 0x80
        else:
            return byte

    def _read_signed_word(self):
        word = self._read_word()
        if word & 0x8000 == 0x8000:
            return (word & 0x7fff) - 0x8000
        else:
            return word

    def read(self, count):
        samples = []
        value = self.__data.read_word()
        if value & 0x800 == 0x800:
            self.__last = (value & 0x7ff) - 0x800
        else:
            self.__last = value & 0xfff
        samples.append(self.__last/self.__max_value/10)
        while len(samples) < count:
            raw = self._read_packed()
            if raw == 100:
                raw = self._read_packed()
            else:
                if raw == 99:
                    raw = self._read_signed_word()
                elif raw == 98:
                    raw = self._read_signed_byte()
                value = raw*2 - 3 if raw > 3 else raw
                value = value*2 + 3 if value < -3 else value
                self.__last += value
                samples.append(self.__last/self.__max_value/10)
        assert self.__data.eof()
        return samples
