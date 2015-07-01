#!/usr/bin/env python
#
# Copyright (C) 2015 GNS3 Technologies Inc.
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

"""
This script fake GNS3 run as a frozen app.

Use it for testing stuff like self update.
"""

import os
import sys
import importlib

# Fake GNS3 run from a binary
sys.executable = os.path.realpath(__file__)

# Add site-package directory before cx_freeze directory
sys.path.insert(0, os.path.dirname(sys.executable))
sys.path.insert(0, os.path.join(os.path.dirname(sys.executable), 'site-packages'))

sys.frozen = True

module = importlib.import_module("gns3.main")
module.main()
