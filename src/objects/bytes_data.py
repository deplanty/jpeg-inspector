class BytesData(bytes):
    def to_raw_str(self) -> str:
        return str(self)

    def to_str(self) -> str:
        try:
            return self.decode("utf-8")
        except UnicodeDecodeError:
            return str(self)

    def to_hex(self, line_width: int = 16) -> str:
        lines: list[str] = []
        line_start: int = 0
        line_hex: list[str] = []
        line_str: str = ""
        for index in range(len(self)):
            if index != 0 and index % line_width == 0:
                line = f"{line_start:08x} {' '.join(line_hex)} | {line_str}"
                lines.append(line)
                line_start = index
                line_hex.clear()
                line_str = ""
            # The hex representation of the byte
            line_hex.append(f"{self[index]:02x}")
            # The string represtation of the byte
            char = chr(self[index])
            if not char.isprintable():
                char = "."
            line_str += char

        return "\n".join(lines)
