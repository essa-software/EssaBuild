from .BuildConfig import BuildConfig
from .Config import config
from .Utils import sprun

class Target:
    _project: 'Project'
    _name: str
    sources = list[str]()
    compile_config: BuildConfig
    link_config: BuildConfig

    def __init__(self, project: 'Project', name: str, *, sources: list[str]):
        self._project = project
        self._name = name
        self.sources = sources
        self.compile_config = BuildConfig(project.compile_config)
        self.link_config = BuildConfig(project.link_config)

    def name(self) -> str:
        return self._name

    def executable_path(self) -> str:
        return config.build_file(self._name)

    def build(self) -> list[str]:
        for src in self.sources:
            print(f"... building: {src}")
            sprun(f"""g++
            -c {config.source_file(src)}
            -o {config.build_file(src)}.o
            {self.compile_config.build_command_line()}
        """)

        print(f"... linking: {self._name}")
        linked_sources = ' '.join(
            [config.build_file(f"{src}.o") for src in self.sources])
        sprun(f"""g++
            -o {self.executable_path()}
            {linked_sources}
            {self.link_config.build_command_line()}
        """)
