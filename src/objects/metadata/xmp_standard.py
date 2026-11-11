from .metadata import Metadata


class XmpStandard(Metadata):
    signature = b"http://ns.adobe.com/xap/1.0/\x00"
    name = "XMP standard"
