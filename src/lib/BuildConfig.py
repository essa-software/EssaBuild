class BuildConfig:
    _parent = None
    std: str = None
    defines: dict[str, str] = {}
    options: list[str] = []

    def __init__(self, parent):
        self._parent = parent

    def get_std(self):
        return self.std or (self._parent.get_std() if self._parent else "gnu++20")

    def get_defines(self):
        return self.defines or (self._parent.get_defines() if self._parent else {})

    def get_options(self):
        return self.options or (self._parent.get_options() if self._parent else [])

    def defines_command(self):
        return " ".join([f"-D{v[0]}={v[1]}" for v in self.get_defines().items()])

    def options_command(self):
        return " ".join(self.get_options())

    def build_command_line(self):
        return f"-std={self.get_std()} {self.defines_command()} {self.options_command()}"
