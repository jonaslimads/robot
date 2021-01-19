from datetime import datetime
from decimal import Decimal
import json
from typing import List

import attr, cattr


cattr.register_structure_hook(datetime, lambda value, type: value)
cattr.register_structure_hook(Decimal, lambda value, type: value)
cattr.register_structure_hook(dict, lambda value, type: value)


@attr.s(auto_attribs=True)
class BaseModel:
    def to_dict(self) -> dict:
        return cattr.unstructure(self)

    def to_json(self) -> str:
        return BaseModel.as_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict):
        return cattr.structure(data, cls)

    @classmethod
    def from_list(cls, data_list: List[dict]):
        return [cls.from_dict(data) for data in data_list]

    @classmethod
    def from_json(cls, data: str):
        return cattr.structure(json.loads(data), cls)

    @classmethod
    def as_json(cls, data: dict) -> str:
        return json.dumps(data, separators=(",", ":"))

    @staticmethod
    def encode(data: str, *args, **kwargs) -> bytes:
        return data.encode("utf-8", *args, **kwargs)

    @staticmethod
    def decode(data: bytes, *args, **kwargs) -> str:
        return data.decode("utf-8", *args, **kwargs)
