from enum import IntEnum

from .BuildConfig import BuildConfig
from .Config import config
from .Utils import *

from typing import TYPE_CHECKING
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
    sources: list[str]
    compile_config: BuildConfig
    link_config: BuildConfig

    def __init__(self, project: 'Project', target_type: TargetType, name: str, *, sources: list[str]):
        self._project = project
        self._name = name
        self._linked_targets = []
        self.target_type = target_type
        self.sources = sources
        self.compile_config = BuildConfig(project.compile_config)
        self.link_config = BuildConfig(project.link_config)

    def __repr__(self):
        return f"{self.target_type.name} {self._name}"
    def name(self) -> str:
        return self._name

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

        # TODO: Topo sort, so that the target is built only once.
        self._linked_targets.append(target)

    def build(self):
        for src in self.sources:
            print(f"... building: {src}")
            sprun(f"""g++
            -c {config.source_file(src)}
            -o {config.build_file(src)}.o
            {self.compile_config.build_command_line()}
        """)

        linked_sources = ' '.join(
            [config.build_file(f"{src}.o") for src in self.sources])
        linked_targets = ' '.join([lib.get_link_option()
                                  for lib in self._linked_targets])

        match self.target_type:
            case TargetType.EXECUTABLE:
                print(f"... linking: {self._name}")
                sprun(f"""g++
                    -o {self.executable_path()}
                    {linked_sources}
                    {linked_targets}
                    {self.link_config.build_command_line()}
                """)
            case TargetType.STATIC_LIBRARY:
                print(f"... packing: {self._name}")
                sprun(f"""ar -rcs
                    {self.executable_path()}
                    {linked_sources}
                    {linked_targets}
                """)
