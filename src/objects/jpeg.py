from pathlib import Path

from src.objects.metadata import Metadata, XmpStandard

from .jpeg_image import JpegImage
from .segment import Segment


class Jpeg:
    def __init__(self, filename: str | Path):
        self.path: Path = Path(filename)
        self.image: JpegImage
        self.extra_data: Metadata

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

        with self.path.open("rb") as fid:
            self.image = JpegImage.parse(fid)

            # Some Jpeg files have more data after EOI
            self.extra_data = Metadata(fid.read())

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
            if b'GCamera:MotionPhoto="1"' in segment.data:
                return True
        return False
