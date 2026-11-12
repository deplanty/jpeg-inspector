from src.objects import Jpeg

filename = "data-test/example_art.MP.jpg"
jpeg = Jpeg(filename)
jpeg.parse()
jpeg.save("data-test/tmp.jpg")
