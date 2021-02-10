from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
import json
from typing import List, Optional, Type, Union
from enum import Enum

from mind.logging import get_logger

import attr, cattr

cattr.register_structure_hook(datetime, lambda value, type: value)
cattr.register_structure_hook(Decimal, lambda value, type: value)
cattr.register_structure_hook(dict, lambda value, type: value)

logger = get_logger(__name__)


class NotFoundModel(Exception):
    def __init__(self, metadata: str):
        super().__init__(f"Model for {metadata} not found")


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

    @staticmethod
    def from_bytes(data: bytes) -> Union["AudioFrame", "VideoFrame", None]:
        delimiter_pos = data.find(b"\r\n")
        if delimiter_pos == -1:
            raise ValueError(f"Could not find message delimiter from\n:{str(data)}")

        message_metadata = Message.decode(data[:delimiter_pos])
        message_data = data[delimiter_pos + 2 :]

        if "AudioFrame" in message_metadata:
            return AudioFrame(message_data)

        if "VideoFrame" in message_metadata:
            return VideoFrame(message_data)

        logger.warning(f"Model for {message_metadata} not found")

        # raise NotFoundModel(message_metadata)
        return None


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
class VideoFrame(Message):

    data: bytes = attr.ib(default=b"", validator=attr.validators.instance_of(bytes))

    _src: List[Type] = attr.ib(init=False, factory=list)

    def is_empty(self) -> bool:
        return self.data == b""

    @staticmethod
    def EMPTY() -> "VideoFrame":
        return VideoFrame(b"")

    def __str__(self):
        return f"VideoFrame(len(data)={len(self.data)}) from {self._src}"
