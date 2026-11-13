import sys

from src.objects import Jpeg
from src.objects.metadata import XmpExtensionFragment, XmpStandard

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

xmp_extended_guid = xmp_standard.get_attribute(".//rdf:Description", "xmpNote:HasExtendedXMP")
print(xmp_extended_guid)

xmp_extension: list[XmpExtensionFragment] = []
for segment in jpeg.image.segments:
    if isinstance(segment.data, XmpExtensionFragment):
        xmp_extension.append(segment.data)

print(xmp_extension)
