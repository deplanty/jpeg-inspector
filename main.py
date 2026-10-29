import argparse
import sys

from src.jpeg import Jpeg


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse the JPEG files to show their structure and their metadata."
    )
    parser.add_argument("filenames", nargs="+", help="The JPEG files to parse.")

    if len(sys.argv) == 1:
        filenames = ["data-test/example_art.jpg"]
    else:
        args: argparse.Namespace = parser.parse_args()
        filenames = args.filenames

    print("--- JPEG Inspector ---")
    print()

    # Preload the files
    images: list[Jpeg] = []
    for filename in filenames:
        image = Jpeg(filename)
        if image.is_valid_jpeg():
            images.append(image)
        else:
            print(f"{image.path.absolute()} is skipped: not a valid JPEG.")

    print(f"There are {len(filenames)} files to parse.")
    print(f"{len(images)} are JPEG, {len(filenames) - len(images)} are skipped.")

    if len(images) <= 10:
        for image in images:
            print("  -", image.path.absolute())

    print()
    print("This tool has several choices:")
    print("1: Remove all metadata in a duplicated file. (output_name -> filename.clean.jpg)")
    print(
        "2: Remove Motion Picture metadata in a duplicated file. "
        "(output_name -> filename.clean.jpg)"
    )
    print("Else: Quit.")
    answer = input("Your choice: ")

    if answer == "1":
        for image in images:
            image.remove_metadata()
    elif answer == "3":
        for image in images:
            image.remove_motion_photo()

    input("\nPress Enter to quit...")
