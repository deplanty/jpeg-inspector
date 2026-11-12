from src.objects import Jpeg
from src.objects.metadata import XmpStandard

filename = "data-test/example_art.MP.jpg"
jpeg = Jpeg(filename)
jpeg.parse()

xmp: XmpStandard | None = None
for segment in jpeg.image.segments:
    if isinstance(segment.data, XmpStandard):
        xmp = segment.data
        break

if xmp is not None:
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhoto")
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhotoVersion")
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhotoPresentationTimestampUs")

    xmp.remove_elements(".//Container:Item", {"Item:Semantic": "MotionPhoto"})

jpeg.save("data-test/tmp.jpg")
