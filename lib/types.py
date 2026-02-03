from enum import IntEnum, auto

from typing import Self, Any
from ruamel.yaml import YAML

yaml = YAML()
yaml.encoding = "utf-8"

class YamlScalar:
    __match_args__ = ("value",)
    
    def __init__(self : Self, value : Any) -> None:
        if not isinstance(value, int) and not isinstance(value, float):
            raise ValueError(f"{ self.__class__.__name__ } expected scalar value, got \"{ type(value).__name__ }\".")
        
        self.value : int | float = value
        
    @classmethod
    def __init_subclass__(cls : type[Self]) -> None:
        yaml.register_class(cls)

    @classmethod
    def from_yaml(cls : type[Self], constructor : Any, node : Any) -> Self:
        value : float | int

        try:
            value = float(node.value)
        except ValueError:
            raise

        if value.is_integer(): value = int(value)

        return cls(value)

    @classmethod
    def to_yaml(cls : type[Self], representer : Any, node : Any):
        return representer.represent_scalar(u"!{.__name__}".format(cls), u'{.value}'.format(node))

class Int32(YamlScalar):    ...
class Float32(YamlScalar):  ...
class Pointer(YamlScalar):  ...
class Color(YamlScalar):    ...
class UInt64(YamlScalar):   ...

class ValueType(IntEnum):
    MAPPING_BEGIN = 0
    STRING = auto()
    INT32 = auto()
    FLOAT32 = auto()
    POINTER = auto()
    WIDESTRING = auto()
    COLOR = auto()
    UINT64 = auto()
    MAPPING_END = auto()