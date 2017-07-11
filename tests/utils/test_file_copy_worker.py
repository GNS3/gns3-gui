# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 GNS3 Technologies Inc.
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

import os
import stat
import tempfile
from unittest.mock import patch

from gns3.utils.file_copy_worker import FileCopyWorker


def test_file_copy_worker_with_preserve_permissions():
    source_fp, source = tempfile.mkstemp()
    destination_fp, destination = tempfile.mkstemp()

    st = os.stat(source)
    os.chmod(source, st.st_mode | stat.S_IEXEC)
    assert os.access(source, os.X_OK)

    with patch('gns3.utils.file_copy_worker.FileCopyWorker.finished'):
        worker = FileCopyWorker(source, destination)
        worker.run()
        assert os.access(destination, os.X_OK)

    os.close(source_fp)
    os.close(destination_fp)
    os.remove(source)
    os.remove(destination)
