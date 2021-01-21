import attr


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
