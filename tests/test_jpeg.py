from src.objects import Jpeg


def test_parse_flower():
    filename = "./tests/data/flower.jpg"
    jpeg = Jpeg(filename)
    jpeg.parse()
    assert len(jpeg.image.segments) == 26

    # Get image size
    with jpeg.path.open("rb") as fid:
        fid.seek(0, 2)
        jpeg_size = fid.tell()
    assert len(jpeg) == jpeg_size
    # The file does not have extra data
    assert len(jpeg.image) == jpeg_size
    assert jpeg.extra_data.as_bytes() == b""


def test_parse_art_mp():
    filename = "./tests/data/art.MP.jpg"
    jpeg = Jpeg(filename)
    jpeg.parse()
    assert "GainMap" in jpeg.xmp_data
    assert "MotionPhoto" in jpeg.xmp_data
