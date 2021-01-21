from enum import Enum
import json
from typing import Optional, List

import attr

from mind.models.BaseModel import BaseModel
from mind.models.Device import Device


@attr.s(auto_attribs=True)
class Packet(BaseModel):

    device: Device

    _data: bytes = attr.ib(default=b"")

    def to_bytes(self, *args, **kwargs) -> bytes:
        payload = {"device": self.device.to_dict()}

        return Packet.encode(f"{Packet.as_json(payload)}\r\n", *args, **kwargs) + self._data

    @classmethod
    def from_bytes(cls, data: bytes, *args, **kwargs) -> "Packet":
        delimiter_pos = data.find(b"\r\n")
        if delimiter_pos == -1:
            raise ValueError(f"Could not find packet delimiter from\n:{str(data)}")

        packet = cls.from_json(cls.decode(data[:delimiter_pos]))
        packet._data = data[delimiter_pos + 2 :]

        return packet

    def is_empty(self) -> bool:
        return self._data == b""

    @staticmethod
    def CAMERA_EMPTY_PACKET() -> "Packet":
        return Packet(Device("c0", Device.Type.CAMERA))

    @staticmethod
    def MICROPHONE_EMPTY_PACKET() -> "Packet":
        return Packet(Device("m0", Device.Type.MICROPHONE))
