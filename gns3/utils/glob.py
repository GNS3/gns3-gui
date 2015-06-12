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
import re
import os
import glob


def glob_escape(path):
    """
    Escape all special chars for glob.
    For Python after 3.4 we use the glob.escape method.

    :returns: Escaped path
    """

    if sys.version_info < (3, 4):
        # Extracted from Python 3.4 source code
        # Escaping is done by wrapping any of "*?[" between square brackets.
        # Metacharacters do not work in the drive part and shouldn't be escaped.
        magic_check = re.compile('([*?[])')
        magic_check_bytes = re.compile(b'([*?[])')
        drive, pathname = os.path.splitdrive(pathname)
        if isinstance(pathname, bytes):
            pathname = magic_check_bytes.sub(br'[\1]', pathname)
        else:
            pathname = magic_check.sub(r'[\1]', pathname)
        return drive + pathname
    else:
        return glob.escape(path)

