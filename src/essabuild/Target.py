from enum import IntEnum
import os

from .BuildConfig import BuildConfig
from .Config import config
from .Source import Source, CppCompiledSource
from .TaskScheduler import Task
from .Utils import *

from typing import TYPE_CHECKING, Union, cast
if TYPE_CHECKING:
    from .Project import Project


class TargetType(IntEnum):
    EXECUTABLE = 1
    STATIC_LIBRARY = 2


class Target:
    _project: 'Project'
    _name: str
    _linked_targets: list['Target']
    target_type: TargetType
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
                                    for lib in self._linked_targets])

            match self.target_type:
                case TargetType.EXECUTABLE:
                    sprun(f"""g++
                        -o {self.executable_path()}
                        {linked_sources}
                        {linked_targets}
                        {self.link_config.build_command_line()}
                    """)
                case TargetType.STATIC_LIBRARY:
                    sprun(f"""ar -rcs
                        {self.executable_path()}
                        {linked_sources}
                        {linked_targets}
                    """)

        dependency_tasks = [dep._get_link_task() for dep in self._linked_targets if not dep._is_linking_up_to_date()]
        self.link_task = Task(f"link {self._name}", link, cast(list[Task], [*self._get_source_tasks(), *dependency_tasks]))
        return self.link_task

    def __init__(self, project: 'Project', target_type: TargetType, name: str, *, sources: list[Union[str, Source]]):
        self._project = project
        self._name = name
        self._linked_targets = []
        self._linking_up_to_date = None
        self.target_type = target_type
        self.compile_config = BuildConfig(project.compile_config)
        self.link_config = BuildConfig(project.link_config)
        self.sources = self._resolve_sources_argument(sources)
        self.source_tasks = None
        self.link_task = None

    def __repr__(self):
        return f"{self.target_type.name} {self._name}"

    def name(self) -> str:
        return self._name

    def linked_targets(self):
        return self._linked_targets

    def executable_path(self) -> str:
        match self.target_type:
            case TargetType.EXECUTABLE:
                return config.build_file(self._name)
            case TargetType.STATIC_LIBRARY:
                return f"{config.build_file(self._name)}.a"

    def get_link_option(self):
        match self.target_type:
            case TargetType.EXECUTABLE:
                raise Exception(
                    f"Cannot link to executable '{self.name()}'. Ensure that '{self.name()}' is a library")
            case TargetType.STATIC_LIBRARY:
                return f"{self.executable_path()}"

    def link(self, target: 'Target'):
        # Raise an exception early if linking is not allowed
        _ = target.get_link_option()
        self._linked_targets.append(target)

    def _is_linking_up_to_date(self):
        if self._linking_up_to_date:
            return self._linking_up_to_date

        # linking is up to date if:
        # 1. The executable actually exists
        # 2. All sources are up-to-date
        # 3. All dependencies (that are static libraries) have linking up-to-date.
        return \
            os.path.exists(self.executable_path()) and \
            all([src.is_up_to_date() for src in self.sources]) and \
            all([lib._is_linking_up_to_date() for lib in self._linked_targets]) 

    def get_tasks(self):
        # Note: It is important to store task objects, because they are compared
        #       to in dependency checks.
        return [*self._get_source_tasks()] + ([] if self._is_linking_up_to_date() else [self._get_link_task()])
