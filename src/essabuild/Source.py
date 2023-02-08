import abc
import hashlib

from .BuildConfig import BuildConfig
from .Config import config
from .Utils import *
from .TaskScheduler import Task

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Target import Target


class Source(abc.ABC):

    @abc.abstractmethod
    def build(self):
        return

    @abc.abstractmethod
    def get_build_description(self) -> str:
        return

    @abc.abstractmethod
    def is_up_to_date(self) -> bool:
        return

    def get_task(self):

        def worker():
            nonlocal self
            print(f"... {self.get_build_description()}")
            if self.is_up_to_date():
                return
            self.build()

        return Task(self.get_build_description(), worker, [])


class CppCompiledSource(Source):
    _path: str
    config: 'BuildConfig'

    def __init__(self, path, target: 'Target'):
        self._path = path
        self.config = BuildConfig(target.compile_config)

    def build(self):
        sprun(f"""g++
        -c {config.source_file(self._path)}
        -o {config.build_file(self._path)}.o
        {self.config.build_command_line()}
        """)

        with open(self.hash_path(), "w") as f:
            f.write(self.calculate_actual_file_hash())

    def get_build_description(self):
        return f"build source: {self._path}"

    def hash_path(self):
        return config.tmp_file(
            f"hash_{hashlib.md5(self._path.encode()).hexdigest()}")

    def calculate_actual_file_hash(self):
        with open(self._path, "rb") as f:
            # TODO: This file should be preprocessed so that it handles headers properly.
            return hashlib.md5(f.read()).hexdigest()

    def is_up_to_date(self):
        try:
            with open(self.hash_path()) as f:
                old_hash = f.read()
        except FileNotFoundError:
            old_hash = None

        new_hash = self.calculate_actual_file_hash()
        return new_hash == old_hash

    def path(self):
        return self._path
