import argparse
from pathlib import Path

from src.jpeg import Jpeg

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

    print("--- JPEG Inspector ---")
    print()

    # Process the filenames to extract all the paths
    paths: list[Path] = []
    for filename in args.paths:
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

    print(f"There are {len(paths)} JPEG files to parse.")

    if len(images) <= 10:
        for image in images:
            print("  -", image.path.absolute())

    print()
    print("This tool has several choices:")
    print("1: Remove all metadata in a duplicated file. (output_name -> filename.clean.jpg)")
    print("2: Check if the images contains Motion Photo.")
    print(
        "3: Remove Motion Picture metadata in a duplicated file. "
        "(output_name -> filename.static.jpg)"
    )
    print("Else: Quit.")
    print()
    answer = input("Your choice: ")
    print()

    if answer == "1":
        for image in images:
            image.remove_metadata()
    elif answer == "2":
        # To show the current folder
        dir_current = images[0].path.parent
        print(dir_current)
        # To show the progress
        progress_total = len(images)
        progress = 0
        for image in images:
            # show current folder
            if dir_current != image.path.parent:
                dir_current = image.path.parent
                print(dir_current)
            # Show progress
            progress += 1
            print(
                f"  {progress:>{len(str(progress_total))}}/{progress_total} "
                f"{image.path.name} {image.has_motion_photo()}"
            )
    elif answer == "3":
        # To show the current folder
        dir_current = images[0].path.parent
        print(dir_current)
        # To show the progress
        progress_total = len(images)
        progress = 0
        for image in images:
            # show current folder
            if dir_current != image.path.parent:
                dir_current = image.path.parent
                print(dir_current)
            # Show progress
            progress += 1
            print(f"  {progress:>{len(str(progress_total))}}/{progress_total} ", end="")
            if image.has_motion_photo():
                output = image.remove_motion_photo(args.dry, args.verbose)
                print(image.path.name, "->", output.name)
            else:
                print(image.path.name, " -> Skip")
