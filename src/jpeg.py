from pathlib import Path

from .segment import Segment


class Jpeg:
    def __init__(self, filename: str):
        self.path: Path = Path(filename)
        self.segments: list[Segment] = []
        self.data_extra: bytes = b""

        data = self.path.read_bytes()
        self.size_data = len(data)

        # Check if the file is a valid JPEG
        if data[:2] != b"\xff\xd8":
            raise Exception(f"{self.path} is not a valid JPEG.")

        # Parse the file to find the markers and their data
        index = 0
        while index < self.size_data:
            segment = Segment.parse(data, index)
            index += segment.size
            self.segments.append(segment)

            # The parser reached the end of the image
            if segment.name == "EOI":
                break

        self.data_extra = data[index:]

    def inspect(self):
        """
        Print the structure of the JPEG file.
        """

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
