import logging
import subprocess as sp
import traceback
from typing import Callable, Union

from .Source import Source
from .Target import Target, CppTarget, CppTargetType, GeneratedTarget
from .TaskScheduler import TaskScheduler
from .BuildConfig import BuildConfig


class Project:
    _name: str
    _targets = dict[str, Target]()
    compile_config = BuildConfig(None)
    link_config = BuildConfig(None)

    def __init__(self, name):
        logging.info(f"New project: {name}")
        self._name = name

    # Sources given as strings are assumed to be CppCompiledSources.
    def add_executable(self, name: str, *, sources: list[Union[str, Source]]):
        logging.info(f"New executable: {name}, compiled from {sources[:3]}...")
        target = CppTarget(self,
                           CppTargetType.EXECUTABLE,
                           name,
                           sources=sources)
        self._targets[name] = target
        return target

    # Sources given as strings are assumed to be CppCompiledSources.
    def add_static_library(self, name: str, *, sources: list[Union[str,
                                                                   Source]]):
        logging.info(
            f"New static library: {name}, compiled from {sources[:3]}...")
        target = CppTarget(self,
                           CppTargetType.STATIC_LIBRARY,
                           name,
                           sources=sources)
        self._targets[name] = target
        return target

    def add_generated(self, name: str, *, generator: Callable[[list[str]],
                                                              None],
                      sources: list[str]):
        logging.info(
            f"New generated target: {name}, built from {sources[:3]}...")
        target = GeneratedTarget(self, name, sources, generator)
        self._targets[name] = target
        return target

    def build(self):
        scheduler = TaskScheduler()
        for target in self._targets.values():
            for task in target.get_tasks():
                scheduler.add_task(task)

        if logging.root.isEnabledFor(logging.DEBUG):
            scheduler.dump()

        while True:
            task = scheduler.get_next_task()
            if not task:
                break
            try:
                print(f"\033[32;1mPerforming task:\033[m {task.name}")
                task.worker()
            except Exception:
                traceback.print_exc()
            finally:
                scheduler.mark_as_done(task)

    def run(self, target_name):
        print(f"\033[34;1mRunning target:\033[m {target_name}")
        target = self._targets.get(target_name)
        if not target:
            raise Exception(f"No target with name {target_name} found")

        target.run()
