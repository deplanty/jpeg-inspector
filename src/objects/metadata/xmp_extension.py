from .metadata import Metadata


class XmpExtension(Metadata):
    signature = b"http://ns.adobe.com/xmp/extension/\x00"
    name = "XMP extension"
