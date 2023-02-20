import abc
import hashlib
import os

from .BuildConfig import BuildConfig
from .Config import config
from .Utils import *
from .TaskScheduler import Task

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from .Target import CppTarget


def hash_path(path):
    return config.tmp_file(f"hash_{hashlib.md5(path.encode()).hexdigest()}")


def calculate_file_hash(path):
    with open(path, "rb") as f:
        # TODO: This file should be preprocessed so that it handles headers properly.
        return hashlib.md5(f.read()).hexdigest()


def file_didnt_change(path):
    try:
        with open(hash_path(path)) as f:
            old_hash = f.read()
    except FileNotFoundError:
        old_hash = None

    new_hash = calculate_file_hash(path)
    return new_hash == old_hash


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

    def __init__(self, path, target: 'CppTarget'):
        self._path = path
        self.config = BuildConfig(target.compile_config)

    def object_file_path(self):
        return f"{config.build_file(self._path)}.o"

    def build(self):
        sprun(f"""g++
        -c {config.source_file(self._path)}
        -o {self.object_file_path()}
        {self.config.build_command_line()}
        """)

        with open(hash_path(self._path), "w") as f:
            f.write(calculate_file_hash(self._path))

    def get_build_description(self):
        return f"build source: {self._path}"

    def is_up_to_date(self):
        # Source file is up to date if:
        # 1. Object file exists
        if not os.path.exists(self.object_file_path()):
            return False

        # 2. File hash didn't change since last build
        return file_didnt_change(self._path)

    def path(self):
        return self._path


class GeneratedSource(Source):

    def __init__(self, generator: Callable[['GeneratedSource'], None],
                 sources: list[str]):
        self._sources = sources
        self._generator = generator

    def build(self):
        self._generator

    def get_build_description(self) -> str:
        return f"Source generated from {self._sources}"

    def is_up_to_date(self) -> bool:
        # 1. Underlying source file is up to date
        # 2. All files are
        return all([file_didnt_change(f) for f in self._sources])
