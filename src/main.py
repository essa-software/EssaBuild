import essabuild as eb
import essabuild.BuildSystem

import os
import sys


def main():
    # TODO: Use argparse
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} build | [run <target>]")
        return 1
    cwd = os.getcwd()
    command = sys.argv[1]
    eb.config.source_directory = cwd
    eb.config.build_directory = os.path.join(
        eb.config.source_directory, "build")

    do_build = command == "build" or command == "run"
    do_run = command == "run"
    if do_run:
        if len(sys.argv) != 3:
            print(f"Expected target name")
            return 1
        run_target = sys.argv[2]
    else:
        run_target = None

    filename = f"{eb.config.source_directory}/build.py"

    print(f"Source dir: {eb.config.source_directory}")
    print(f"Build dir:  {eb.config.build_directory}")
    try:
        with open(filename) as f:
            sys.path.append(os.path.dirname(__file__))
            compiled = compile(f.read(), filename, "exec")
            exec(compiled)
    except FileNotFoundError:
        print(f"There is no EssaBuild project in {cwd}.")
    except SystemError as e:
        print(f"Failed to open build.py: {e}")

    try:
        essabuild.BuildSystem.main(
            build=do_build, run=do_run, run_target=run_target)
    except Exception as e:
        print(e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
