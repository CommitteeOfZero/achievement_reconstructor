from typing import Self, Any
from pathlib import Path
import re

from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

from .reader import Reader
from .types import Int32, Float32, UInt64, Pointer, Color, KeyType

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

            key : str = self.reader.read_utf8_string()
            if key.isnumeric(): key = DQ(key)

            match key_type:
                case KeyType.NONE:
                    ret[key] = self.parse()
                case KeyType.STRING:
                    ret[key] = DQ(self.reader.read_utf8_string())
                case KeyType.INT32:
                    ret[key] = Int32(self.reader.read_int32_le())
                case KeyType.FLOAT32:
                    ret[key] = Float32(self.reader.read_float32_le())
                case KeyType.POINTER:
                    ret[key] = Pointer(self.reader.read_uint32_le())
                case KeyType.COLOR:
                    ret[key] = Color(self.reader.read_uint32_le())
                case KeyType.UINT64:
                    ret[key] = UInt64(self.reader.read_uint64_le())
                case _:
                    raise NotImplementedError()

        return ret