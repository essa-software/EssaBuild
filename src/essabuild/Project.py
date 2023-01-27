

import logging
import subprocess as sp

from .Target import Target, TargetType
from .BuildConfig import BuildConfig


class Project:

    _name: str
    _targets = dict[str, Target]()
    compile_config = BuildConfig(None)
    link_config = BuildConfig(None)

    def __init__(self, name):
        logging.info(f"New project: {name}")
        self._name = name

    def add_executable(self, name: str, *, sources: list[str]):
        logging.info(f"New executable: {name}, compiled from {sources[:3]}...")
        target = Target(self, TargetType.EXECUTABLE,
                        name, sources=sources)
        self._targets[name] = target
        return target

    def add_static_library(self, name: str, *, sources: list[str]):
        logging.info(
            f"New static library: {name}, compiled from {sources[:3]}...")
        target = Target(self, TargetType.STATIC_LIBRARY,
                        name, sources=sources)
        self._targets[name] = target
        return target

    def build(self):
        for target in self._targets.values():
            print(f"\033[32;1mBuilding target:\033[m {target.name()}")
            try:
                target.build()
            except Exception as e:
                print(e)
                print(f"\033[31;1mFailed:\033[m {target.name()}")

    def run(self, target_name):
        print(f"\033[34;1mRunning target:\033[m {target_name}")
        target = self._targets.get(target_name)
        if not target:
            raise Exception(f"No target with name {target_name} found")

        sp.run(target.executable_path())
