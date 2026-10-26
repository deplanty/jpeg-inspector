"""
Inspect the data contained in a JPEG file.
"""

import argparse
from pathlib import Path
import struct


P_POSITION_WIDTH = 8
P_MARKER_WIDTH = 8
P_SIZE_WIDTH = 8

# Key: the byte marker 0xffxx
# Values:
#   0: marker name
#   1: size in bytes
#      -1 for variable size where the length is after ther marker.
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


def inspect_jpg(filename: str):
    """
    Inspect the given JPEG file.
    Show its markers and sizes.
    """

    # Read the file and get its full size
    path = Path(filename)
    data = path.read_bytes()
    size_data = len(data)

    print("Filename:", path)
    print("File size:", size_data, "bytes")

    # Check if the file is a valid JPEG
    if data[:2] != b"\xff\xd8":
        raise Exception(f"{path} is not a valid JPEG.")

    print()
    print(
        f"{'Position': <{P_POSITION_WIDTH}} | {'Marker': <{P_MARKER_WIDTH}} | "
        f"{'Size': <{P_SIZE_WIDTH}}"
    )

    # Parse the file to find the markers and their data
    index = 0
    while index < size_data:
        # Check if the marker starts with 0xff
        if data[index] == 0xFF:
            index += 1
        else:
            raise Exception(f"Invalid byte at position {index:08x}: {hex(data[index])}.")
        # Check if the marker is known
        if data[index] not in MARKERS:
            raise Exception(f"Marker {data[index]:02x} is unknown.")

        marker, size_marker = MARKERS[data[index]]
        index += 1

        # The marker has no size (e.g. SOI and EOI)
        if size_marker == 0:
            pass
        # The marker has a variable size given by the next 2 bytes
        if size_marker == -1:
            # How to read: https://www.media.mit.edu/pia/Research/deepview/exif.html
            # 0xFF+Marker Number(1 byte) + Data size(2 bytes) + Data(n bytes)
            # Example: FF C1 00 0C
            # It means this Marker (0xFFC1) has 0x000C (equal 12) bytes of data. But the data size
            # '12' includes "Data size" descriptor, it follows only 10 bytes of data after 0x000C.
            size_marker, *_ = struct.unpack(">H", data[index : index + 2])
            index += 2
            size_marker -= 2
        # The marker has a variable size: from this marker to the next one
        if size_marker == -2:
            # The length of the data is not given. The data is between this marker and the next one.
            # In this data, if a 0xff value is followed by a 0x00 it is a value and not a new marker.
            start = index
            while index < size_data:
                if data[index] == 0xFF and data[index + 1] in MARKERS:
                    break
                index += 1
            size_marker = index - start
            index = start

        # The "index - 1" is to indicate the start of the marker. Here, index targets the 2nd byte
        # of the marker but it starts with 0xffxx.
        print(
            f"{index - 1:0{P_POSITION_WIDTH}x} | {marker: <{P_MARKER_WIDTH}} | "
            f"{size_marker: <{P_SIZE_WIDTH}}"
        )

        # Skip the data contained in the marker
        if size_marker > 0:
            # Check if the file can contain all the marker's data
            if index + size_marker > size_data:
                raise Exception(
                    f"The marker {marker} is incomplete. "
                    "The file ended before the end of the marker."
                )
            marker_data = data[index : index + size_marker]
            index += size_marker

            if marker.startswith("APP"):
                print(marker_data[:40])

        # The parser reached the end of the image
        if marker == "EOI":
            break

    size_rest = size_data - index
    print(
        f"{index:0{P_POSITION_WIDTH}x} | {'Rest': <{P_MARKER_WIDTH}} | "
        f"{size_rest: <{P_SIZE_WIDTH}}"
    )

    print()
    print(f"Image size: {index} bytes")
    # At the end of a JPEG file, manufacturers can add more data
    print(f"Rest of file: {size_rest} bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")

    args: argparse.Namespace = parser.parse_args()
    if args.filenames:
        for filename in args.filenames:
            inspect_jpg(filename)
            input("Press Enter to continue...")
    else:
        filename = "./example_flower.jpg"
        filename = "./example_art.jpg"
        filename = "./example_art.cleaned.jpg"
        inspect_jpg(filename)
