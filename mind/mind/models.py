from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
import json
from typing import List, Optional, Type, Union
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

    # Prevent circular enqueue of a message. Example:
    #   ChatBot's listens for Text, then it enqueues a new Text as of result of processing.
    #   If we don't check for circular enqueue, chatbot will listen for its own produced Text.
    _src: List[Type]

    @property
    def src(self) -> List[Type]:
        return self._src

    def append_src(self, src: Union[Type, List[Type]]):
        if not isinstance(src, list):
            src = [src]
        for s in src:
            if s not in self._src:
                self._src.append(s)
        return self


@attr.s(auto_attribs=True)
class Text(Message):

    value: str = attr.ib(validator=attr.validators.instance_of(str))

    _src: List[Type] = attr.ib(init=False, factory=list)

    def __str__(self):
        return f"Text(value={self.value}) from {self.src}"


@attr.s(auto_attribs=True)
class AudioFrame(Message):

    data: bytes = attr.ib(default=b"", validator=attr.validators.instance_of(bytes))

    timestamp: float = attr.ib(default=-1.0, validator=attr.validators.instance_of(float))

    duration: float = attr.ib(default=-1.0, validator=attr.validators.instance_of(float))

    sample_rate: int = attr.ib(default=16000)

    channels: int = attr.ib(default=1)

    _src: List[Type] = attr.ib(init=False, factory=list)

    def is_empty(self) -> bool:
        return self.data == b""

    @staticmethod
    def EMPTY() -> "AudioFrame":
        return AudioFrame(b"", 0.0, 0.0)

    def __str__(self):
        return f"AudioFrame(len(data)={len(self.data)}, timestamp={self.timestamp}, duration={self.duration}, sample_rate={self.sample_rate}) from {self._src}"


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

    _src: List[Type] = attr.ib(init=False, factory=list)

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
    def MICROPHONE(data: bytes) -> "Packet":
        return Packet(Device("m0", Device.Type.MICROPHONE), data)

    @staticmethod
    def MICROPHONE_EMPTY_PACKET() -> "Packet":
        return Packet.MICROPHONE(b"")

    def __str__(self):
        return f"Packet(device={self.device})"
