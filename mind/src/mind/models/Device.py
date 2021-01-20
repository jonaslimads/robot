from enum import Enum
from typing import Optional

import attr

from mind.models.BaseModel import BaseModel


@attr.s(auto_attribs=True)
class Device(BaseModel):
    class Type(Enum):
        def __str__(self):
            return str(self.value)

        MICROPHONE = "MICROPHONE"
        CAMERA = "CAMERA"

    id: str = attr.ib(validator=attr.validators.instance_of(str))

    type: Type = attr.ib(validator=attr.validators.instance_of(Type))

    params: dict = attr.ib(default=dict(), validator=attr.validators.instance_of(dict))
