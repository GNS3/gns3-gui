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


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errcode = tox.cmdline(self.test_args)
        sys.exit(errcode)

setup(
    name="gns3-gui",
    version=__import__("gns3").__version__,
    url="http://github.com/GNS3/gns3-gui",
    license="GNU General Public License v3 (GPLv3)",
    tests_require=["tox"],
    cmdclass={"test": Tox},
    author="Jeremy Grossmann",
    author_email="package-maintainer@gns3.net",
    description="GNS3 graphical interface for the GNS3 server.",
    long_description=open("README.rst", "r").read(),
    install_requires=[
        "apache-libcloud>=0.14.1",
        "requests==2.4.3",
        "paramiko==1.15.1",
        "gns3-converter",
        "raven==5.2.0"
    ],
    entry_points={
        "gui_scripts": [
            "gns3 = gns3.main:main",
        ]
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={"gns3": ["configs/*.txt"]},
    platforms="any",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Natural Language :: English',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
