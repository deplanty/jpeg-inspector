from .metadata import Metadata


class Exif(Metadata):
    signature = b"Exif\x00\x00"
    name = "EXIF"
