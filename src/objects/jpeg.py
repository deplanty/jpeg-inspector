from pathlib import Path

from src.objects.metadata import Metadata
from src.utils.exceptions import InvalidJpegError

from .segment import Segment


class Jpeg:
    def __init__(self, filename: str | Path):
        self.path: Path = Path(filename)
        self.segments: list[Segment] = []
        self.data_extra: bytes = b""

        with self.path.open("r") as fid:
            fid.seek(0, 2)  # End of file
            self.size_data = fid.tell()

        self.__parsed = False

    # Public methods
    def parse(self, force=False):
        """
        Parse the file to load its data.
        Do not load twice the data unless forced.
        """

        if self.__parsed and not force:
            return

        self.segments.clear()
        self.data_extra = b""

        # Check if the file is a valid JPEG
        if not self.is_valid_jpeg():
            raise InvalidJpegError(str(self.path))

        # Parse the file to find the markers and their data
        data = self.path.read_bytes()
        index = 0
        while index < self.size_data:
            segment = Segment.parse(data, index)
            index += segment.size
            self.segments.append(segment)

            # The parser reached the end of the image
            if segment.name == "EOI":
                break

        self.data_extra = Metadata(data[index:])

    # Tools

    def is_valid_jpeg(self) -> bool:
        """
        Return True if the file is a valid JPEG.
        The validation is done on the first header only.
        """

        with self.path.open("rb") as fid:
            header = fid.read(2)
        return header == b"\xff\xd8"

    def has_motion_photo(self) -> bool:
        """
        Return True if the image has some metadata associated with Motion Photo.
        """

        self.parse()
        segment: Segment
        for segment in self.segments:
            if not segment.name.startswith("APP"):
                continue
            if not segment.data.startswith(b"http://"):
                continue
            if b"GCamera:MotionPhoto" in segment.data:
                return True
        return False
