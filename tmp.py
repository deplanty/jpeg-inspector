from src.objects import Jpeg
from src.objects.metadata import XmpStandard

filename = "data-test/example_art.MP.jpg"
# filename = "data-test/tmp.jpg"
jpeg = Jpeg(filename)
jpeg.parse()

if "MotionPhoto" in jpeg.xmp_data:
    # Find the XMP Standard segment
    xmp: XmpStandard | None = None
    for segment in jpeg.image.segments:
        if isinstance(segment.data, XmpStandard):
            xmp = segment.data
            break

    # Remove the attributes associated with the MotionPhoto
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhoto")
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhotoVersion")
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhotoPresentationTimestampUs")
    # Remove the Container:Item for the MotionPhoto
    xmp.remove_elements('.//rdf:li/Container:Item[@Item:Semantic="MotionPhoto"]/..')
    # Remove the data of the MotionPhoto
    jpeg.xmp_data.pop("MotionPhoto")

jpeg.save("data-test/tmp.jpg")
