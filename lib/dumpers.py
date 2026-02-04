from pathlib import Path
import re

from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

from typing import Self, Any, cast

from .reader import Reader
from .writer import Writer
from .types import Int32, Float32, UInt64, Pointer, Color, ValueType

class BinaryDumper:
    def __init__(self : Self, path : Path):
        assert path.exists, "Path does not exist"
        assert re.match(r"UserGameStatsSchema_\d+.bin", path.name), "Invalid file"
        
        self.reader = Reader(path)

    def get_value_type(self : Self) -> ValueType:
        # May throw EOFError
        data : int = self.reader.read_uint8()
        
        # May throw ValueError
        value_type = ValueType(data)

        return value_type

    def dump(self : Self) -> dict[str, Any]:
        ret : dict[str, Any] = dict()

        while True:
            value_type = self.get_value_type()
            if (value_type == ValueType.END): break

            key : str = self.reader.read_utf8_string()
            if key.isnumeric(): key = DQ(key)

            match value_type:
                case ValueType.BEGIN:
                    ret[key] = self.dump()
                case ValueType.STRING:
                    ret[key] = DQ(self.reader.read_utf8_string())
                case ValueType.INT32:
                    ret[key] = Int32(self.reader.read_int32_le())
                case ValueType.FLOAT32:
                    ret[key] = Float32(self.reader.read_float32_le())
                case ValueType.POINTER:
                    ret[key] = Pointer(self.reader.read_uint32_le())
                case ValueType.COLOR:
                    ret[key] = Color(self.reader.read_uint32_le())
                case ValueType.UINT64:
                    ret[key] = UInt64(self.reader.read_uint64_le())
                case _:
                    raise NotImplementedError()

        return ret
    
class YamlDumper:
    def __init__(self : Self, path : Path):
        assert path.exists, "Path does not exist"
        assert re.match(r"UserGameStatsSchema_\d+.bin", path.name), "Invalid file"
        
        self.writer = Writer(path)
            
    def dump(self : Self, data : dict[str, Any]) -> None:
        def inner(data : dict[str, Any]):
            for key, value in data.items():
                match value:
                    case dict():
                        self.writer.write_uint8(ValueType.BEGIN)
                        self.writer.write_utf8_string(key)
                        inner(cast(dict[str, Any], value))
                        self.writer.write_uint8(ValueType.END)
                    case str() as string:
                        self.writer.write_uint8(ValueType.STRING)
                        self.writer.write_utf8_string(key)
                        self.writer.write_utf8_string(string)
                    case Int32(scalar):
                        self.writer.write_uint8(ValueType.INT32)
                        self.writer.write_utf8_string(key)
                        assert type(scalar) == int
                        self.writer.write_int32_le(scalar)
                    case Float32(scalar):
                        self.writer.write_uint8(ValueType.FLOAT32)
                        self.writer.write_utf8_string(key)
                        assert type(scalar) == float
                        self.writer.write_float32_le(scalar)
                    case Pointer(scalar):
                        self.writer.write_uint8(ValueType.POINTER)
                        self.writer.write_utf8_string(key)
                        assert type(scalar) == int
                        self.writer.write_uint32_le(scalar)
                    case Color(scalar):
                        self.writer.write_uint8(ValueType.COLOR)
                        self.writer.write_utf8_string(key)
                        assert type(scalar) == int
                        self.writer.write_uint32_le(scalar)
                    case UInt64(scalar):
                        self.writer.write_uint8(ValueType.UINT64)
                        self.writer.write_utf8_string(key)
                        assert type(scalar) == int
                        self.writer.write_uint64_le(scalar)
                    case _:
                        raise NotImplementedError
        inner(data)
        self.writer.write_uint8(ValueType.END)
                
