from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import TextArea, Tree

from src.utils.enums import DisplayFormat

if TYPE_CHECKING:
    from textual.widgets.tree import TreeNode

    from objects.metadata import Metadata


class Notebook(HorizontalGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # How the data is shown (raw, plain or hex)
        self.__display_format: DisplayFormat = DisplayFormat.RAW
        # The nodes of the tree identified by a unique identifier
        self.__tree_nodes: dict[str, TreeNode] = {}
        # The data associated with each leaf
        self.__tree_data: dict[TreeNode, Metadata] = {}
        # The current node selected
        self.__tree_node_current: TreeNode | None = None
        # The text area showing the data
        self.__text_area: TextArea

    def compose(self) -> ComposeResult:
        self.__tree = Tree("Jpeg", classes="notebook-tab")
        self.__tree.root.expand()
        self.__tree_nodes["root"] = self.__tree.root
        yield self.__tree

        self.__text_area = TextArea(read_only=True, show_cursor=False, id="text-data")
        yield self.__text_area

    # Events

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node not in self.__tree_data:
            return
        self.__tree_node_current = event.node
        self.__show_data()

    # Public methods

    def set_display_format(self, display_format: DisplayFormat) -> None:
        self.__display_format = display_format
        self.__show_data()

    def add_element(self, parent_uid: str, uid: str, label: str, data: bytes | None = None) -> None:
        """
        To add an element to the main item, use parent_uid=root.
        If data is None, the element is a node. Else the element is a leaf.

        Args:
            parent_uid (str): the unique identifier of the parent node.
            uid (str): the unique identifier of the node.
            label (str): the displayed text.
            data (bytes): the associated data of the leaf for this component.
        """

        node = self.__tree_nodes[parent_uid]
        if data is None:
            self.__tree_nodes[uid] = node.add(label, expand=True)
        else:
            leaf = node.add_leaf(label)
            self.__tree_nodes[uid] = leaf
            self.__tree_data[leaf] = data

    def clear(self) -> None:
        self.__tree.clear()
        self.__tree_nodes.clear()
        self.__tree_data.clear()
        self.__tree_node_current = None
        self.__text_area.clear()

        self.__tree_nodes["root"] = self.__tree.root

    # Private methods

    def __show_data(self) -> None:
        if self.__tree_node_current is None:
            return

        data: Metadata = self.__tree_data[self.__tree_node_current]
        text: str
        match self.__display_format:
            case DisplayFormat.RAW:
                text = data.to_raw_str()
            case DisplayFormat.PLAIN:
                text = data.to_str()
            case DisplayFormat.HEX:
                text = data.to_hex()
            case _:
                text = data.to_raw_str()

        self.__text_area.load_text(text)
