import argparse
from pathlib import Path

from src.objects import Jpeg


def remove_motion_photo(image: Jpeg, dry: bool = False, verbose: bool = False) -> Path:
    """
    Export a new image without the metadata associated with Motion Photo.
    If the initial image ends with .MP.jpg export as path/to/image.jpg.
    Else, export the image as path/to/image.static.jpg

    If dry is True, only show information without creating output images.
    If verbose is True, print information about the input and output images.

    Return the path of the output image.
    """

    image.parse()

    if image.path.stem.endswith(".MP"):
        stem = Path(image.path.stem).stem
        output = image.path.with_stem(stem)
    else:
        output = image.path.with_stem(image.path.stem + ".static")

    if not dry:
        with output.open("wb") as fid:
            for segment in image.segments:
                # Remove APP1 http://adobe metadata
                if (
                    segment.name.startswith("APP1")
                    and segment.data.startswith(b"http://")
                    or segment.name.startswith("APP")
                    and segment.data.startswith(b"MPF")
                ):
                    continue
                # Write the segment
                fid.write(segment.get_full_segment())

        # Show information about the input and output images
        if verbose:
            print("Input file: ", image.path.absolute())
            print("Input size: ", image.size_data, "bytes")
            print("Output file:", output.absolute())
            print("Output size:", len(output.read_bytes()), "bytes")

    return output.absolute()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse the JPEG files to show their structure and their metadata."
    )
    parser.add_argument("paths", nargs="+", help="The JPEG files or directories to parse.")
    parser.add_argument(
        "-d",
        "--dry",
        action="store_true",
        default=False,
        help="Run the process without doing anything.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False, help="Show information."
    )

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

    # To show the current folder
    dir_current = ""
    # To show the progress
    progress_total = len(images)
    for progress, image in enumerate(images):
        # show current folder
        if dir_current != image.path.parent:
            dir_current = image.path.parent
            print(dir_current)
        # Show progress
        print(f"  {progress:>{len(str(progress_total))}}/{progress_total} ", end="")
        if image.has_motion_photo():
            output = remove_motion_photo(image, args.dry, args.verbose)
            print(image.path.name, "->", output.name)
        else:
            print(image.path.name, " -> Skip")
