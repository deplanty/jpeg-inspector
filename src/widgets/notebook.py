from textual.app import App, ComposeResult
from textual.containers import Horizontal, HorizontalGroup, VerticalScroll
from textual.widgets import Button, TextArea


class Notebook(HorizontalGroup):
    def compose(self) -> ComposeResult:
        self.__tab_data: dict[Button, str] = dict()

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

    def add_tab(self, name: str, data: str) -> None:
        button = Button(name, classes="notebook-tab", compact=True)
        self.query_one("VerticalScroll").mount(button)
        self.__tab_data[button] = data

        if len(self.query("Button.notebook-tab")) == 1:
            # Show tab data
            button.add_class("selected")
            self.__show_data(button)

    def clear(self) -> None:
        for button in self.query("Button.notebook-tab"):
            button.remove()
        self.__tab_data.clear()

    def __show_data(self, button: Button) -> None:
        data = self.__tab_data[button]
        self.__text_area.load_text(data)
