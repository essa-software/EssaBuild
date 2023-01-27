import essabuild as eb

project = eb.project("linking-multiple-times")

lib = project.add_static_library("lib", sources=["lib.cpp"])

foo = project.add_executable("foo", sources=["foo.cpp"])
foo.link(lib)

bar = project.add_executable("bar", sources=["bar.cpp"])
bar.link(lib)
