from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import Button, TextArea

from src.enums import DisplayFormat


def _bytes_to_string(b: bytes) -> str:
    """
    Args:
        b (bytes): bytes object to convert to string.

    Returns (str): the decoded string or the raw value of the bytes.
    """

    try:
        return b.decode("utf-8")
    except UnicodeDecodeError as e:
        print(e)
        return str(b)


def _bytes_to_hex(b: bytes, line_width: int = 16) -> str:
    lines: list[str] = []
    line: list[str] = []
    for index in range(len(b)):
        if index % line_width == 0:
            lines.append(" ".join(line))
            line = [f"{index:08x}"]
        line.append(f"{b[index]:02x}")

    return "\n".join(lines)


class Notebook(HorizontalGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The data associated with each tab
        self.__tab_data: dict[Button, bytes] = {}
        # The text area showing the data
        self.__text_area: TextArea
        # How the data is shown (raw, plain or hex)
        self.__display_format: DisplayFormat = DisplayFormat.RAW
        # If the notebook is ready to show data
        self.__ready: bool = False

    def set_display_format(self, display_format: DisplayFormat) -> None:
        self.__display_format = display_format
        self.__show_data()

    def compose(self) -> ComposeResult:
        yield VerticalScroll(classes="notebook-tab")
        self.__text_area = TextArea(read_only=True, show_cursor=False, id="text-data")
        yield self.__text_area

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # if event.button.has_class("notebook-tab"):
        # Manage tabs style
        for button in self.query("Button.notebook-tab"):
            if button.has_class("selected"):
                button.remove_class("selected")
        event.button.add_class("selected")

        # Show tab data
        self.__show_data(event.button)

    def add_tab(self, name: str, data: bytes) -> None:
        button = Button(name, classes="notebook-tab", compact=True)
        self.query_one("VerticalScroll").mount(button)
        self.__tab_data[button] = data
        self.__ready = True

        if len(self.query("Button.notebook-tab")) == 1:
            # Show tab data
            button.add_class("selected")
            self.__show_data(button)

    def clear(self) -> None:
        for button in self.query("Button.notebook-tab"):
            button.remove()
        self.__tab_data.clear()

    def __show_data(self, button: Button | None = None) -> None:
        if not self.__ready:
            return

        if button is None:
            button = self.query_one("Button.notebook-tab.selected", Button)

        data: bytes = self.__tab_data[button]
        text: str
        match self.__display_format:
            case DisplayFormat.RAW:
                text = str(data)
            case DisplayFormat.PLAIN:
                text = _bytes_to_string(data)
            case DisplayFormat.HEX:
                text = _bytes_to_hex(data)
            case _:
                print("Other")
                text = str(data)

        self.__text_area.load_text(text)
        self.__text_area.focus()
