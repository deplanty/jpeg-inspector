class InvalidJpegError(Exception):
    def __init__(self, path: str):
        super().__init__()
        self.path: str = path

    def __str__(self) -> str:
        return f"{self.path} is not a valid JPEG."


class SegmentMarkerError(Exception):
    pass
