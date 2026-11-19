from .exif import Exif
from .icc_profile import IccProfile
from .jfif import Jfif
from .jfxx import Jfxx
from .metadata import Metadata
from .mpf import Mpf
from .xmp_extended import ExtendedXmp as ExtendedXmp
from .xmp_extended import ExtendedXmpFragment
from .xmp_standard import StandardXmp
from .xmp_standard import StandardXmpItem as StandardXmpItem


def get(data: bytes) -> Metadata:
    if Exif.has_signature(data):
        return Exif(data)
    elif IccProfile.has_signature(data):
        return IccProfile(data)
    elif Jfif.has_signature(data):
        return Jfif(data)
    elif Jfxx.has_signature(data):
        return Jfxx(data)
    elif Mpf.has_signature(data):
        return Mpf(data)
    elif ExtendedXmpFragment.has_signature(data):
        return ExtendedXmpFragment(data)
    elif StandardXmp.has_signature(data):
        return StandardXmp(data)
    else:
        return Metadata(data)
