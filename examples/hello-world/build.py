import essabuild as eb

# Initialize a new project.
project = eb.project("hello-world")

# Set properties that will be shared by every target.
project.compile_config.set_std("c++20")
project.compile_config.add_define("TEST_DEFINE", "TEST")

main = project.add_executable("main", sources=["main.cpp"])
