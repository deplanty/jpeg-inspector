from .exif import Exif
from .icc_profile import IccProfile
from .jfif import Jfif
from .jfxx import Jfxx
from .metadata import Metadata
from .mpf import Mpf
from .xmp_extension import XmpExtension
from .xmp_standard import XmpStandard


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
    elif XmpExtension.has_signature(data):
        return XmpExtension(data)
    elif XmpStandard.has_signature(data):
        return XmpStandard(data)
    else:
        return Metadata(data)
