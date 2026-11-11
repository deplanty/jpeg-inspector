from .metadata import Metadata


class Jfif(Metadata):
    signature = b"JFIF\x00"
    name = "JFIF"
