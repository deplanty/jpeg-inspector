import io
from typing import Any
from xml.etree import ElementTree

from .metadata import Metadata


class XmlMetadata(Metadata):
    def __init__(self, payload: bytes):
        super().__init__(payload)

        self.namespaces: dict[str, str] = {}
        self.register_namespaces()
        self.tree = ElementTree.fromstring(self.payload.decode())

    def _update_payload(self) -> None:
        self.payload = ElementTree.tostring(self.tree)

    def register_namespaces(self) -> None:
        """Return the sequence of items contained in the JPEG file."""

        # Load all the namespaces to read the xml and use the URI
        for events, (prefix, uri) in ElementTree.iterparse(
            io.BytesIO(self.payload), events=["start-ns"]
        ):
            self.namespaces[prefix] = uri
            # Register the namespaces to write the correct name when calling ElementTree.tostring
            ElementTree.register_namespace(prefix, uri)

    def get_attribute(self, xpath: str, attribute: str) -> None | Any:
        element = self.tree.find(xpath, self.namespaces)
        if element is None:
            return

        attribute = self.with_namespace(attribute)
        return element.attrib[attribute]

    def set_attribute(self, xpath: str, attribute: str, value: str):
        element = self.tree.find(xpath, self.namespaces)
        if element is None:
            return

        attribute = self.with_namespace(attribute)
        element.attrib[attribute] = str(value)
        self._update_payload()

    def remove_attribute(self, xpath: str, attribute: str):
        element = self.tree.find(xpath, self.namespaces)
        if element is None:
            return

        attribute = self.with_namespace(attribute)
        element.attrib.pop(attribute)
        self._update_payload()

    def remove_elements(self, xpath: str):
        elements = self.tree.findall(xpath, self.namespaces)
        if not elements:
            return

        parent = self.tree.find(xpath + "/..", self.namespaces)
        for element in elements:
            parent.remove(element)

        self._update_payload()

    def with_namespace(self, item: str) -> str:
        # If a namespace is used for the attribute
        if ":" in item:
            space, key = item.split(":")
            namespace = self.namespaces[space]
            item = f"{{{namespace}}}{key}"
        return item
