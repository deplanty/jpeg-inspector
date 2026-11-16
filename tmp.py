import sys

from src.objects import Jpeg, Segment
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

xmp_extension_segments: list[Segment] = []
for segment in jpeg.image.segments:
    if isinstance(segment.data, XmpExtensionFragment):
        xmp_extension_segments.append(segment)

# Remove Extended XMP fragments for jpeg image
for segment in xmp_extension_segments:
    jpeg.image.segments.remove(segment)
# Create the full Extended XMP from the fragments
xmp_extension = XmpExtension.from_fragments([segment.data for segment in xmp_extension_segments])

# Remove the HdrPlusMakernote attribute
if xmp_extension.has_attribute(".//rdf:Description", "GCamera:HdrPlusMakernote") is not None:
    xmp_extension.remove_attribute(".//rdf:Description", "GCamera:HdrPlusMakernote")
    fragments = xmp_extension.to_fragments()
    # Set the new fragments in tje jpeg image
    for fragment in fragments:
        jpeg.image.segments.append(Segment.from_metadata("APP1", fragment))
    xmp_standard.set_attribute(".//rdf:Description", "xmpNote:HasExtendedXMP", xmp_extension.guid)
jpeg.image.sort_segments()
jpeg.save("data-test/tmp.jpg")
# print(xmp_extension.payload.decode())
