import essabuild as eb

project = eb.project("linking")

lib = project.add_static_library("lib", sources=["lib.cpp"])
main = project.add_executable("main", sources=["main.cpp"])
main.link(lib)
