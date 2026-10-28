from pathlib import Path

from .segment import Segment


class Jpeg:
    def __init__(self, filename: str):
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
            raise Exception(f"{self.path} is not a valid JPEG.")

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

        self.data_extra = data[index:]

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
                if segment.name.startswith("APP"):
                    continue
                elif segment.name == "COM":
                    continue

                fid.write(segment.get_full_segment())

        print("Inout file: ", self.path.absolute())
        print("Input size: ", self.size_data, "bytes")
        print("Output file:", output.absolute())
        print("Output size:", len(output.read_bytes()), "bytes")

    def remove_motion_photo(self):
        """
        Export a new image without the metadata associated with Motion Photo.
        The exported image is path/to/image.clean.jpg
        """

        self.parse()

        output = self.path.with_stem(self.path.stem + ".clean")
        with output.open("wb") as fid:
            for segment in self.segments:
                if segment.name.startswith("APP"):
                    if segment.data[2:].startswith(b"http://"):
                        continue

                fid.write(segment.get_full_segment())

        print("Input file: ", self.path.absolute())
        print("Input size: ", self.size_data, "bytes")
        print("Output file:", output.absolute())
        print("Output size:", len(output.read_bytes()), "bytes")
