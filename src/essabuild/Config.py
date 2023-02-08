import os


class Config:
    # Directory with the main build.py script.
    source_directory: str

    # Directory in which resulting binaries (**target** outputs) are stored.
    build_directory: str

    # Directory which can be used by build drivers for storing
    # temporary files (e.g object, caches)
    tmp_directory: str

    def source_file(self, path: str):
        return os.path.join(self.source_directory, path)

    def build_file(self, path: str):
        return os.path.join(self.build_directory, path)

    def tmp_file(self, path: str):
        return os.path.join(self.tmp_directory, path)


config = Config()
