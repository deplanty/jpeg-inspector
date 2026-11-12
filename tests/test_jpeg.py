from src.objects import Jpeg


def test_load_jpeg():
    filename = "./tests/data/flower.jpg"
    jpeg = Jpeg(filename)
    jpeg.parse()
    assert len(jpeg.image.segments) == 26
    assert jpeg.size_data == len(jpeg.image)
    assert jpeg.extra_data == b""
