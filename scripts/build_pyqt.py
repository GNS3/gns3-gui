#!/usr/bin/env python3

"""
Script to build all the PyQt user interfaces and resources for this project.
"""

import os
import sys
import stat
import shutil
import subprocess


if sys.platform.startswith('win'):
    PATH = os.path.join(os.path.dirname(sys.executable), "Lib/site-packages/PyQt4")
    if os.access(os.path.join(PATH, "bin"), os.R_OK):
        PATH = os.path.join(PATH, "bin")
    PYUIC4 = os.path.join(PATH, "pyuic4")
    PYRCC4 = os.path.join(PATH, "pyrcc4")
else:
    PYUIC4 = shutil.which("pyuic4")
    PYRCC4 = shutil.which("pyrcc4")


def build_ui(path):
    for file in os.listdir(path):
        source = os.path.join(path, file)
        if source.endswith(".ui"):
            target = os.path.join(path, file.replace(".ui", "_ui.py"))
            if not os.access(target, os.F_OK) or (os.stat(source)[stat.ST_MTIME] > os.stat(target)[stat.ST_MTIME]):
                command = [PYUIC4, "--from-imports", "-o", target, source]
                print("Building UI {}".format(source))
                subprocess.call(command)


def build_resources(path, target):
    for file in os.listdir(path):
        source = os.path.join(path, file)
        if source.endswith(".qrc"):
            target = os.path.join(target, file.replace(".qrc", "_rc.py"))
            if not os.access(target, os.F_OK) or (os.stat(source)[stat.ST_MTIME] > os.stat(target)[stat.ST_MTIME]):
                command = [PYRCC4, "-py3", "-compress", "9", "-o", target, source]
                print("Building resources {}".format(source))
                subprocess.call(command)


def recursive(function, path):
    for root, dirs, _ in os.walk(path):
        for directory in dirs:
            function(os.path.join(root, directory))


if __name__ == '__main__':

    if not PYUIC4 or not PYRCC4:
        raise RuntimeError("pyuic4 or pyrcc4 could't be found, please install PyQt4 development tools")

    cwd = os.path.dirname(os.path.abspath(__file__))
    gns3_path = os.path.abspath(os.path.join(cwd, "../gns3/"))
    ui_path = os.path.abspath(os.path.join(cwd, "../gns3/ui"))
    recursive(build_ui, gns3_path)
    rcc_path = os.path.abspath(os.path.join(cwd, "../resources"))
    build_resources(rcc_path, ui_path)
