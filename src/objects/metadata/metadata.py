class Metadata(bytes):
    signature: bytes = b""
    name: str = ""

    @property
    def payload(self) -> bytes:
        return self[len(self.signature) :]

    @classmethod
    def has_signature(cls, data: bytes) -> bool:
        return data.startswith(cls.signature)

    def to_raw_str(self) -> str:
        if self.name:
            return f"{self.name}\n{self.payload!s}"
        else:
            return str(self)

    def to_str(self) -> str:
        try:
            return f"{self.name}\n{self.payload.decode('utf-8')}"
        except UnicodeDecodeError:
            return self.to_raw_str()

    def to_hex(self, line_width: int = 16) -> str:
        lines: list[str] = []
        line_start: int = 0
        if self.name:
            lines.append(self.name)
        line_hex: list[str] = []
        line_str: str = ""
        for index in range(len(self.payload)):
            if index != 0 and index % line_width == 0:
                line = f"{line_start:08x} {' '.join(line_hex)} | {line_str}"
                lines.append(line)
                line_start = index
                line_hex.clear()
                line_str = ""
            # The hex representation of the byte
            line_hex.append(f"{self.payload[index]:02x}")
            # The string representation of the byte
            char = chr(self.payload[index])
            if not char.isprintable():
                char = "."
            line_str += char

        return "\n".join(lines)
