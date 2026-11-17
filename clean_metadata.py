import argparse
from collections.abc import Callable
from pathlib import Path

from src.objects import Jpeg, Segment
from src.objects.metadata import XmpExtension, XmpExtensionFragment, XmpStandard


def remove_motion_photo(jpeg: Jpeg, verbose: bool) -> bool:
    """Return True is a change has been done"""

    # Check if the MotionPhoto is in the file
    if "MotionPhoto" not in jpeg.xmp_data:
        if verbose:
            print("MotionPhoto not found in Standard XMP.")
        return False

    # Find the XMP Standard segment
    xmp: XmpStandard | None = None
    for segment in jpeg.image.segments:
        if isinstance(segment.data, XmpStandard):
            xmp = segment.data
            break

    if xmp is None:
        if verbose:
            print("Standard XMP not found.")
        return False

    # Remove the attributes associated with the MotionPhoto
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhoto")
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhotoVersion")
    xmp.remove_attribute(".//rdf:Description", "GCamera:MotionPhotoPresentationTimestampUs")
    # Remove the Container:Item for the MotionPhoto
    xmp.remove_elements('.//rdf:li/Container:Item[@Item:Semantic="MotionPhoto"]/..')
    # Remove the data of the MotionPhoto
    jpeg.xmp_data.pop("MotionPhoto")

    return True


def remove_hdr_plus_makernote(jpeg: Jpeg, verbose: bool) -> bool:
    """Return True is a change has been done"""

    # Find the Standard XMP Metadata
    xmp_standard: XmpStandard | None = None
    for segment in jpeg.image.segments:
        if isinstance(segment.data, XmpStandard):
            xmp_standard = segment.data
            break
    if xmp_standard is None:
        if verbose:
            print("Standard XMP not found.")
        return False

    # Check if the Standard XMP mentions Extended XMP
    has_xmp_extension: bool = xmp_standard.has_attribute(
        ".//rdf:Description", "xmpNote:HasExtendedXMP"
    )
    if not has_xmp_extension:
        if verbose:
            print("Extended XMP not found.")
        return False

    # Fetch all the Extended XMP fragments
    xmp_extension_segments: list[Segment] = []
    for segment in jpeg.image.segments:
        if isinstance(segment.data, XmpExtensionFragment):
            xmp_extension_segments.append(segment)

    # Create the full Extended XMP from the fragments
    xmp_extension: XmpExtension = XmpExtension.from_fragments(
        [segment.data for segment in xmp_extension_segments]
    )

    # Check if the Extended XMP has HdrPlusMakernote
    if not xmp_extension.has_attribute(".//rdf:Description", "GCamera:HdrPlusMakernote"):
        if verbose:
            print("HdrPlusMakernote not found in Extended XMP.")
        return False

    # Remove the HdrPlusMakernote attribute
    xmp_extension.remove_attribute(".//rdf:Description", "GCamera:HdrPlusMakernote")

    # Remove the old Extended XMP fragments
    for segment in xmp_extension_segments:
        jpeg.image.segments.remove(segment)

    # Fragment the Extended XMP and set the new fragments in the jpeg image
    fragments = xmp_extension.to_fragments()
    for fragment in fragments:
        jpeg.image.segments.append(Segment.from_metadata("APP1", fragment))
    # Update the Standard XMP with the new GUID of the Extended XMP
    xmp_standard.set_attribute(".//rdf:Description", "xmpNote:HasExtendedXMP", xmp_extension.guid)

    return True


def process_jpeg(jpeg: Jpeg, dry: bool = False, verbose: bool = False) -> Path | None:
    """
    Export a new image without the metadata associated with Motion Photo.
    If the initial image ends with .MP.jpg export as path/to/image.jpg.
    Else, export the image as path/to/image.static.jpg

    If dry is True, only show information without creating output images.
    If verbose is True, print information about the input and output images.

    Return the path of the output image.
    """

    jpeg.parse()

    if jpeg.path.stem.endswith(".MP"):
        stem = Path(jpeg.path.stem).stem
        output = jpeg.path.with_stem(stem)
    else:
        output = jpeg.path.with_stem(jpeg.path.stem + ".clean")

    if verbose:
        print("Input file: ", jpeg.path.absolute())
        print("Input size: ", len(jpeg), "bytes")

    # Run the pipeline to remove the desired metadata
    pipeline: list[Callable] = [remove_motion_photo, remove_hdr_plus_makernote]
    changed: list[bool] = []
    for func in pipeline:
        change = func(jpeg, verbose)
        changed.append(change)
    jpeg.image.sort_segments()

    # If a change has occured during the pipeline
    if not any(changed):
        if verbose:
            print("No change: skip")
        return None

    if verbose:
        print("Output file:", output.absolute())

    if dry:
        if verbose:
            print("Output size:", len(jpeg), "bytes")
        return output.absolute()

    # Write the output jpeg file
    jpeg.save(output)

    # Show information about the output images
    if verbose:
        print("Output size:", len(jpeg), "bytes")
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
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Show more information about what's happening.",
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
    jpeg_files: list[Jpeg] = []
    for path in paths:
        jpeg = Jpeg(path)
        if jpeg.is_valid_jpeg():
            jpeg_files.append(jpeg)
        else:
            print(f"{jpeg.path.absolute()} is skipped: not a valid JPEG.")

    print(f"There are {len(paths)} JPEG files to parse.")

    if len(jpeg_files) <= 10:
        for jpeg in jpeg_files:
            print("  -", jpeg.path.absolute())
    print()

    # To show the current folder
    dir_current = ""
    # To show the progress
    progress_total = len(jpeg_files)
    for progress, jpeg in enumerate(jpeg_files, 1):
        # show current folder
        if dir_current != jpeg.path.parent:
            dir_current = jpeg.path.parent
            print(f"\nFolder: {dir_current}")
        # Show progress
        if args.verbose:
            print(f"  {progress:>{len(str(progress_total))}}/{progress_total}")
            output = process_jpeg(jpeg, args.dry, args.verbose)
        else:
            print(f"  {progress:>{len(str(progress_total))}}/{progress_total} ", end="")
            output = process_jpeg(jpeg, args.dry, args.verbose)
            if output is None:
                print(jpeg.path.name, "-> no change")
            else:
                print(jpeg.path.name, "->", output.name)
