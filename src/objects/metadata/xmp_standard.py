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
        self.items: list[XmpStandardItem] = []
        self.tree: ElementTree.Element
        self.parse()

    def parse(self) -> list[XmpStandardItem]:
        """Return the sequence of items contained in the JPEG file."""

        # Load all the namespaces to read the xml and use the URI
        for events, (prefix, uri) in ElementTree.iterparse(
            BytesIO(self.payload), events=["start-ns"]
        ):
            namespaces[prefix] = uri

        # Do nothing if the namespace Container is not present
        if "Container" not in namespaces:
            return []

        # Parse the xml with xmp data
        self.tree = ElementTree.fromstring(self.payload.decode())
        # Find the node with the sequence of items contained in the files
        sequence = self.tree.find(".//Container:Directory/rdf:Seq", namespaces)
        if not sequence:
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

    def remove_attribute(self, xpath: str, attribute: str):
        element = self.tree.find(xpath, namespaces)
        if not element:
            return

        attribute = self.with_namespace(attribute)
        element.attrib.pop(attribute)

    def remove_elements(self, xpath: str, where: dict[str, str]):
        elements = self.tree.findall(xpath, namespaces)
        if not elements:
            return

        trash: list[ElementTree.Element] = []
        for element in elements:
            for attrib, value in where.items():
                attrib = self.with_namespace(attrib)
                if element.attrib[attrib] != value:
                    break
            else:
                # If an element passes through all the filters
                trash.append(element)

        print(ElementTree.tostring(self.tree))
        for element in trash:
            print(element)
            elements.remove(element)
        print(ElementTree.tostring(self.tree))

    def with_namespace(self, item: str) -> str:
        # If a namespace is used for the attribute
        if ":" in item:
            space, key = item.split(":")
            namespace = namespaces[space]
            item = f"{{{namespace}}}{key}"
        return item
