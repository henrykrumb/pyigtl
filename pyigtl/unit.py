import struct


IGTL_UNITS = {
    'meter': 0x01,
    'gram': 0x02,
    'second': 0x03,
    'ampere': 0x04,
    'kelvin': 0x05,
    'mole': 0x06,
    'candela': 0x07,
    'radian': 0x08,
    'steradian': 0x09,
    'hertz': 0x0A,
    'newton': 0x0B,
    'pascal': 0x0C,
    'joule': 0x0D,
    'watt': 0x0E,
    'coulomb': 0x0F,
    'volt': 0x10,
    'farad': 0x11,
    'ohm': 0x12,
    'siemens': 0x013,
    'weber': 0x14,
    'tesla': 0x15,
    'henry': 0x16,
    'lumen': 0x17,
    'lux': 0x18,
    'becquerel': 0x19,
    'gray': 0x1A,
    'sievert': 0x1B
}

IGTL_EXPONENTS = {
    0: 0x0,
    1: 0x1,
    2: 0x2,
    3: 0x3,
    4: 0x4,
    5: 0x5,
    6: 0x6,
    7: 0x7,
    -1: 0xF,
    -2: 0xE,
    -3: 0xD,
    -4: 0xC,
    -5: 0xB,
    -6: 0xA
}

IGTL_PREFIXES = {
    None: 0x0,
    # --
    'deka': 0x1,
    'deca': 0x1,
    'hecto': 0x2,
    'kilo': 0x3,
    'mega': 0x4,
    'giga': 0x5,
    'tera': 0x6,
    'peta': 0x7,
    # --
    'deci': 0x9,
    'centi': 0xA,
    'milli': 0xB,
    'micro': 0xC,
    'nano': 0xD,
    'pico': 0xE,
    'femto': 0xF,

    1: 0x1,
    2: 0x2,
    3: 0x3,
    6: 0x4,
    9: 0x5,
    12: 0x6,
    15: 0x7,
    # --
    -1: 0x9,
    -2: 0xA,
    -3: 0xB,
    -6: 0xC,
    -9: 0xD,
    -12: 0xE,
    -15: 0xF,

    '1e1': 0x1,
    '1e2': 0x2,
    '1e3': 0x3,
    '1e6': 0x4,
    '1e9': 0x5,
    '1e12': 0x6,
    '1e15': 0x7,
    # --
    '1e-1': 0x9,
    '1e-2': 0xA,
    '1e-3': 0xB,
    '1e-6': 0xC,
    '1e-9': 0xD,
    '1e-12': 0xE,
    '1e-15': 0xF
}


class SensorUnit:
    def __init__(self, unit, prefix=None, exp=1):
        self._unit = unit
        self._prefix = prefix
        self._exp = exp
        self._validate()

    @property
    def unit(self):
        return self._unit

    @property
    def prefix(self):
        return self._prefix

    @property
    def exp(self):
        return self._exp

    @unit.setter
    def unit(self, value):
        self._unit = value
        self._validate()

    @prefix.setter
    def prefix(self, value):
        self._prefix = value
        self._validate()

    @exp.setter
    def exp(self, value):
        self._exp = value
        self._validate()

    def _validate(self):
        # make unit and exponent iterable if only single values were passed
        try:
            iter(self.unit)
        except TypeError:
            self.unit = [self.unit]
        try:
            iter(self.exp)
        except TypeError:
            self.exp = [self.exp]
        assert len(self.unit) < 6
        assert len(self.exp) == len(self.unit)

        if self.prefix not in IGTL_PREFIXES:
            raise RuntimeError(f'Prefix not supported: {self.prefix}')
        for u in self.unit:
            if type(u) == str and u not in IGTL_UNITS:
                raise RuntimeError(f'Unknown unit: {u}')
            if type(u) == int and u not in list(IGTL_UNITS.values()):
                raise RuntimeError(f'Unknown unit code: {u}')
        for e in self.exp:
            if e not in IGTL_EXPONENTS:
                raise RuntimeError(f'Exponent not supported: {e}')
        
    def pack(self):
        prefix = IGTL_PREFIXES[self.prefix]
        data = prefix << 60
        for i in range(len(self.unit)):
            unit = IGTL_UNITS[self.unit[i]]
            exp = IGTL_EXPONENTS[self.exp[i]]
            exp &= 0x0F
            data |= unit << (10 * (5 - i) + 4)
            data |= exp << (10 * (5 - i))
        binary_content = struct.pack('> 64s', data)
        return binary_content

    @staticmethod
    def unpack(pack):
        prefix = pack >> 60
        unit = []
        exp = []
        for i in range(6):
            u = pack >> (10 * (5 - i) + 4) & 0x3F
            e = pack >> (10 * (5 - i)) & 0x0F
            unit.append(u)
            exp.append(e)
        return SensorUnit(unit, prefix, exp)