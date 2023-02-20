from enum import IntEnum
import os

from .BuildConfig import BuildConfig
from .Config import config
from .Source import Source, CppCompiledSource
from .TaskScheduler import Task
from .Utils import *

import abc
from typing import TYPE_CHECKING, Callable, Union, cast
if TYPE_CHECKING:
    from .Project import Project


class Target(abc.ABC):
    def __init__(self, project: 'Project', name: str):
        self._project = project
        self._name = name
        self._linked_targets = []

    def name(self) -> str:
        return self._name

    def linked_targets(self):
        return self._linked_targets

    def link(self, target: 'Target'):
        # TODO: Raise an exception early if linking is not allowed
        self._linked_targets.append(target)

    @abc.abstractmethod
    def get_tasks(self) -> list[Task]:
        return

    @abc.abstractmethod
    def is_linking_up_to_date(self) -> bool:
        return

    def run(self):
        raise Exception(f"Target '{self.name}' is not runnable")

class CppTargetType(IntEnum):
    EXECUTABLE = 1
    STATIC_LIBRARY = 2

class CppTarget(Target):
    target_type: CppTargetType
    sources: list[Source]
    compile_config: BuildConfig
    link_config: BuildConfig

    def _resolve_sources_argument(self, sources: list[Union[str, Source]]):
        return [
            CppCompiledSource(src, self) if isinstance(src, str) else src for src in sources
        ]

    def _get_source_tasks(self):
        if self.source_tasks:
            return self.source_tasks

        self.source_tasks = [src.get_task() for src in self.sources if not src.is_up_to_date()]
        return self.source_tasks

    def _get_link_task(self):
        if self.link_task:
            return self.link_task

        def link():
            nonlocal self
            # FIXME: This is not abstract enough.
            linked_sources = ' '.join(
                [src.object_file_path() for src in self.sources if isinstance(src, CppCompiledSource)])
            linked_targets = ' '.join([lib.get_link_option()
                                    for lib in self._linked_targets if isinstance(lib, CppTarget)])

            match self.target_type:
                case CppTargetType.EXECUTABLE:
                    sprun(f"""g++
                        -o {self.executable_path()}
                        {linked_sources}
                        {linked_targets}
                        {self.link_config.build_command_line()}
                    """)
                case CppTargetType.STATIC_LIBRARY:
                    sprun(f"""ar -rcs
                        {self.executable_path()}
                        {linked_sources}
                        {linked_targets}
                    """)
                    

        dependency_tasks = [dep._get_link_task() for dep in self._linked_targets if isinstance(dep, CppTarget) and not dep.is_linking_up_to_date()]
        self.link_task = Task(f"link {self._name}", link, cast(list[Task], [*self._get_source_tasks(), *dependency_tasks]))
        return self.link_task

    def __init__(self, project: 'Project', target_type: CppTargetType, name: str, *, sources: list[Union[str, Source]]):
        super().__init__(project, name)
        self._linking_up_to_date = None
        self.target_type = target_type
        self.compile_config = BuildConfig(project.compile_config)
        self.link_config = BuildConfig(project.link_config)
        self.sources = self._resolve_sources_argument(sources)
        self.source_tasks = None
        self.link_task = None

    def __repr__(self):
        return f"{self.target_type.name} {self._name}"

    def executable_path(self) -> str:
        match self.target_type:
            case CppTargetType.EXECUTABLE:
                return config.build_file(self._name)
            case CppTargetType.STATIC_LIBRARY:
                return f"{config.build_file(self._name)}.a"

    def get_link_option(self):
        match self.target_type:
            case CppTargetType.EXECUTABLE:
                raise Exception(
                    f"Cannot link to executable '{self.name()}'. Ensure that '{self.name()}' is a library")
            case CppTargetType.STATIC_LIBRARY:
                return f"{self.executable_path()}"

    def is_linking_up_to_date(self):
        if self._linking_up_to_date:
            return self._linking_up_to_date

        # linking is up to date if:
        # 1. The executable actually exists
        # 2. All sources are up-to-date
        # 3. All dependencies (that are static libraries) have linking up-to-date.
        return \
            os.path.exists(self.executable_path()) and \
            all([src.is_up_to_date() for src in self.sources]) and \
            all([lib.is_linking_up_to_date() for lib in self._linked_targets]) 

    def get_tasks(self):
        # Note: It is important to store task objects, because they are compared
        #       to in dependency checks.
        return [*self._get_source_tasks()] + ([] if self.is_linking_up_to_date() else [self._get_link_task()])

    def run(self):
        if self.target_type != CppTargetType.EXECUTABLE:
            raise Exception(f"Cannot run non-executable target {self.name()}")
        sp.run(self.executable_path())

class GeneratedTarget(Target):
    def __init__(self, project: 'Project', name: str, sources: list[str], generator: Callable[[list[str]], None]):
        super().__init__(project, name)
        self._sources = sources
        self._generator = generator

        def generate():
            nonlocal self, generator
            # TODO: Up to date check
            generator(self._sources)

        self._generate_task = Task(f"generate: {sources}", generate, [])

    def get_tasks(self):
        return [self._generate_task]

    def is_linking_up_to_date(self):
        # TODO
        return True
