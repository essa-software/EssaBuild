class BuildConfig:

    def __init__(self, parent):
        self._parent = parent
        self._options = list[str]()
        if not parent:
            self.set_std("gnu++20")

    def add_option(self, option: str):
        self._options.append(option)

    def add_define(self, name: str, value: str):
        self.add_option(f"-D{name}={value}")

    def set_std(self, std: str):
        self.add_option(f"-std={std}")

    def build_command_line(self):
        return (self._parent.build_command_line() + " " if self._parent else
                "") + " ".join([v for v in self._options])
