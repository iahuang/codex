import os
import platform
from sys import stderr

enclosing_directory = os.path.dirname(os.path.abspath(__file__))

def error(message: str) -> None:
    print("error: " + message, file=stderr)
    exit(1)

# check for the codex/ module directory
module_directory = os.path.join(enclosing_directory, "codex")

if not os.path.exists(module_directory):
    error("Codex module not found. Please run this script from the codex directory.")

# verify that this script is being run on Unix
if platform.system() != "Linux" and platform.system() != "Darwin":
    error("This script is currently only supported on Mac and Linux.")

# verify that this script is being run with admin privileges
if os.geteuid() != 0:
    error("This script must be run with admin privileges.")

# generate executable
out = f"""#!/usr/bin/env python3
import sys
sys.path.append("{enclosing_directory}")

from codex.cli import run_cli
run_cli()
"""

# # create /usr/local/bin/codex
BIN_PATH = "/usr/local/bin/codex"
with open(BIN_PATH, "w") as f:
    f.write(out)

# make executable
os.chmod(BIN_PATH, 0o755)

