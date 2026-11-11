from .metadata import Metadata


class Jfxx(Metadata):
    signature = b"JFXX\x00"
    name = "JFIF extension"
