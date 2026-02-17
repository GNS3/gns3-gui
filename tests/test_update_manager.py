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

import pytest
import sys
import shutil
import tarfile
import os


from gns3.update_manager import UpdateManager
from gns3 import version


@pytest.fixture
def frozen():
    sys.frozen = True
    yield
    delattr(sys, 'frozen')


@pytest.fixture
def devVersion():
    old_version_info = version.__version_info__
    old_version = version.__version__
    version.__version_info__ = (1, 4, 0, -99)
    version.__version__ = '1.4.0'
    yield
    version.__version_info__ = old_version
    version.__version__ = old_version


@pytest.fixture
def stableVersion():
    old_version_info = version.__version_info__
    old_version = version.__version__
    version.__version_info__ = (1, 4, 0, 0)
    version.__version__ = '1.4.0'
    yield
    version.__version_info__ = old_version_info
    version.__version__ = old_version


@pytest.fixture
def update(tmpdir):
    update = UpdateManager()
    update._update_directory = str(tmpdir / 'updates')
    update._package_directory = str(tmpdir / 'site-packages')
    return update


@pytest.fixture
def gui_tar(tmpdir):
    tgz = str(tmpdir / 'updates' / 'gns3-gui.tar.gz')
    os.makedirs(str(tmpdir / 'updates'), exist_ok=True)
    os.makedirs(str(tmpdir / 'gns3-gui-master' / 'gns3'))
    open(str(tmpdir / 'gns3-gui-master' / 'gns3' / 'test.py'), 'w+').close()
    with tarfile.open(tgz, 'w:gz') as tar:
        tar.add(str(tmpdir / 'gns3-gui-master'), arcname='gns3-gui-master')
    shutil.rmtree(str(tmpdir / 'gns3-gui-master' / 'gns3'))
    return tgz


def test_isDevVersion(devVersion, update):
    assert update.isDevVersion() is True


def test_isDevVersion_stable(stableVersion, update):
    assert update.isDevVersion() is False


def test_installDownloadedUpdates(frozen, update, gui_tar, tmpdir):
    update.installDownloadedUpdates()
    assert os.path.exists(str(tmpdir / 'site-packages' / 'gns3' / 'test.py'))


def test_getLastVersionFromPyPiReply_Stable(update, stableVersion):
    body = {
        'releases': {
            '1.4.4rc1': [{'url': 'http://example.com'}],
            '1.4.3': [{'url': 'http://example.com'}],
            '1.4.1': [{'url': 'http://example.com'}],
            '1.4.2': [{'url': 'http://example.com'}]
        }
    }
    assert update._getLastMinorVersionFromPyPiReply(body) == '1.4.3'


def test_getLastVersionFromPyPiReply_Dev(update, devVersion):
    body = {
        'releases': {
            '1.4.2rc1': [{'url': 'http://example.com'}],
            '1.4.1': [{'url': 'http://example.com'}]
        }
    }
    assert update._getLastMinorVersionFromPyPiReply(body) == '1.4.2rc1'


def test_getLastVersionFromPyPiReplyNewMajor(update, stableVersion):
    body = {
        'releases': {
            '1.5': [{'url': 'http://example.com'}],
            '1.4.1': [{'url': 'http://example.com'}]
        }
    }
    assert update._getLastMinorVersionFromPyPiReply(body) == '1.4.1'
