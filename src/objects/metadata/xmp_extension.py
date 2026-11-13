import struct

from .metadata import Metadata
from .xml_metadata import XmlMetadata


class XmpExtensionFragment(Metadata):
    signature = b"http://ns.adobe.com/xmp/extension/\x00"
    name = "XMP extension fragment"

    def __init__(self, data: bytes):
        super().__init__(data)

        self.guid: bytes = self.payload[:32]
        self.size_total: int = struct.unpack(">I", self.payload[32:36])[0]
        self.offset: int = struct.unpack(">I", self.payload[36:40])[0]
        self.payload = self.payload[40:]

    def as_bytes(self) -> bytes:
        size: bytes = struct.pack(">I", self.size_total)
        offset: bytes = struct.pack(">I", self.offset)
        return self.signature + self.guid + size + offset + self.payload


class XmpExtension(XmlMetadata):
    signature = b""
    name = "XMP extension"

    def __init__(self, payload: bytes):
        super().__init__(payload)

    @classmethod
    def from_fragments(cls, fragments: list[XmpExtensionFragment]) -> "XmpExtension":
        payload: bytes = b""
        for fragment in sorted(fragments, key=lambda frag: frag.offset):
            payload += fragment.payload

        return cls(payload)
