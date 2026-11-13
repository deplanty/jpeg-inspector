from dataclasses import dataclass
from xml.etree import ElementTree

from .xml_metadata import XmlMetadata


@dataclass
class XmpStandardItem:
    semantic: str = ""
    mime: str = ""
    length: int = -1
    padding: int = 0

    @classmethod
    def from_element(cls, element: ElementTree.Element, namespaces) -> "XmpStandardItem":
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


class XmpStandard(XmlMetadata):
    signature = b"http://ns.adobe.com/xap/1.0/\x00"
    name = "Standard XMP"

    def __init__(self, payload: bytes):
        super().__init__(payload)

        self.items: list[XmpStandardItem] = []
        self.parse()

    def parse(self) -> list[XmpStandardItem]:
        """Return the sequence of items contained in the JPEG file."""

        # Do nothing if the namespace Container is not present
        if "Container" not in self.namespaces:
            return []

        # Parse the xml with xmp data
        self.tree = ElementTree.fromstring(self.payload.decode())
        # Find the node with the sequence of items contained in the files
        sequence = self.tree.find(".//Container:Directory/rdf:Seq", self.namespaces)
        if sequence is None:
            return []
        # Get sequence of the items
        self.items: list[XmpStandardItem] = []
        for item in sequence.findall("rdf:li/Container:Item", self.namespaces):
            self.items.append(XmpStandardItem.from_element(item, self.namespaces))

        return self.items
