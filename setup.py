# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# we only support Python 3 version >= 3.4
if len(sys.argv) >= 2 and sys.argv[1] == "install" and sys.version_info < (3, 4):
    raise SystemExit("Python 3.4 or higher is required")


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

if sys.platform.startswith('linux'):
    data_files = [
        ("share/applications/", ["resources/linux/applications/gns3.desktop"]),
        ("share/mime/packages", ["resources/linux/gns3-gui.xml"]),
        ("share/icons/hicolor/16x16/apps", ["resources/linux/icons/hicolor/16x16/apps/gns3.png"]),
        ("share/icons/hicolor/32x32/apps", ["resources/linux/icons/hicolor/32x32/apps/gns3.png"]),
        ("share/icons/hicolor/48x48/apps", ["resources/linux/icons/hicolor/48x48/apps/gns3.png"]),
        ("share/icons/hicolor/48x48/mimetypes", ["resources/linux/icons/hicolor/48x48/mimetypes/application-x-gns3.png",
                                                 "resources/linux/icons/hicolor/48x48/mimetypes/application-x-gns3appliance.png",
                                                 "resources/linux/icons/hicolor/48x48/mimetypes/application-x-gns3project.png"]),
        ("share/icons/hicolor/scalable/apps", ["resources/linux/icons/hicolor/scalable/apps/gns3.svg"]),
        ("share/icons/hicolor/scalable/mimetypes", ["resources/linux/icons/hicolor/scalable/mimetypes/application-x-gns3.svg",
                                                    "resources/linux/icons/hicolor/scalable/mimetypes/application-x-gns3appliance.svg",
                                                    "resources/linux/icons/hicolor/scalable/mimetypes/application-x-gns3project.svg"]),
    ]
else:
    data_files = []

setup(
    name="gns3-gui",
    version=__import__("gns3").__version__,
    url="http://github.com/GNS3/gns3-gui",
    license="GNU General Public License v3 (GPLv3)",
    tests_require=["pytest"],
    cmdclass={"test": PyTest},
    author="Jeremy Grossmann",
    author_email="package-maintainer@gns3.net",
    description="GNS3 graphical interface for the GNS3 server.",
    long_description=open("README.rst", "r").read(),
    install_requires=open("requirements.txt", "r").read().splitlines(),
    entry_points={
        "gui_scripts": [
            "gns3 = gns3.main:main"
        ]
    },
    data_files=data_files,
    packages=find_packages(".", exclude=["docs", "tests"]),
    include_package_data=True,
    package_data={"gns3": ["configs/*.txt", "schemas/*.json"]},
    platforms="any",
    python_requires=">=3.4",
    setup_requires=["setuptools>=17.1"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
