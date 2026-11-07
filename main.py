import argparse
from pathlib import Path
import sys

from src.jpeg import Jpeg

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse the JPEG files to show their structure and their metadata."
    )
    parser.add_argument("paths", nargs="+", help="The JPEG files or directories to parse.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False, help="Show information.")

    if len(sys.argv) == 1:
        input_paths = ["data-test/example_art.jpg"]
        verbose = True
    else:
        args: argparse.Namespace = parser.parse_args()
        input_paths = args.paths
        verbose = args.verbose

    print("--- JPEG Inspector ---")
    print()

    # Process the filenames to extract all the paths
    paths: list[Path] = []
    for filename in input_paths:
        path = Path(filename)
        if path.is_dir():
            paths.extend(path.rglob("*.jp*"))
        elif path.is_file():
            paths.append(path)
        else:
            raise Exception(f"Path {path} is unknown.")

    # Preload the files
    images: list[Jpeg] = []
    for path in paths:
        image = Jpeg(path)
        if image.is_valid_jpeg():
            images.append(image)
        else:
            print(f"{image.path.absolute()} is skipped: not a valid JPEG.")

    print(f"There are {len(paths)} files to parse.")
    print(f"{len(images)} are JPEG, {len(paths) - len(images)} are skipped.")

    if len(images) <= 10:
        for image in images:
            print("  -", image.path.absolute())

    print()
    print("This tool has several choices:")
    print("1: Remove all metadata in a duplicated file. (output_name -> filename.clean.jpg)")
    print(
        "2: Remove Motion Picture metadata in a duplicated file. "
        "(output_name -> filename.static.jpg)"
    )
    print("Else: Quit.")
    answer = input("Your choice: ")

    if answer == "1":
        for image in images:
            image.remove_metadata()
    elif answer == "2":
        n = len(images)
        len_n = len(str(n))
        index = 0
        for image in images:
            index += 1
            print(f"{index:>{len_n}}/{n} ", end="")
            if image.has_motion_photo():
                output = image.remove_motion_photo(verbose)
                print("Done", image.path.name, "->", output.name)
            else:
                print("Skip", image.path)

    input("\nPress Enter to quit...")
