import argparse
import re
from pathlib import Path

from rich.progress import track

from src.utils.verbose import Verbose


def process_path(path: Path, dry: bool) -> None:
    """
    If the path has ".clean" in its name:
      - Find if its twin file is present.
      - Remove .clean and replace the current file.

    Args:
        path (pathlib.Path): The filename to process.
        dry (bool): Simulate the process without doing anything.
    """

    if ".clean" in path.suffixes:
        stem: str = re.sub(r"\.clean", "", path.stem)
        twin_path: Path = path.with_stem(stem)
        if twin_path.exists():
            verbose.print(Verbose.SYM_OK, twin_path.name, "replaced")
        else:
            verbose.print(Verbose.SYM_NOT_OK, twin_path.name, "created")

        if not dry:
            path.replace(twin_path)
    else:
        verbose.print(Verbose.SYM_ARROW, path.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean the folder after the metadata are cleaned.")
    parser.add_argument("paths", nargs="+", help="The directories to parse.")
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
    verbose = Verbose(args.verbose)

    # Find all the files to process
    paths: list[Path] = []
    for filename in args.paths:
        path = Path(filename)
        if path.is_dir():
            paths.extend(path.rglob("*.jp*"))
        elif path.is_file() and path.suffix.endswith((".jpg", ".jpeg")):
            paths.append(path)
        else:
            raise ValueError(f"Path {path} is unknown.")

    # To show the current folder
    dir_current = ""
    for path in track(paths, transient=True):
        if dir_current != path.parent:
            dir_current = path.parent
            print(f"\nFolder: {dir_current}")

        process_path(path, args.dry)
