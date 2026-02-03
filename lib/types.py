from enum import Enum, auto

from typing import Self, Any
from ruamel.yaml import YAML

yaml = YAML()
yaml.encoding = "utf-8"

class YamlScalar:
    def __init__(self : Self, value : int | float) -> None:
        self.value = value
    
    @classmethod
    def __init_subclass__(cls) -> None:
        yaml.register_class(cls)

    @classmethod
    def to_yaml(cls : type[Self], representer : Any, node : Any):
        return representer.represent_scalar(u"!{.__name__}".format(cls), u'{.value}'.format(node))

class Int32(YamlScalar):    ...
class Float32(YamlScalar):  ...
class Pointer(YamlScalar):  ...
class Color(YamlScalar):    ...
class UInt64(YamlScalar):   ...

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