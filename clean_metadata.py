import argparse
import time
from collections.abc import Callable
from pathlib import Path

from rich.progress import track

from src.objects import Jpeg, Segment
from src.objects.metadata import ExtendedXmp, ExtendedXmpFragment, Metadata, StandardXmp

SYM_OK: str = "\033[92m✓\033[0m"
SYM_NOT_OK: str = "\033[91m✗\033[0m"
SYM_ARROW: str = "\033[96m→\033[0m"
VERBOSE: bool = False


def print_verbose(text: str, **kwargs) -> None:
    if VERBOSE:
        print(text, **kwargs)


def remove_motion_photo(jpeg: Jpeg) -> bool:
    """
    Remove:
        - GCamera:MotionPhoto
        - GCamera:MotionPhotoVersion
        - GCamera:MotionPhotoPresentationTimestampUs
    Return True is a change has been done
    """

    # Check if the MotionPhoto is in the file
    if "MotionPhoto" not in jpeg.xmp_data:
        print_verbose(f"{SYM_NOT_OK} MotionPhoto not found in Standard XMP.")
        return False

    # Find the XMP Standard segment
    xmp: StandardXmp | None = None
    for segment in jpeg.image.segments:
        if isinstance(segment.data, StandardXmp):
            xmp = segment.data
            break

    if xmp is None:
        print_verbose(f"{SYM_NOT_OK} Standard XMP not found.")
        return False

    # Try to remove the attributes associated with the MotionPhoto
    to_remove: list[tuple[str, str]] = [
        (".//rdf:Description", "GCamera:MotionPhoto"),
        (".//rdf:Description", "GCamera:MotionPhotoVersion"),
        (".//rdf:Description", "GCamera:MotionPhotoPresentationTimestampUs"),
    ]
    for xpath, attribute in to_remove:
        # Check if the Standard XMP has the attribute and remove it
        if xmp.has_attribute(xpath, attribute):
            xmp.remove_attribute(xpath, attribute)
            print_verbose(f"{SYM_OK} {attribute} removed from Standard XMP.")
        else:
            print_verbose(f"{SYM_NOT_OK} {attribute} not found in Standard XMP.")

    if xmp.has_element('.//rdf:li/Container:Item[@Item:Semantic="MotionPhoto"]/..'):
        # Remove the rdf:li with Container:Item for the MotionPhoto
        xmp.remove_elements('.//rdf:li/Container:Item[@Item:Semantic="MotionPhoto"]/..')
        # Remove the data of the MotionPhoto
        jpeg.xmp_data.pop("MotionPhoto")
        print_verbose(f"{SYM_OK} MotionPhoto removed from Standard XMP")
    else:
        print_verbose(f"{SYM_NOT_OK} Container:Item for the MotionPhoto not found in Standard XMP")

    return True


def remove_hdr_makernote(jpeg: Jpeg) -> bool:
    """
    Remove:
        - GCamera:HdrPlusMakernote from recent HDR+ format
        - GCamera:hdrp_makernote from old HDR+ format
        - GCamera:shot_log_data linked with hdrp_makernote
    Return True is a change has been done
    """

    # Find the Standard XMP Metadata
    xmp_standard: StandardXmp | None = None
    for segment in jpeg.image.segments:
        if isinstance(segment.data, StandardXmp):
            xmp_standard = segment.data
            break
    if xmp_standard is None:
        print_verbose(f"{SYM_NOT_OK} Standard XMP not found.")
        return False

    # Check if the Standard XMP mentions Extended XMP
    has_xmp_extension: bool = xmp_standard.has_attribute(
        ".//rdf:Description", "xmpNote:HasExtendedXMP"
    )
    if not has_xmp_extension:
        print_verbose(f"{SYM_NOT_OK} Extended XMP not found.")
        return False

    # Fetch all the Extended XMP fragments
    xmp_extension_segments: list[Segment] = []
    for segment in jpeg.image.segments:
        if isinstance(segment.data, ExtendedXmpFragment):
            xmp_extension_segments.append(segment)

    # Create the full Extended XMP from the fragments
    xmp_extension: ExtendedXmp = ExtendedXmp.from_fragments(
        [segment.data for segment in xmp_extension_segments]
    )

    # Try to remove several attributes
    change: bool = False
    to_remove: list[tuple[str, str]] = [
        (".//rdf:Description", "GCamera:HdrPlusMakernote"),
        (".//rdf:Description", "GCamera:hdrp_makernote"),
        (".//rdf:Description", "GCamera:shot_log_data"),
    ]
    for xpath, attribute in to_remove:
        # Check if the Extended XMP has the attribute and remove it
        if xmp_extension.has_attribute(xpath, attribute):
            xmp_extension.remove_attribute(xpath, attribute)
            change = True
            print_verbose(f"{SYM_OK} {attribute} removed from Extended XMP.")
        else:
            print_verbose(f"{SYM_NOT_OK} {attribute} not found in Extended XMP.")

    if not change:
        return False

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


def remove_extra_data(jpeg: Jpeg) -> bool:
    """
    Remove:
        - jpeg.extra_data
    Return True is a change has been done
    """

    if jpeg.extra_data.as_bytes() == b"":
        print_verbose(f"{SYM_NOT_OK} Extra data not found.")
        return False
    else:
        jpeg.extra_data = Metadata(b"")
        print_verbose(f"{SYM_OK} Extra data removed.")
        return True


def process_jpeg(jpeg: Jpeg, dry: bool = False) -> tuple[Path | None, int, int]:
    """
    Export a new image without the metadata associated with Motion Photo.
    If the initial image ends with .MP.jpg export as path/to/image.jpg.
    Else, export the image as path/to/image.static.jpg

    If dry is True, only show information without creating output images.

    Return the path of the output image, the size of the input and the size of the output images.
    """

    suffix: str = ".clean"

    # Ignore files already cleaned
    print_verbose(f"Input file: {jpeg.path.absolute()}")
    if jpeg.path.stem.endswith(suffix):
        print_verbose(f"{SYM_ARROW} File already cleaned")
        return None, 0, 0

    jpeg.parse()
    size_input = len(jpeg)
    print_verbose(f"Input size: {size_input:,d} bytes")

    # Add a .clean suffix to the filename to identify which files have been modified
    output = jpeg.path.with_stem(jpeg.path.stem + ".clean")

    # Run the pipeline to remove the desired metadata
    pipeline: list[Callable] = [remove_motion_photo, remove_hdr_makernote, remove_extra_data]
    changed: list[bool] = []
    for func in pipeline:
        change = func(jpeg)
        changed.append(change)
    jpeg.image.sort_segments()

    # If a change has occured during the pipeline
    if not any(changed):
        print_verbose(f"{SYM_ARROW} No change applied")
        return None, size_input, size_input

    # Show information about the output images
    print_verbose(f"Output file: {output.absolute()}")
    size_output = len(jpeg)
    print_verbose(f"Output size: {size_output:,d} bytes")
    bytes_saved: int = size_input - size_output
    print_verbose(f"Difference: {bytes_saved:,d} bytes")

    # Write the output jpeg file
    if not dry:
        jpeg.save(output)

    return output.absolute(), size_input, size_output


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
    VERBOSE = args.verbose

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
    # Total bytes saved
    total_bytes: int = 0
    bytes_saved: int = 0
    # To show the progress
    progress_total = len(jpeg_files)
    # Total time
    timer_start = time.time()
    for progress, jpeg in track(enumerate(jpeg_files, 1), total=progress_total, transient=True):
        # show current folder
        if dir_current != jpeg.path.parent:
            dir_current = jpeg.path.parent
            print(f"\nFolder: {dir_current}")
        # Show progress
        if args.verbose:
            print(f"  {progress:>{len(str(progress_total))}}/{progress_total}")
        else:
            print(f"  {progress:>{len(str(progress_total))}}/{progress_total} ", end="")
        # Process the file
        output, size_input, size_output = process_jpeg(jpeg, args.dry)
        total_bytes += size_input
        bytes_saved += size_input - size_output
        # If not verbose, show the exported image
        if not args.verbose:
            if output is None:
                print(jpeg.path.name, "-> no change")
            else:
                print(jpeg.path.name, "->", output.name)

    print()
    timer_duration = time.time() - timer_start
    print(f"Total time: {time.strftime("%H:%M:%S", time.gmtime(timer_duration))}")
    print(f"Total size: {total_bytes:,d} bytes")
    print(f"Total saved: {bytes_saved:,d} bytes")
    print(f"Percent saved: {bytes_saved / total_bytes:.2%}")
