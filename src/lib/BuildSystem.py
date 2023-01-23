from .Project import Project
from .Config import config

import os

root_project: Project = None


def project(name):
    global root_project
    if root_project:
        raise Exception("Project is already defined")
    root_project = Project(name)
    return root_project


def main(*, build: bool, run: bool, run_target: str):
    global root_project
    if not root_project:
        raise Exception("No project was defined")

    if build:
        os.makedirs(config.build_directory, exist_ok=True)
        root_project.build()

    if run:
        print(os.getcwd())
        root_project.run(run_target)
