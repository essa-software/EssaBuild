import essabuild as eb


def generate_data(sources):
    import json
    import os
    with open(eb.config.source_file(sources[0])) as f:
        data = json.load(f)

    os.makedirs(eb.config.build_file("generated"), exist_ok=True)
    with open(eb.config.build_file("generated/Data.hpp"), "w") as f:
        f.write("namespace Data {\n")
        f.write("    struct Entry { const char* name; const char* value; };\n")
        f.write("    const Entry entries[] = {\n")
        for entry in data:
            f.write(f"        {{ \"{entry['name']}\", \"{entry['value']}\" }}, \n")
        f.write("    };")
        f.write("}")


project = eb.project("generation")

generator = project.add_generated("gen-data",
                                  generator=generate_data,
                                  sources=["data.json"])

target = project.add_executable("main", sources=["main.cpp"])
target.compile_config.add_option(f"-I{eb.config.build_directory}")
target.link(generator)
