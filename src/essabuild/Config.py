import os


class Config:
    source_directory: str
    build_directory: str

    def source_file(self, path: str):
        return os.path.join(self.source_directory, path)

    def build_file(self, path: str):
        return os.path.join(self.build_directory, path)


config = Config()
