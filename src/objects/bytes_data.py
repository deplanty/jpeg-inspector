class BytesData(bytes):
    def to_str(self) -> str:
        try:
            return self.decode("utf-8")
        except UnicodeDecodeError:
            return str(self)

    def to_raw_str(self) -> str:
        return str(self)

    def to_hex(self, line_width: int = 16) -> str:
        lines: list[str] = []
        line_hex: list[str] = []
        for index in range(len(self)):
            if index % line_width == 0:
                lines.append(" ".join(line_hex))
                line_hex = [f"{index:08x}"]
            line_hex.append(f"{self[index]:02x}")

        return "\n".join(lines)
