from pathlib import Path
from typing import Any

from src.objects.metadata import Metadata, XmpStandard

from .jpeg_image import JpegImage
from .segment import Segment


class Jpeg:
    def __init__(self, filename: str | Path):
        self.path: Path = Path(filename)
        self.image: JpegImage
        self.xmp_data: dict[str, Any] = {}
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
            # Parse the main image
            self.image = JpegImage.parse(fid)

            # Check for additional data in the file
            xmp: XmpStandard | None = None
            for segment in self.image.segments:
                if isinstance(segment.data, XmpStandard):
                    xmp = segment.data
                    break

            if xmp:
                for xmp_item in xmp.items:
                    # Skip XMP Item with a negative length because it's the main image
                    if xmp_item.length == -1:
                        continue
                    # Parse the Jpeg images (gain map for ultra HDR, ...)
                    if xmp_item.mime == "image/jpeg":
                        image = JpegImage.parse(fid)
                        self.xmp_data[xmp_item.semantic] = image
                    # Parse the videos (Motion Photo, ...)
                    elif xmp_item.mime == "video/mp4":
                        self.xmp_data[xmp_item.semantic] = Metadata(fid.read(xmp_item.length))

                    # Skip the padding after the data
                    fid.read(xmp_item.padding)

            # Some Jpeg files have more data after EOI
            self.extra_data = Metadata(fid.read())

    def save(self, filename: str | Path):
        output: Path = Path(filename)
        with output.open("wb") as fid:
            # Write the main image
            fid.write(self.image.as_bytes())
            # Write the extra data found in the XMP Standard segment
            for xmp_data in self.xmp_data.values():
                if isinstance(xmp_data, (Metadata, JpegImage)):
                    fid.write(xmp_data.as_bytes())
            # Write the additional data found
            fid.write(self.extra_data.as_bytes())

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
        for segment in self.image.segments:
            if not segment.name.startswith("APP"):
                continue
            if not segment.data.startswith(b"http://"):
                continue
            if b'GCamera:MotionPhoto="1"' in segment.data:
                return True
        return False
