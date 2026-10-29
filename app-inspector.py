#!.venv/Scripts/python

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, Vertical, VerticalScroll
from textual.events import Paste
from textual.message import Message
from textual.widgets import Button, Footer, Header, Label, TextArea

from src.jpeg import Jpeg
from src.widgets import Notebook


class JpegInspector(App):

    CSS_PATH = "./resources/style.tcss"

    def __init__(self) -> None:
        super().__init__()

        self.filename: str = ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Vertical(
            Label("Paste or drop a JPEG file"),
            Label("...", id="filename"),
            classes="browser",
        )
        yield Notebook(id="notebook")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse":
            filename = filedialog.askopenfilename()
            if not filename:
                return

            self.filename = filename
            self.query_one("#filename", Label).update(filename)
            self.load_jpeg()

        elif event.button.has_class("tab"):
            for button in self.query("Button.tab"):
                if button.has_class("selected"):
                    button.remove_class("selected")
                event.button.add_class("selected")

    def on_paste(self, event: Paste) -> None:
        path = Path(event.text.strip('"'))
        # If the pasted texts contains only paths
        if not path.exists():
            self.notify(
                f"Paste data is not a valid path\n{repr(event.text)}",
                title="Invalid input",
                severity="warning",
            )
            return
        elif path.suffix not in (".jpg", ".jpeg"):
            self.notify(
                f"File is not a JPEG: {path.name}",
                title="Invalid input",
                severity="warning",
            )
            return
        self.filename = str(path.absolute())
        self.query_one("#filename", Label).update(self.filename)
        self.load_jpeg()

    def load_jpeg(self) -> None:
        notebook: Notebook = self.query_one("#notebook")

        image = Jpeg(self.filename)
        if not image.is_valid_jpeg():
            self.notify("The file is not a valid JPEG", severity="error")
            return
        image.parse()
        # Populate the notebook with a tab for each segment
        notebook.clear()
        for segment in image.segments:
            notebook.add_tab(segment.name, str(segment.data))
            notebook.refresh()


if __name__ == "__main__":
    app = JpegInspector()
    app.run()
