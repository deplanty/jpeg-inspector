import struct
from dataclasses import dataclass
from typing import BinaryIO

from src.objects import metadata
from src.objects.metadata import Metadata
from src.utils.exceptions import SegmentMarkerError


@dataclass
class Segment:
    # The name of the marker (e.g. SOI)
    name: str
    # The marker's bytes (e.g. 0xFFD8)
    marker: bytes
    # The data contained in the marker (without the 2 bytes for the length when present)
    data: Metadata
    # The priority order in all the segments
    order_priority: int

    def __len__(self) -> int:
        return len(self.get_full_segment())

    @classmethod
    def parse(cls, fid: BinaryIO) -> "Segment":
        marker = fid.read(2)
        name, length, order_priority = MARKERS[marker[1]]

        # Info about reading the markers: https://www.media.mit.edu/pia/Research/deepview/exif.html
        # The marker has no size (e.g. SOI and EOI) or a given size (e.g. DRI)
        data_size = 0
        if length >= 0:
            data_size = length
        # The marker has a variable size given by the next 2 bytes
        elif length == -1:
            # Read 2 bytes of data: >H (big endian unsigned short)
            # The length contains the 2 bytes indicating the size of the data
            length, *_ = struct.unpack(">H", fid.read(2))
            data_size = length - 2
        # The marker has a variable size: from this marker to the next one
        elif length == -2:
            # In this data, if a 0xff value is followed by a 0x00 it is a value and not a new marker.
            start = fid.tell()
            previous_byte = 0x00
            while True:
                byte: bytes = fid.read(1)
                # End of file without a marker
                if byte == b"":
                    raise SegmentMarkerError(
                        f"The segment with marker {marker} is incomplete. "
                        "The file ended before the end of the marker."
                    )
                value: int = int.from_bytes(byte)
                if previous_byte == 0xFF and cls.is_marker_valid(value):
                    break
                previous_byte = value
            # A marker as been found, so the parser go back two bytes
            fid.seek(-2, 1)
            length = fid.tell() - start
            data_size = length
            # Go back to the start of the parser
            fid.seek(start, 0)
        # If the marker has an unrecognised length
        else:
            raise SegmentMarkerError(
                f"The segment with marker {marker} has an unrecognised length {length}."
            )

        # Determine the type of metadata contained in the data
        data_obj = metadata.get(fid.read(data_size))
        segment = cls(name, marker, data_obj, order_priority)
        return segment

    @classmethod
    def from_metadata(cls, name: str, metadata: Metadata) -> "Segment":
        for marker, (marker_name, _, order) in MARKERS.items():
            if marker_name == name:
                marker = b"\xff" + int.to_bytes(marker)
                return cls(name, marker, metadata, order)

    @staticmethod
    def is_marker_valid(marker: int) -> bool:
        return marker in MARKERS

    def get_full_segment(self) -> bytes:
        _, length, _ = MARKERS[self.marker[1]]
        # No length is given
        if length >= 0 or length == -2:
            return self.marker + self.data.as_bytes()
        # A length is specified
        elif length == -1:
            # len + 2 to include the bytes for the length
            return self.marker + struct.pack(">H", len(self.data) + 2) + self.data.as_bytes()


# Key: the byte marker 0xffxx
# Values:
#   0: marker name
#   1: size in bytes
#      >=0 for known size.
#      -1 for variable size where the length is after their marker.
#      -2 for variable size where no length is given.
#   2: order priority
MARKERS: dict[int, tuple[str, int]] = {
    0xD8: ("SOI", 0, 0),  # First segment
    0xC0: ("SOF0", -1, 50),
    0xC2: ("SOF2", -1, 50),
    0xC4: ("DHT", -1, 50),
    0xDB: ("DQT", -1, 50),
    0xDD: ("DRI", 4, 50),
    0xDA: ("SOS", -2, 50),
    # The RSTn n=[0, 7] are inside the SOS marker and are not used here
    # 0xD0: ("RST0", 0, 40),
    # 0xD1: ("RST1", 0, 41),
    # 0xD2: ("RST2", 0, 42),
    # 0xD3: ("RST3", 0, 43),
    # 0xD4: ("RST4", 0, 44),
    # 0xD5: ("RST5", 0, 45),
    # 0xD6: ("RST6", 0, 46),
    # 0xD7: ("RST7", 0, 47),
    0xE0: ("APP0", -1, 10),
    0xE1: ("APP1", -1, 11),
    0xE2: ("APP2", -1, 12),
    0xE3: ("APP3", -1, 13),
    0xE4: ("APP4", -1, 14),
    0xE5: ("APP5", -1, 15),
    0xE6: ("APP6", -1, 16),
    0xE7: ("APP7", -1, 17),
    0xE8: ("APP8", -1, 18),
    0xE9: ("APP9", -1, 19),
    0xEA: ("APP10", -1, 20),
    0xEB: ("APP11", -1, 21),
    0xEC: ("APP12", -1, 22),
    0xED: ("APP13", -1, 23),
    0xEE: ("APP14", -1, 24),
    0xEF: ("APP15", -1, 25),
    0xFE: ("COM", -1, 20),
    0xD9: ("EOI", 0, 100),  # Last segment
}
