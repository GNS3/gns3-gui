#!/usr/bin/env python3

"""
Script to build all the PyQt user interfaces and resources for this project.
"""

import os
import sys
import stat
import shutil
import subprocess
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--qt4", help="compilation with QT4", action="store_true")
parser.add_argument("--force", help="force rebuild all files", action="store_true")
args = parser.parse_args()

if args.qt4:
    if sys.platform.startswith('win'):
        PATH = os.path.join(os.path.dirname(sys.executable), "Lib\\site-packages\\PyQt4")
        if os.access(os.path.join(PATH, "bin"), os.R_OK):
            PATH = os.path.join(PATH, "bin")
        PYUIC = os.path.join(PATH, "pyuic4")
        PYRCC = os.path.join(PATH, "pyrcc4")
    else:
        PYUIC = shutil.which("pyuic4")
        PYRCC = shutil.which("pyrcc4")
    PYRCC_PYTHON3_FLAG = "-py3"
else:
    if sys.platform.startswith('win'):
        PATH = os.path.join(os.path.dirname(sys.executable), "Lib\\site-packages\\PyQt5")
        if os.access(os.path.join(PATH, "bin"), os.R_OK):
            PATH = os.path.join(PATH, "bin")
        PYUIC = os.path.join(PATH, "pyuic5")
        PYRCC = os.path.join(PATH, "pyrcc5")
    else:
        PYUIC = shutil.which("pyuic5")
        PYRCC = shutil.which("pyrcc5")
    PYRCC_PYTHON3_FLAG = None


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
                patch_file_qt4_5(target)


def build_resources(path, target):
    for file in os.listdir(path):
        source = os.path.join(path, file)
        if source.endswith(".qrc"):
            target = os.path.join(target, file.replace(".qrc", "_rc.py"))
            if not os.access(target, os.F_OK) or (os.stat(source)[stat.ST_MTIME] > os.stat(target)[stat.ST_MTIME]) or args.force:
                if PYRCC_PYTHON3_FLAG is not None:
                    command = [PYRCC, PYRCC_PYTHON3_FLAG, "-compress", "9", "-o", target, source]
                else:
                    command = [PYRCC, "-compress", "9", "-o", target, source]
                print("Building resources {}".format(source))
                if args.force and os.access(target, os.F_OK):
                    os.remove(target)
                if sys.platform.startswith('win'):
                    for i, arg in enumerate(command):
                        command[i] = '"' + arg.replace('"', '"""') + '"'
                    command = ' '.join(command)
                subprocess.call(command)
                patch_file_qt4_5(target)


def patch_file_qt4_5(target):
    """
    Patch a file for supporting Qt4 and Qt5
    """
    # We patch the file in order to support both version of Qt
    out = ""
    print("Patch {} for Qt4 and Qt5 support".format(target))
    original_from = re.compile(r"^from PyQt[45] ", re.U)
    original_translate = re.compile(r"_translate = QtCore\.QCoreApplication\.translate", re.U)
    gen_line = r"# Form implementation generated from reading ui file '";
    with open(target, 'r', encoding="utf-8") as f:
        for line in f.readlines():
            if line.startswith(gen_line):
                line = line[0:len(gen_line)] + line[line.rfind(os.sep)+len(os.sep):]
            line = original_from.sub("import gns3.qt\nfrom gns3.qt ", line)
            line = original_translate.sub("_translate = gns3.qt.translate", line)
            out += line
    with open(target, 'w', encoding="utf-8") as f:
        f.write(out)


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
