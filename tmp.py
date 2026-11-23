import sys

from src.objects import Jpeg, Segment
from src.objects.metadata import ExtendedXmp, ExtendedXmpFragment, StandardXmp

filename = "D:/Library/Photos/2013/2013_08_Corse/2013-08-22_17-01-12.jpg"
jpeg = Jpeg(filename)
jpeg.parse()

extra_data = jpeg.extra_data.as_bytes()
index = extra_data.find(b"\xff\xd8")
with open("data-test/tmp.jpg", "wb") as fid:
    fid.write(extra_data[index:])

# # Find the XMP Standard Metadata
# xmp_standard: StandardXmp | None = None
# for segment in jpeg.image.segments:
#     if isinstance(segment.data, StandardXmp):
#         xmp_standard = segment.data
#         break
# if xmp_standard is None:
#     sys.exit()
#
# xmp_extension_guid = xmp_standard.get_attribute(".//rdf:Description", "xmpNote:HasExtendedXMP")
#
# xmp_extension_segments: list[Segment] = []
# for segment in jpeg.image.segments:
#     if isinstance(segment.data, ExtendedXmpFragment):
#         xmp_extension_segments.append(segment)
#
# # Remove Extended XMP fragments for jpeg image
# for segment in xmp_extension_segments:
#     jpeg.image.segments.remove(segment)
# # Create the full Extended XMP from the fragments
# xmp_extension = ExtendedXmp.from_fragments([segment.data for segment in xmp_extension_segments])
