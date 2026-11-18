from pathlib import Path
from typing import Any

from src.objects.metadata import Metadata, XmpStandard, XmpStandardItem

from .jpeg_image import JpegImage


class Jpeg:
    def __init__(self, filename: str | Path):
        self.path: Path = Path(filename)
        self.image: JpegImage
        self.xmp_data: dict[str, Any] = {}
        self.extra_data: Metadata

        self.__parsed = False

    def __len__(self) -> int:
        size: int = 0
        # Size of the main image
        size += len(self.image)
        # Size of all the extra data found in the XMP Standard segment
        for xmp_data in self.xmp_data.values():
            if isinstance(xmp_data, (Metadata, JpegImage)):
                size += len(xmp_data)
        # Size of the additional data found
        size += len(self.extra_data)

        return size

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

            # The index of the first byte after the main image
            extra_data_start: int = fid.tell()

            if xmp:
                # The Standard XMP associated data are stored at the end of the file. The data are
                # read backward.
                index_from_end: int = fid.seek(0, 2)
                xmp_item: XmpStandardItem
                for xmp_item in reversed(xmp.items):
                    index_from_end -= xmp_item.length
                    if xmp_item.length > 0:
                        xmp_item.offset = index_from_end

                # The extra data is between the main image and the Standard XMP data.
                extra_data_stop: int = index_from_end

                for xmp_item in xmp.items:
                    # Skip XMP Item without length
                    if xmp_item.length == 0:
                        continue
                    fid.seek(xmp_item.offset)
                    # Parse the Jpeg images (gain map for ultra HDR, ...)
                    if xmp_item.mime == "image/jpeg":
                        image = JpegImage.parse(fid)
                        self.xmp_data[xmp_item.semantic] = image
                    # Parse the videos (Motion Photo, ...)
                    elif xmp_item.mime == "video/mp4":
                        self.xmp_data[xmp_item.semantic] = Metadata(fid.read(xmp_item.length))

                    # Skip the padding after the data
                    fid.read(xmp_item.padding)
            else:
                extra_data_stop: int = fid.seek(0, 2)

            # Some Jpeg files have more data after EOI and before the Standard XMP data
            fid.seek(extra_data_start)
            self.extra_data = Metadata(fid.read(extra_data_stop - extra_data_start))

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

    def is_valid_jpeg(self) -> bool:
        """
        Return True if the file is a valid JPEG.
        The validation is done on the first header only.
        """

        with self.path.open("rb") as fid:
            header = fid.read(2)
        return header == b"\xff\xd8"
