from pathlib import Path
import re

from ruamel.yaml.scalarstring import DoubleQuotedScalarString as DQ

from typing import Self, cast, assert_never

from .reader import Reader
from .writer import Writer
from .types import Int32, Float32, UInt64, Pointer, Color, ValueType, YamlScalar

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

    def dump(self : Self) -> dict[str, object]:
        ret : dict[str, object] = dict()

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
                case ValueType.WIDESTRING:
                    raise NotImplementedError("Wide strings are not supported.")
                case ValueType.COLOR:
                    ret[key] = Color(self.reader.read_uint32_le())
                case ValueType.UINT64:
                    ret[key] = UInt64(self.reader.read_uint64_le())
                case _:
                    assert_never(value_type)
        return ret
    
class YamlDumper:
    def __init__(self : Self, path : Path):
        assert path.exists, "Path does not exist"
        assert re.match(r"UserGameStatsSchema_\d+.bin", path.name), "Invalid file"
        
        self.writer = Writer(path)
            
    def dump(self : Self, data : dict[str, object]) -> None:
        def inner(data : dict[str, object]):
            for key, value in data.items():
                match value:
                    case dict():
                        self.writer.write_uint8(ValueType.BEGIN)
                        self.writer.write_utf8_string(key)
                        inner(cast(dict[str, object], value))
                        self.writer.write_uint8(ValueType.END)
                    case str() as string:
                        self.writer.write_uint8(ValueType.STRING)
                        self.writer.write_utf8_string(key)
                        self.writer.write_utf8_string(string)
                    case YamlScalar(_, value_type) as kind:
                        self.writer.write_uint8(value_type)
                        self.writer.write_utf8_string(key)
                        match kind:
                            case Int32(scalar):
                                assert isinstance(scalar, int)
                                self.writer.write_int32_le(scalar)
                            case Float32(scalar):
                                assert isinstance(scalar, float)
                                self.writer.write_float32_le(scalar)
                            case Pointer(scalar):
                                assert isinstance(scalar, int)
                                self.writer.write_uint32_le(scalar)
                            case Color(scalar):
                                assert isinstance(scalar, int)
                                self.writer.write_uint32_le(scalar)
                            case UInt64(scalar):
                                assert isinstance(scalar, int)
                                self.writer.write_uint64_le(scalar)
                            case YamlScalar():
                                assert False, "YamlScalar isn't instantiable"
                            case _:
                                assert_never(kind)
                    case _:
                        raise NotImplementedError(f"Type \"{ type(value).__name__ }\" is not a valid schema type.")
        inner(data)
        self.writer.write_uint8(ValueType.END)
                
