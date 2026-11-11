from .metadata import Metadata


class IccProfile(Metadata):
    signature = b"ICC_PROFILE\x00"
    name = "ICC_PROFILE"
