from src.objects import Jpeg


def test_parse_flower():
    filename = "./tests/data/flower.jpg"
    jpeg = Jpeg(filename)
    jpeg.parse()
    assert len(jpeg.image.segments) == 26
    assert jpeg.size_data == len(jpeg.image)
    assert jpeg.extra_data == b""


def test_parse_art_mp():
    filename = "./tests/data/art.MP.jpg"
    jpeg = Jpeg(filename)
    jpeg.parse()
    assert "GainMap" in jpeg.xmp_data
    assert "MotionPhoto" in jpeg.xmp_data
