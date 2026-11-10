from dataclasses import dataclass
import struct


@dataclass
class Segment:
    #: The name of the marker (e.g. SOI)
    name: str
    #: The marker's bytes (e.g. 0xFFD8)
    marker: bytes
    #: The length of the marker's data (without the 2 bytes of the marker)
    length: int
    #: The size of the data (without the 2 bytes for the length when present)
    data_size: int
    #: The data contained in the marker (without the 2 bytes for the length when present)
    data: bytes = b""

    @classmethod
    def parse(cls, data: bytes, index: int) -> "Segment":
        marker = data[index : index + 2]
        name, length = MARKERS[marker[1]]
        index += 2

        # Info about reading the markers: https://www.media.mit.edu/pia/Research/deepview/exif.html
        # The marker has no size (e.g. SOI and EOI) or a given size (e.g. DRI)
        if length >= 0:
            data_size = length
        # The marker has a variable size given by the next 2 bytes
        elif length == -1:
            # Read 2 bytes of data: >H (big endian unsigned short)
            # The length contains the 2 bytes indicating the size of the data
            length, *_ = struct.unpack(">H", data[index : index + 2])
            data_size = length - 2
            index += 2
        # The marker has a variable size: from this marker to the next one
        elif length == -2:
            # The length of the data is not given. The data is between this marker and the next one.
            # In this data, if a 0xff value is followed by a 0x00 it is a value and not a new marker.
            start = index
            while index < len(data):
                if data[index] == 0xFF and cls.is_marker_valid(data[index + 1]):
                    break
                index += 1
            length = index - start
            data_size = length
            index = start

        # Check if the file can contain all the marker's data
        if index + length > len(data):
            raise Exception(
                f"The segment with marker {marker} is incomplete. "
                "The file ended before the end of the marker."
            )

        segment = cls(name, marker, length, data_size, data[index : index + data_size])
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
