from typing import Self, Any
from enum import Enum, auto
from pathlib import Path
import re

from .reader import Reader

class KeyType(Enum):
    NONE = 0
    STRING = auto()
    INT32 = auto()
    FLOAT32 = auto()
    POINTER = auto()
    WIDESTRING = auto()
    COLOR = auto()
    UINT64 = auto()
    END = auto()

class Parser:
    def __init__(self : Self, path : Path):
        assert path.exists, "Path does not exist"
        assert re.match(r"UserGameStatsSchema_\d+.bin", path.name), "Invalid file"
        
        self.reader = Reader(path)

    def get_key_type(self : Self) -> KeyType:
        # May throw EOFError
        data : int = self.reader.read_uint8()
        
        # May throw ValueError
        key_type = KeyType(data)

        return key_type

    def parse(self : Self) -> dict[str, Any]:
        ret : dict[str, Any] = dict()

        while True:
            key_type = self.get_key_type()
            if (key_type == KeyType.END): break

            key = self.reader.read_utf8_string()

            match key_type:
                case KeyType.NONE:
                    ret[key] = self.parse()
                case KeyType.STRING:
                    ret[key] = self.reader.read_utf8_string()
                case KeyType.INT32:
                    ret[key] = self.reader.read_int32_le()
                case KeyType.FLOAT32:
                    ret[key] = self.reader.read_float32_le()
                case KeyType.POINTER | KeyType.COLOR:
                    ret[key] = self.reader.read_uint32_le()
                case KeyType.UINT64:
                    ret[key] = self.reader.read_uint64_le()
                case _:
                    raise NotImplementedError()

        return ret