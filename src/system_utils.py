"""
System-level utilities.
"""

import os
import sys
import subprocess


def open_file(path):
    if sys.platform.startswith("darwin"):
        subprocess.call(["open", path])
    elif os.name == "nt":
        os.startfile(path)
    else:
        subprocess.call(["xdg-open", path])