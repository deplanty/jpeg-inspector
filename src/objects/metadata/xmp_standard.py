from dataclasses import dataclass
from io import BytesIO
from xml.etree import ElementTree

from .metadata import Metadata

namespaces: dict[str, str] = {}


@dataclass
class XmpStandardItem:
    semantic: str = ""
    mime: str = ""
    length: int = -1
    padding: int = 0

    @classmethod
    def from_element(cls, element: ElementTree.Element) -> "XmpStandardItem":
        def get(key: str) -> str:
            return element.attrib.get(f"{{{namespaces['Item']}}}{key}", "")

        semantic = get("Semantic")
        mime = get("Mime")
        length = get("Length")
        if not length:
            length = cls.length
        else:
            length = int(length)
        padding = get("Padding")
        if not padding:
            padding = cls.padding
        else:
            padding = int(padding)

        return cls(semantic, mime, length, padding)


class XmpStandard(Metadata):
    signature = b"http://ns.adobe.com/xap/1.0/\x00"
    name = "XMP standard"

    def __init__(self, data):
        super().__init__()
        # Cache the result of the parse method
        self._items: list[XmpStandardItem] = []
        self._parsed: bool = False

    @property
    def items(self) -> list[XmpStandardItem]:
        # If the metadata has not been parsed, parse it
        if not self._parsed:
            self.parse()

        return self._items

    def parse(self) -> list[XmpStandardItem]:
        """Return the sequence of items contained in the JPEG file."""

        self._parsed = True

        # Load all the namespaces to read the xml and use the URI
        for events, (prefix, uri) in ElementTree.iterparse(
            BytesIO(self.payload), events=["start-ns"]
        ):
            namespaces[prefix] = uri

        # Parse the xml with xmp data
        tree = ElementTree.fromstring(self.payload.decode())
        # Find the node with the sequence of items contained in the files
        sequence = tree.find(".//Container:Directory/rdf:Seq", namespaces)
        if not sequence:
            return []
        # Get sequence of the items
        self._items: list[XmpStandardItem] = []
        for item in sequence.findall("rdf:li/Container:Item", namespaces):
            self._items.append(XmpStandardItem.from_element(item))

        return self._items
