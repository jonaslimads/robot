from abc import ABC
from datetime import datetime
from decimal import Decimal
import json
from typing import List, Optional
from enum import Enum

import attr, cattr

cattr.register_structure_hook(datetime, lambda value, type: value)
cattr.register_structure_hook(Decimal, lambda value, type: value)
cattr.register_structure_hook(dict, lambda value, type: value)


class BaseModel(ABC):
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


class Message(BaseModel):

    ignore_middleware: List[str] = []  # = attr.ib(default=list(), validator=attr.validators.instance_of(list))


@attr.s(auto_attribs=True)
class AudioFrame:

    data: bytes = attr.ib(validator=attr.validators.instance_of(bytes))

    timestamp: float = attr.ib(validator=attr.validators.instance_of(float))

    duration: float = attr.ib(validator=attr.validators.instance_of(float))

    def is_empty(self) -> bool:
        return self.data == b""

    @staticmethod
    def EMPTY() -> "AudioFrame":
        return AudioFrame(b"", 0.0, 0.0)


@attr.s(auto_attribs=True)
class Device(BaseModel):
    class Type(Enum):

        MICROPHONE = "MICROPHONE"

        CAMERA = "CAMERA"

        def __str__(self):
            return str(self.value)

    id: str = attr.ib(validator=attr.validators.instance_of(str))

    type: Type = attr.ib(validator=attr.validators.instance_of(Type))

    params: dict = attr.ib(default=dict(), validator=attr.validators.instance_of(dict))


@attr.s(auto_attribs=True)
class Packet(Message):
    """
    a single packet transmitted between server and websockets.
    """

    device: Device

    data: bytes = attr.ib(default=b"")

    ignore_middleware: List[str] = attr.ib(default=list(), validator=attr.validators.instance_of(list))

    def to_bytes(self, *args, **kwargs) -> bytes:
        payload = {"device": self.device.to_dict()}

        return Packet.encode(f"{Packet.as_json(payload)}\r\n", *args, **kwargs) + self.data

    @classmethod
    def from_bytes(cls, data: bytes, *args, **kwargs) -> "Packet":
        delimiter_pos = data.find(b"\r\n")
        if delimiter_pos == -1:
            raise ValueError(f"Could not find packet delimiter from\n:{str(data)}")

        packet = cls.from_json(cls.decode(data[:delimiter_pos]))
        packet.data = data[delimiter_pos + 2 :]

        return packet

    def is_empty(self) -> bool:
        return self.data == b""

    @staticmethod
    def CAMERA_EMPTY_PACKET() -> "Packet":
        return Packet(Device("c0", Device.Type.CAMERA))

    @staticmethod
    def MICROPHONE_EMPTY_PACKET() -> "Packet":
        return Packet(Device("m0", Device.Type.MICROPHONE))

    def __str__(self):
        return f"Packet(device={self.device})"


@attr.s(auto_attribs=True)
class Text(Message):

    value: str = attr.ib(validator=attr.validators.instance_of(str))

    def __str__(self):
        return f"Text(value={self.value})"
