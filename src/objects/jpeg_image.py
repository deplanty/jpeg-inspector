from typing import BinaryIO

from .segment import Segment


class JpegImage:
    def __init__(self, segments: list[Segment]):
        self.segments: list[Segment] = segments

    def __len__(self) -> int:
        return sum(len(segment) for segment in self.segments)

    @classmethod
    def parse(cls, fid: BinaryIO) -> "JpegImage":
        """
        Parse the file to load its data.
        """

        segments: list[Segment] = []

        # Parse the file to find the markers and their data
        while True:
            segment = Segment.parse(fid)
            segments.append(segment)
            # The parser reached the end of the image
            if segment.name == "EOI":
                break

        return cls(segments)
