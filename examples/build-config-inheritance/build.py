import essabuild as eb

project = eb.project("build-config")
project.compile_config.add_define("SCOPE", "\\\"GLOBAL\\\"")

lib = project.add_static_library("lib", sources=["lib.cpp"])
lib.compile_config.add_define("SCOPE", "\\\"LIB\\\"")

main = project.add_executable("main", sources=["main.cpp"])
main.link(lib)
main.compile_config.add_define("SCOPE", "\\\"MAIN\\\"")
