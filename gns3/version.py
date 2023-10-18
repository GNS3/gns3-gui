# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 GNS3 Technologies Inc.
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

# __version__ is a human-readable version number.

# __version_info__ is a four-tuple for programmatic comparison. The first
# three numbers are the components of the version number. The fourth
# is zero for an official release, positive for a development branch,
# or negative for a release candidate or beta (after the base version
# number has been incremented)

__version__ = "3.0.0a4"
__version_info__ = (3, 0, 0, -99)

if "dev" in __version__:
    try:
        import os
        import subprocess
        if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".git")):
            r = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip("\n")
            __version__ += "+" + r
    except Exception as e:
        print(e)
