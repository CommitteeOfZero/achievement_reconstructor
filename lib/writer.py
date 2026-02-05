from pathlib import Path
import struct

from typing import Self, BinaryIO

class Writer:
    def __init__(self : Self, path : Path):
        self.handle : BinaryIO = open(path, "wb")

    def __del__(self : Self) -> None:
        if (self.handle.closed): return
        self.handle.close()

    def __write_raw(self : Self, raw : bytes) -> int:
        return self.handle.write(raw)
    
    def write_uint8(self : Self, value : int) -> int:
        return self.__write_raw(struct.pack("B", value))
    
    def write_int32_le(self : Self, value : int) -> int:
        return self.__write_raw(struct.pack("<i", value))
    
    def write_uint32_le(self : Self, value : int) -> int:
        return self.__write_raw(struct.pack("<I", value))
    
    def write_float32_le(self : Self, value : float) -> int:
        return self.__write_raw(struct.pack("<f", value))
    
    def write_uint64_le(self : Self, value : int) -> int:
        return self.__write_raw(struct.pack("<Q", value))
    
    def write_utf8_string(self : Self, value : str):
        assert len(value) <= 128
        raw_string : bytes = value.encode("utf-8") + b"\x00"
        return self.__write_raw(raw_string)