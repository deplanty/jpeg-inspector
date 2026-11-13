import sys

from src.objects import Jpeg
from src.objects.metadata import XmpExtension, XmpExtensionFragment, XmpStandard

filename = "data-test/example_art.MP.jpg"
jpeg = Jpeg(filename)
jpeg.parse()

# Find the XMP Standard Metadata
xmp_standard: XmpStandard | None = None
for segment in jpeg.image.segments:
    if isinstance(segment.data, XmpStandard):
        xmp_standard = segment.data
        break
if xmp_standard is None:
    sys.exit()

xmp_extension_guid = xmp_standard.get_attribute(".//rdf:Description", "xmpNote:HasExtendedXMP")


fragments: list[XmpExtensionFragment] = []
for segment in jpeg.image.segments:
    if isinstance(segment.data, XmpExtensionFragment):
        fragments.append(segment.data)

xmp_extension = XmpExtension.from_fragments(fragments)
xmp_extension.remove_attribute(".//rdf:Description", "GCamera:HdrPlusMakernote")
print(xmp_extension.payload.decode())
