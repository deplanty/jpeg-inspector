from abc import ABC


class Metadata(ABC):
    signature: bytes
    name: str
    payload: bytes

    @classmethod
    def has_signature(cls, data: bytes) -> bool:
        return data.startswith(cls.signature)
