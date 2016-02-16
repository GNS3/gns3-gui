#!/usr/bin/env python3

"""
Script to build all the PyQt user interfaces and resources for this project.
"""

import os
import sys
import stat
import shutil
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--force", help="force rebuild all files", action="store_true")
parser.add_argument("--ressources", help="force rebuild ressources", action="store_true")
args = parser.parse_args()

if sys.platform.startswith('win'):
    PATH = os.path.join(os.path.dirname(sys.executable), "Lib\\site-packages\\PyQt5")
    if os.access(os.path.join(PATH, "bin"), os.R_OK):
        PATH = os.path.join(PATH, "bin")
    PYUIC = os.path.join(PATH, "pyuic5")
    PYRCC = os.path.join(PATH, "pyrcc5")
else:
    PYUIC = shutil.which("pyuic5")
    PYRCC = shutil.which("pyrcc5")


def build_ui(path):
    for file in os.listdir(path):
        source = os.path.join(path, file)
        if source.endswith(".ui"):
            target = os.path.join(path, file.replace(".ui", "_ui.py"))
            if not os.access(target, os.F_OK) or (os.stat(source)[stat.ST_MTIME] > os.stat(target)[stat.ST_MTIME]) or args.force:
                command = [PYUIC, "--from-imports", "-o", target, source]
                print("Building UI {}".format(source))
                if args.force and os.access(target, os.F_OK):
                    os.remove(target)

                if sys.platform.startswith('win'):
                    for i, arg in enumerate(command):
                        command[i] = '"' + arg.replace('"', '"""') + '"'
                    command = ' '.join(command)
                    subprocess.call(command, shell=True)
                else:
                    subprocess.call(command)


def build_resources(path, target):
    for file in os.listdir(path):
        source = os.path.join(path, file)
        if source.endswith(".qrc"):
            target = os.path.join(target, file.replace(".qrc", "_rc.py"))
            if not os.access(target, os.F_OK) or (os.stat(source)[stat.ST_MTIME] > os.stat(target)[stat.ST_MTIME]) or args.force or args.ressources:
                command = [PYRCC, "-compress", "9", "-o", target, source]
                print("Building resources {}".format(source))
                if args.force and os.access(target, os.F_OK):
                    os.remove(target)
                if sys.platform.startswith('win'):
                    for i, arg in enumerate(command):
                        command[i] = '"' + arg.replace('"', '"""') + '"'
                    command = ' '.join(command)
                subprocess.call(command)


def recursive(function, path):
    for root, dirs, _ in os.walk(path):
        for directory in dirs:
            function(os.path.join(root, directory))


if __name__ == '__main__':

    if not PYUIC or not PYRCC:
        raise SystemExit("pyuic5 or pyrcc5 could't be found, please install PyQt5 development tools (e.g. pyqt5-dev-tools)")

    cwd = os.path.dirname(os.path.abspath(__file__))
    gns3_path = os.path.abspath(os.path.join(cwd, "../gns3/"))
    ui_path = os.path.abspath(os.path.join(cwd, "../gns3/ui"))
    recursive(build_ui, gns3_path)
    rcc_path = os.path.abspath(os.path.join(cwd, "../resources"))
    build_resources(rcc_path, ui_path)
