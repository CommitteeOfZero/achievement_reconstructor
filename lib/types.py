# pyright: reportUnknownMemberType=false
 
from enum import IntEnum, auto

from ruamel.yaml import YAML, Node, Representer

from typing import Self, Protocol, ClassVar, runtime_checkable, cast

yaml = YAML()
yaml.encoding = "utf-8"

class ValueType(IntEnum):
    BEGIN = 0
    STRING = auto()
    INT32 = auto()
    FLOAT32 = auto()
    POINTER = auto()
    WIDESTRING = auto()
    COLOR = auto()
    UINT64 = auto()
    END = auto()
    
@runtime_checkable
class ValueTyped(Protocol):
    value_type : ClassVar[ValueType]

class YamlScalar(ValueTyped):
    __match_args__ = ("value", "value_type")

    def __new__(cls : type[Self], value : object) -> Self:
        if cls is __class__:
            raise TypeError(f"Only subclasses of { __class__.__name__ } can be instanced.")
        return super().__new__(cls)
        
    def __init__(self : Self, value : object) -> None:
        if not isinstance(value, int) and not isinstance(value, float):
            raise TypeError(f"{ self.__class__.__name__ } expected scalar value, got \"{ type(value).__name__ }\" instead.")
        
        self.value : int | float = value
        
    @classmethod
    def __init_subclass__(cls : type[Self]) -> None:
        yaml.register_class(cls)

    @classmethod
    def from_yaml(cls : type[Self], _, node : Node) -> Self:
        value : float | int

        try:
            value = float(cast(str, node.value))
        except:
            raise ValueError(f"Expected float-convertible string in YAML node, got \"{ node.value }\" instead.")

        if value.is_integer(): value = int(value)

        return cls(value)

    @classmethod
    def to_yaml(cls : type[Self], representer : Representer, node : Node):
        return representer.represent_scalar(u"!{.__name__}".format(cls), u'{.value}'.format(node))

class Int32(YamlScalar):    value_type = ValueType.INT32
class Float32(YamlScalar):  value_type = ValueType.FLOAT32
class Pointer(YamlScalar):  value_type = ValueType.POINTER
class Color(YamlScalar):    value_type = ValueType.COLOR
class UInt64(YamlScalar):   value_type = ValueType.UINT64