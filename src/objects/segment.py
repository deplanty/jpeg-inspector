import struct
from dataclasses import dataclass
from typing import BinaryIO

from src.objects import metadata
from src.utils.exceptions import SegmentMarkerError


@dataclass
class Segment:
    # The name of the marker (e.g. SOI)
    name: str
    # The marker's bytes (e.g. 0xFFD8)
    marker: bytes
    # The length of the marker's data (without the 2 bytes of the marker)
    length: int
    # The size of the data (without the 2 bytes for the length when present)
    data_size: int
    # The data contained in the marker (without the 2 bytes for the length when present)
    data: metadata.Metadata

    def __len__(self) -> int:
        return len(self.get_full_segment())

    @classmethod
    def parse(cls, fid: BinaryIO) -> "Segment":
        marker = fid.read(2)
        name, length = MARKERS[marker[1]]

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
        segment = cls(name, marker, length, data_size, data_obj)
        return segment

    @staticmethod
    def is_marker_valid(marker: int) -> bool:
        return marker in MARKERS

    @property
    def size(self) -> int:
        return len(self.get_full_segment())

    def get_full_segment(self) -> bytes:
        if self.data_size == self.length:
            return self.marker + self.data
        else:
            return self.marker + struct.pack(">H", self.length) + self.data


# Key: the byte marker 0xffxx
# Values:
#   0: marker name
#   1: size in bytes
#      >=0 for known size.
#      -1 for variable size where the length is after their marker.
#      -2 for variable size where no length is given.
MARKERS: dict[int, tuple[str, int]] = {
    0xD8: ("SOI", 0),
    0xC0: ("SOF0", -1),
    0xC2: ("SOF2", -1),
    0xC4: ("DHT", -1),
    0xDB: ("DQT", -1),
    0xDD: ("DRI", 4),
    0xDA: ("SOS", -2),
    0xD0: ("RST0", 0),
    0xD1: ("RST1", 0),
    0xD2: ("RST2", 0),
    0xD3: ("RST3", 0),
    0xD4: ("RST4", 0),
    0xD5: ("RST5", 0),
    0xD6: ("RST6", 0),
    0xD7: ("RST7", 0),
    0xE0: ("APP0", -1),
    0xE1: ("APP1", -1),
    0xE2: ("APP2", -1),
    0xE3: ("APP3", -1),
    0xE4: ("APP4", -1),
    0xE5: ("APP5", -1),
    0xFE: ("COM", -1),
    0xD9: ("EOI", 0),
}
