from pathlib import Path

from src.objects.metadata import Metadata

from .segment import Segment


class InvalidJpegError(Exception):
    def __init__(self, path: str):
        super().__init__()
        self.path: str = path

    def __str__(self) -> str:
        return f"{self.path} is not a valid JPEG."


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

    # Commands

    def inspect(self):
        """
        Print the structure of the JPEG file.
        """

        self.parse()

        print("Filename:", self.path.absolute())
        print()
        print(f"{'Position': <8} | {'Marker': <6} | {'Segment size': <12}")
        print(f"{'-' * 8} | {'-' * 6} | {'-' * 12}")

        index = 0
        for segment in self.segments:
            print(f"{index:08x} | {segment.name: <6} | {segment.size: <12}")
            index += segment.size

        print()
        print("JPEG data size: ", index, "bytes")
        print("Extra data size:", len(self.data_extra), "bytes")
        print("Total size:     ", self.size_data, "bytes")

    def remove_metadata(self):
        """
        Export a new image without the metadata.
        The exported image is path/to/image.clean.jpg
        """

        self.parse()

        output = self.path.with_stem(self.path.stem + ".clean")
        with output.open("wb") as fid:
            for segment in self.segments:
                if segment.name.startswith("APP") or segment.name == "COM":
                    continue

                fid.write(segment.get_full_segment())

        print("Inout file: ", self.path.absolute())
        print("Input size: ", self.size_data, "bytes")
        print("Output file:", output.absolute())
        print("Output size:", len(output.read_bytes()), "bytes")

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

    def remove_motion_photo(self, dry: bool = False, verbose: bool = False) -> Path:
        """
        Export a new image without the metadata associated with Motion Photo.
        If the initial image ends with .MP.jpg export as path/to/image.jpg.
        Else, export the image as path/to/image.static.jpg

        If dry is True, only show information without creating output images.
        If verbose is True, print information about the input and output images.

        Return the path of the output image.
        """

        self.parse()

        if self.path.stem.endswith(".MP"):
            stem = Path(self.path.stem).stem
            output = self.path.with_stem(stem)
        else:
            output = self.path.with_stem(self.path.stem + ".static")

        if not dry:
            with output.open("wb") as fid:
                for segment in self.segments:
                    # Remove APP1 http://adobe metadata
                    if (
                        segment.name.startswith("APP1")
                        and segment.data.startswith(b"http://")
                        or segment.name.startswith("APP")
                        and segment.data.startswith(b"MPF")
                    ):
                        continue
                    # Write the segment
                    fid.write(segment.get_full_segment())

            # Show information about the input and output images
            if verbose:
                print("Input file: ", self.path.absolute())
                print("Input size: ", self.size_data, "bytes")
                print("Output file:", output.absolute())
                print("Output size:", len(output.read_bytes()), "bytes")

        return output.absolute()
