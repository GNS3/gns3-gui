#!/usr/bin/env python
#
# Copyright (C) 2023 GNS3 Technologies Inc.
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

# This script is intended to be built as a small executable for macOS to set the correct permissions on uBridge

import os
import shutil
import sys


def authorize_ubridge():

    path = shutil.which("ubridge", path=os.path.dirname(sys.executable))
    if path is None:
        raise SystemExit("Could not find ubridge executable at {}".format(path))
    try:
        shutil.chown(path, "root", "admin")
        os.chmod(path, 0o4750)
    except OSError as e:
        raise SystemExit("Could not authorize {}: {}".format(path, str(e)))


if __name__ == '__main__':
    authorize_ubridge()
