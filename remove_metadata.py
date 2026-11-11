import argparse
from pathlib import Path

from src.objects import Jpeg


def remove_metadata(image: Jpeg):
    """
    Export a new image without the metadata.
    The exported image is path/to/image.clean.jpg
    """

    image.parse()

    output = image.path.with_stem(image.path.stem + ".clean")
    with output.open("wb") as fid:
        for segment in image.segments:
            if segment.name.startswith("APP") or segment.name == "COM":
                continue

            fid.write(segment.get_full_segment())

    print("Inout file: ", image.path.absolute())
    print("Input size: ", image.size_data, "bytes")
    print("Output file:", output.absolute())
    print("Output size:", len(output.read_bytes()), "bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse the JPEG files to show their structure and their metadata."
    )
    parser.add_argument("paths", nargs="+", help="The JPEG files or directories to parse.")

    args: argparse.Namespace = parser.parse_args()

    # Process the filenames to extract all the paths
    paths: list[Path] = []
    for filename in args.paths:
        path = Path(filename)
        if path.is_dir():
            paths.extend(path.rglob("*.jp*"))
        elif path.is_file():
            paths.append(path)
        else:
            raise ValueError(f"Path {path} is unknown.")

    # Preload the files
    images: list[Jpeg] = []
    for path in paths:
        image = Jpeg(path)
        if image.is_valid_jpeg():
            images.append(image)
        else:
            print(f"{image.path.absolute()} is skipped: not a valid JPEG.")

    print(f"There are {len(paths)} JPEG files to parse.")

    if len(images) <= 10:
        for image in images:
            print("  -", image.path.absolute())

    for image in images:
        remove_metadata(image)
