from typing import Callable

import logging


class Task:

    def __init__(self, name: str, worker: Callable[[], None],
                 dependencies: list['Task']):
        self.name = name
        self.worker = worker
        self.dependencies = dependencies

    def __str__(self):
        return f"Task({self.name})"

    def __repr__(self):
        return f"{self.__str__()} -> {[str(task) for task in self.dependencies]}"


class TaskScheduler:

    class TaskState:
        task: Task

        def __init__(self, task: Task):
            self.task = task

    def __init__(self):
        self.remaining_tasks = list[Task]()
        self.currently_performed_tasks = set[Task]()
        self.done_tasks = set[Task]()

    def add_task(self, task: Task):
        self.remaining_tasks.append(task)

    def get_next_task(self):
        for task in self.remaining_tasks:
            all_dependencies_are_worked_on = True
            for dep in task.dependencies:
                if not dep in self.currently_performed_tasks and not dep in self.done_tasks:
                    if not dep in self.remaining_tasks:
                        logging.warning("Dependency %s of %s is unfinished but is also not scheduled, skipping! This is a bug.", dep, task)
                        continue
                    logging.debug(
                        "Skipping %s because of unfinished dependency %s.",
                        task, dep)
                    all_dependencies_are_worked_on = False
                    break
            if all_dependencies_are_worked_on:
                self.currently_performed_tasks.add(task)
                self.remaining_tasks.remove(task)
                return task

        if len(self.remaining_tasks) > 0:
            logging.warning(
                f"No suitable task found but {len(self.remaining_tasks)} left to do!\
                    This is probably because of circular dependencies.")
            for task in self.remaining_tasks:
                print(task)

        return None

    def mark_as_done(self, task: Task):
        self.done_tasks.add(task)
        assert (task in self.currently_performed_tasks)
        self.currently_performed_tasks.remove(task)

    def dump(self):
        print("Remaining tasks:")
        for task in self.remaining_tasks:
            print(repr(task))
        print("Currently performed tasks:")
        for task in self.currently_performed_tasks:
            print(repr(task))
        print("Done tasks:")
        for task in self.done_tasks:
            print(repr(task))
