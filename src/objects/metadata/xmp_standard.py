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

    def __init__(self, data: bytes):
        super().__init__(data)
        # Cache the result of the parse method
        self.items: list[XmpStandardItem] = []
        self.tree: ElementTree.Element
        self.parse()

    def _update_payload(self) -> None:
        self.payload = ElementTree.tostring(self.tree)

    def parse(self) -> list[XmpStandardItem]:
        """Return the sequence of items contained in the JPEG file."""

        # Load all the namespaces to read the xml and use the URI
        for events, (prefix, uri) in ElementTree.iterparse(
            BytesIO(self.payload), events=["start-ns"]
        ):
            namespaces[prefix] = uri
            # Register the namespaces to write the correct name when calling ElementTree.tostring
            ElementTree.register_namespace(prefix, uri)

        # Do nothing if the namespace Container is not present
        if "Container" not in namespaces:
            return []

        # Parse the xml with xmp data
        self.tree = ElementTree.fromstring(self.payload.decode())
        # Find the node with the sequence of items contained in the files
        sequence = self.tree.find(".//Container:Directory/rdf:Seq", namespaces)
        if sequence is None:
            return []
        # Get sequence of the items
        self.items: list[XmpStandardItem] = []
        for item in sequence.findall("rdf:li/Container:Item", namespaces):
            self.items.append(XmpStandardItem.from_element(item))

        return self.items

    def set_attribute(self, xpath: str, attribute: str, value: str):
        element = self.tree.find(xpath, namespaces)
        if not element:
            return

        attribute = self.with_namespace(attribute)
        element.attrib[attribute] = str(value)
        self._update_payload()

    def remove_attribute(self, xpath: str, attribute: str):
        element = self.tree.find(xpath, namespaces)
        if not element:
            return

        attribute = self.with_namespace(attribute)
        element.attrib.pop(attribute)
        self._update_payload()

    def remove_elements(self, xpath: str):
        elements = self.tree.findall(xpath, namespaces)
        if not elements:
            return

        parent = self.tree.find(xpath + "/..", namespaces)
        for element in elements:
            parent.remove(element)

        self._update_payload()

    def with_namespace(self, item: str) -> str:
        # If a namespace is used for the attribute
        if ":" in item:
            space, key = item.split(":")
            namespace = namespaces[space]
            item = f"{{{namespace}}}{key}"
        return item
