#!.venv/Scripts/textual run --dev

import tkinter as tk
from tkinter import filedialog

from textual import work
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Label, TextArea

from src.jpeg import Jpeg
from src.widgets import Notebook


class JpegInspector(App):

    CSS_PATH = "./resources/style.tcss"

    def __init__(self) -> None:
        super().__init__()

        self.filename: str = ""
        self.image: Jpeg
        # Required to ask the user to select a file
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Horizontal(
            Button("Browse...", id="browse", variant="primary"),
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

            self.query_one("#filename", Label).update(filename)
            self.filename = filename
            self.load_jpeg()

        elif event.button.has_class("tab"):
            for button in self.query("Button.tab"):
                if button.has_class("selected"):
                    button.remove_class("selected")
                event.button.add_class("selected")

    def load_jpeg(self) -> None:
        notebook: Notebook = self.query_one("#notebook")

        self.image = Jpeg(self.filename)
        self.image.parse()
        # Populate the notebook with a tab for each segment
        notebook.clear()
        for segment in self.image.segments:
            notebook.add_tab(segment.name, str(segment.data))
            notebook.refresh()


if __name__ == "__main__":
    app = JpegInspector()
    app.run()
