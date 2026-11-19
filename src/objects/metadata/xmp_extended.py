import hashlib
import struct

from src.utils.exceptions import SegmentMarkerError

from .metadata import Metadata
from .xml_metadata import XmlMetadata


class ExtendedXmpFragment(Metadata):
    signature = b"http://ns.adobe.com/xmp/extension/\x00"
    name = "Extended XMP fragment"
    max_size: int = 64500

    def __init__(self, data: bytes):
        super().__init__(data)

        self.guid: bytes = self.payload[:32]
        self.size_total: int = struct.unpack(">I", self.payload[32:36])[0]
        self.offset: int = struct.unpack(">I", self.payload[36:40])[0]
        self.payload = self.payload[40:]

    @classmethod
    def from_payload(
        cls, guid: bytes, size_total: int, offset: int, payload: bytes
    ) -> "ExtendedXmpFragment":
        size_total_b = struct.pack(">I", size_total)
        offset_b = struct.pack(">I", offset)
        data = cls.signature + guid + size_total_b + offset_b + payload
        return cls(data)

    def as_bytes(self) -> bytes:
        size: bytes = struct.pack(">I", self.size_total)
        offset: bytes = struct.pack(">I", self.offset)
        return self.signature + self.guid + size + offset + self.payload

    def to_str(self) -> str:
        try:
            return f"{self.name} {self.guid.decode('utf-8')}\n{self.payload.decode('utf-8')}"
        except UnicodeDecodeError:
            return self.to_raw_str()


class ExtendedXmp(XmlMetadata):
    signature = b""
    name = "Extended XMP"

    @property
    def guid(self) -> bytes:
        """The identifier of the Extended XMP = md5 of the payload."""
        return hashlib.md5(self.payload).hexdigest().upper().encode()

    @classmethod
    def from_fragments(cls, fragments: list[ExtendedXmpFragment]) -> "ExtendedXmp":
        payload: bytes = b""
        for fragment in sorted(fragments, key=lambda frag: frag.offset):
            payload += fragment.payload

        xmp_extension = cls(payload)
        if fragments[0].guid != xmp_extension.guid:
            raise SegmentMarkerError(
                "Error when reading Extended XMP. Fused fragments doesn't have the correct GUID"
                f"Expected {fragments[0].guid}, found {xmp_extension.guid}."
            )

        return xmp_extension

    def to_fragments(self) -> list[ExtendedXmpFragment]:
        fragments: list[ExtendedXmpFragment] = []
        size_total = len(self.payload)
        for index in range(size_total // ExtendedXmpFragment.max_size + 1):
            offset = index * ExtendedXmpFragment.max_size
            fragment = ExtendedXmpFragment.from_payload(
                self.guid, size_total, offset, self.payload
            )
            fragments.append(fragment)
        return fragments
