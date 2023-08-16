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

import atexit
import logging
import os
import sys

try:
    import importlib_resources
except ImportError:
    from importlib import resources as importlib_resources


from contextlib import ExitStack
resource_manager = ExitStack()
atexit.register(resource_manager.close)

log = logging.getLogger(__name__)


def get_resource(resource_name):
    """
    Return a resource in current directory or in frozen package
    """

    resource_path = None
    if hasattr(sys, "frozen"):
        resource_path = os.path.normpath(os.path.join(os.path.dirname(sys.executable), resource_name))
    else:
        ref = importlib_resources.files("gns3") / resource_name
        path = resource_manager.enter_context(importlib_resources.as_file(ref))
        if os.path.exists(path):
            resource_path = os.path.normpath(path)
    return resource_path
