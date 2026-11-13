import struct

from .metadata import Metadata


class XmpExtensionFragment(Metadata):
    signature = b"http://ns.adobe.com/xmp/extension/\x00"
    name = "XMP extension"

    def __init__(self, data: bytes):
        super().__init__(data)

        self.guid: bytes = self.payload[:32]
        self.size_total: int = struct.unpack(">I", self.payload[32:36])[0]
        self.offset: int = struct.unpack(">I", self.payload[36:40])[0]
        self.payload = self.payload[40:]

    def __str__(self) -> str:
        return f"{self.name}: {self.signature} {self.payload[:40]}"

    def __repr__(self) -> str:
        return str(self)
