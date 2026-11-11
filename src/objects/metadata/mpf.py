from .metadata import Metadata


class Mpf(Metadata):
    signature = b"MPF\x00"
    name = "MPF"
