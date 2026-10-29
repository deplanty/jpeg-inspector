#!.venv/Scripts/python

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

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Horizontal(
            Button("Browse...", id="browse", compact=True),
            Label("filename.jpg", id="filename"),
        )
        yield Notebook(id="notebook")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "browse":
            # root = tk.Tk()
            # filename = filedialog.askopenfilename()
            # if not filename:
            #     return
            filename = "C:/Users/4177349/Documents/Perso/Scripts/jpeg-inspector/data-test/example_art.MP.jpg"
            self.query_one("#filename", Label).update(filename)
            self.filename = filename
            self.load_jpeg()

        elif event.button.has_class("tab"):
            for button in self.query("Button.tab"):
                if button.has_class("selected"):
                    button.remove_class("selected")
                event.button.add_class("selected")

    @work(thread=True)
    def load_jpeg(self) -> None:
        notebook: Notebook = self.query_one("#notebook")

        self.image = Jpeg(self.filename)
        self.image.parse()
        # Populate the notebook with a tab for each segment
        self.call_from_thread(notebook.clear)
        for segment in self.image.segments:
            self.call_from_thread(notebook.add_tab, segment.name, str(segment.data))


if __name__ == "__main__":
    app = JpegInspector()
    app.run()
