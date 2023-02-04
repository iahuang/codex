class StringBuilder:
    _data: str

    def __init__(self) -> None:
        self._data = ""

    def write(self, data: str) -> None:
        self._data += data

    def writeln(self, data="") -> None:
        self.write(data + "\n")

    def get_data(self, trim_trailing_whitespace=True) -> str:
        if trim_trailing_whitespace:
            return self._data.rstrip()
        else:
            return self._data
