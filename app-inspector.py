#!.venv/Scripts/python

from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Vertical, HorizontalGroup
from textual.events import Paste
from textual.widgets import Footer, Header, Label, Select

from src.enums import DisplayFormat
from src.jpeg import Jpeg
from src.widgets import Notebook


class JpegInspector(App):
    CSS_PATH = "./resources/style.tcss"

    def __init__(self) -> None:
        super().__init__()

        self.filename: str = ""

    def compose(self) -> ComposeResult:
        display_format_options = [(df.name.title(), df) for df in DisplayFormat]
        yield Header(show_clock=True)
        yield Vertical(
            Label("Paste or drop a JPEG file"),
            Label("...", id="filename"),
            HorizontalGroup(
                Label("Text display format:"),
                Select(
                    options=display_format_options,
                    allow_blank=False,
                    value=DisplayFormat.RAW,
                    compact=True,
                    id="display-format",
                ),
            ),
            classes="browser",
        )
        yield Notebook(id="notebook")
        yield Footer()

    def on_paste(self, event: Paste) -> None:
        path = Path(event.text.strip('"'))
        # If the pasted texts contains only paths
        if not path.exists():
            self.notify(
                message=f"Paste data is not a valid path\n{event.text}",
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

    @on(Select.Changed)
    def on_select_changed(self, event: Select.Changed) -> None:
        notebook: Notebook = self.query_one("#notebook", expect_type=Notebook)
        notebook.set_display_format(event.value)

    def load_jpeg(self) -> None:
        notebook: Notebook = self.query_one("#notebook", expect_type=Notebook)

        image = Jpeg(self.filename)
        if not image.is_valid_jpeg():
            self.notify("The file is not a valid JPEG", severity="error")
            return
        image.parse()
        # Populate the notebook with a tab for each segment
        notebook.clear()
        for segment in image.segments:
            notebook.add_tab(segment.name, segment.data)
            notebook.refresh()
        # Add the existing trailing data
        if image.data_extra:
            notebook.add_tab("Tail", image.data_extra)


if __name__ == "__main__":
    app = JpegInspector()
    app.run()
