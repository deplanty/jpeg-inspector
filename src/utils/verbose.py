class Verbose:
    SYM_OK: str = "\033[92m✓\033[0m"
    SYM_NOT_OK: str = "\033[91m✗\033[0m"
    SYM_ARROW: str = "\033[96m→\033[0m"

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

    def print(self, *args, **kwargs) -> None:
        if self.verbose:
            print(*args, **kwargs, **kwargs)
