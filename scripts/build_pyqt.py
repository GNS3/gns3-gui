#!/usr/bin/env python3

"""
Script to build all the PyQt user interfaces and resources for this project.
"""

import os
import platform
import stat
import shutil
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--force", help="force rebuild all files", action="store_true")
parser.add_argument("--resources", help="force rebuild resources", action="store_true")
args = parser.parse_args()

PYUIC = shutil.which("pyuic6")
PYRCC = shutil.which("pyrcc5")  # Using PyQt5's rcc as PyQt6's pyrcc6 does not exist


def build_ui(path):
    for file in os.listdir(path):
        source = os.path.join(path, file)
        if source.endswith(".ui"):
            target = os.path.join(path, file.replace(".ui", "_ui.py"))
            if not os.access(target, os.F_OK) or (os.stat(source)[stat.ST_MTIME] > os.stat(target)[stat.ST_MTIME]) or args.force:
                command = [PYUIC, "-o", target, source]
                print("Building UI {}".format(source))
                if args.force and os.access(target, os.F_OK):
                    os.remove(target)
                subprocess.call(command)

                if target == os.path.join(path, "main_window_ui.py"):
                    # Patch the main_window_ui.py to import resources_rc
                    # could potentially use https://github.com/domarm-comat/pyqt6rc instead
                    print("Patching UI {} to import resources".format(target))
                    with open(target, "a") as f:
                        f.write("from . import resources_rc")

def build_resources(path, target):
    for file in os.listdir(path):
        source = os.path.join(path, file)
        if source.endswith(".qrc"):
            target = os.path.join(target, file.replace(".qrc", "_rc.py"))
            if not os.access(target, os.F_OK) or (os.stat(source)[stat.ST_MTIME] > os.stat(target)[stat.ST_MTIME]) or args.force or args.resources:
                command = [PYRCC, "-compress", "9", "-o", target, source]
                print("Building resources {}".format(source))
                if args.force and os.access(target, os.F_OK):
                    os.remove(target)
                subprocess.call(command)

                # patch the .py resource file to replace PyQt5 by PyQt6
                print("Patching resources {}".format(target))
                with open(target, "r") as f:
                    content = f.read()
                content = content.replace("PyQt5", "PyQt6")
                with open(target, "w") as f:
                    f.write(content)

def recursive(function, path):
    for root, dirs, _ in os.walk(path):
        for directory in dirs:
            function(os.path.join(root, directory))


if __name__ == '__main__':

    if platform.system() != "Linux":
        raise SystemExit("This script can only be run on Linux.")

    if not PYUIC or not PYRCC:
        raise SystemExit("pyuic6 or pyrcc5 couldn't be found, please install PyQt5 and PyQt6 development tools (e.g. pyqt5-dev-tools)")

    cwd = os.path.dirname(os.path.abspath(__file__))
    gns3_path = os.path.abspath(os.path.join(cwd, "../gns3/"))
    ui_path = os.path.abspath(os.path.join(cwd, "../gns3/ui"))
    recursive(build_ui, gns3_path)
    rcc_path = os.path.abspath(os.path.join(cwd, "../resources"))
    build_resources(rcc_path, ui_path)
