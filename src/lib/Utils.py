import subprocess as sp
import logging

def sprun(cmd):
    logging.debug(f"subprocess.run: {cmd}")
    result = sp.run(cmd.replace("\n", " "), shell=True)
    if result.returncode != 0:
        raise Exception(f"command failed: {cmd}")
