from pathlib import Path
from itertools import takewhile
import struct

from typing import Self

class Reader:
    def __init__(self : Self, path : Path):
        self.contents : bytes
        self.pointer : int

        # No need to keep the file open
        # The parser can still pretend as if it's reading from file
        with open(path, "rb") as fl:
            self.contents = fl.read()
            self.pointer = 0
    
    def __read_raw(self : Self, size : int) -> bytes:
        if len(self.contents) < self.pointer + size:
            raise EOFError("Attempted to read past end of file.")
        
        ret : bytes = self.contents[self.pointer : self.pointer + size]
        self.pointer += size
        return ret

    def peek(self : Self) -> bytes:
        if len(self.contents) < self.pointer + 1:
            raise EOFError("Attempted to read past end of file.")
        
        return self.contents[self.pointer : self.pointer + 1]

    def read_uint8(self : Self) -> int:
        return struct.unpack("B", self.__read_raw(1))[0]
    
    def read_int32_le(self : Self) -> int:
        return struct.unpack("<i", self.__read_raw(4))[0]
    
    def read_uint32_le(self : Self) -> int:
        return struct.unpack("<I", self.__read_raw(4))[0]
    
    def read_float32_le(self : Self) -> float:
        return struct.unpack("<f", self.__read_raw(4))[0]

    def read_uint64_le(self : Self) -> int:
        return struct.unpack("<Q", self.__read_raw(4))[0]

    def read_utf8_string(self : Self) -> str:
        raw_string : bytes = self.contents[self.pointer : self.pointer + 128]
        raw_string = bytes(takewhile(lambda byte : byte != 0, raw_string))

        string : str = raw_string.decode("utf-8")
        self.pointer += len(raw_string) + 1
        
        if self.contents[self.pointer - 1] == 0: return string

        if len(string) < 128:
            raise EOFError("Expected null-terminated UTF-8 string, reached EOF instead.")
        else:
            raise ValueError("UTF-8 strings longer than 127 characters are not supported by the schema ")
