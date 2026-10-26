import sys

from src.jpeg import Jpeg

if __name__ == "__main__":
    if len(sys.argv) == 1:
        filename = "data-test/example_art.MP.jpg"
    else:
        filename = sys.argv[1]

    image = Jpeg(filename)
    print("INSPECT")
    print()
    image.inspect()
    print()
    print("REMOVE METADATA")
    print()
    image.remove_metadata()
