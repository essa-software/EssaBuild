import subprocess as sp


def sprun(cmd):
    # print(f"!! run {cmd}")
    result = sp.run(cmd.replace("\n", " "), shell=True)
    if result.returncode != 0:
        raise Exception(f"command failed: {cmd}")
