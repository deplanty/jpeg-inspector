#!.venv/Scripts/python

from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, Vertical
from textual.events import Paste
from textual.widgets import Footer, Header, Label, Select

from src.objects.jpeg import Jpeg, JpegImage
from src.utils.enums import DisplayFormat
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

        jpeg = Jpeg(self.filename)
        if not jpeg.is_valid_jpeg():
            self.notify("The file is not a valid JPEG", severity="error")
            return
        jpeg.parse()
        # Clean th notebook
        notebook.clear()
        # Populate the notebook with a tab with the main image
        notebook.add_element("root", "main-image", "Main image")
        for i, segment in enumerate(jpeg.image.segments):
            notebook.add_element("main-image", f"main-image-{i:02d}", segment.name, segment.data)
            notebook.refresh()
        # Add the tabs for the xmp data
        notebook.add_element("root", "xmp", "XMP data")
        for i, xmp_data in enumerate(jpeg.xmp_data.values()):
            uid = f"xmp-{i:02d}"
            if isinstance(xmp_data, JpegImage):
                notebook.add_element("xmp", uid, "Image")
                for j, segment in enumerate(xmp_data.segments):
                    notebook.add_element(uid, f"{uid}-{j:02d}", segment.name, segment.data)
            else:
                notebook.add_element("xmp", uid, "Other", xmp_data)
        # Add the extra data
        if jpeg.extra_data:
            notebook.add_element("root", "extra-data", "Extra", jpeg.extra_data)


if __name__ == "__main__":
    app = JpegInspector()
    app.run()
