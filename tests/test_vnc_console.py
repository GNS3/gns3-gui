# -*- coding: utf-8 -*-
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

import os
import shlex
import pytest

from unittest.mock import patch
from gns3.vnc_console import vncConsole


def test_vnc_console_on_linux_and_mac(vpcs_device):
    with patch('subprocess.Popen') as popen, \
            patch('sys.platform', new="linux"):
            vpcs_device.settings()["console_host"] = "localhost"
            vncConsole(vpcs_device, 6000, 'command %h %p %P')
            popen.assert_called_once_with(shlex.split('command localhost 6000 100'), env=os.environ)


def test_vnc_console_on_windows(vpcs_device):
    with patch('subprocess.Popen') as popen, \
            patch('sys.platform', new="win"):
            vpcs_device.settings()["console_host"] = "localhost"
            vncConsole(vpcs_device, 6000, 'command %h %p %P')
            popen.assert_called_once_with('command localhost 6000 100')


# def test_vnc_console_on_linux_with_popen_issues():
#     with patch('subprocess.Popen', side_effect=OSError("Dummy")), \
#             patch('sys.platform', new="linux"):
#
#         with pytest.raises(OSError):
#             vncConsole('localhost', 6000, 'command %h %p %P')
