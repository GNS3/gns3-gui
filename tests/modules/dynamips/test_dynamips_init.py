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


from unittest.mock import patch
from gns3.modules.dynamips import Dynamips


def test_getDefaultIdlePC(tmpdir):

    fake_img = str(tmpdir / 'fake')
    open(fake_img, 'w+').close()

    # Unknow image
    assert Dynamips.getDefaultIdlePC(fake_img) is None

    # Know image with full path
    with patch('gns3.modules.dynamips.Dynamips._md5sum', return_value='7f4ae12a098391bc0edcaf4f44caaf9d'):
        assert Dynamips.getDefaultIdlePC(fake_img) == '0x80358a60'

    # Know image with relative path
    with patch('gns3.image_manager.ImageManager.getDirectoryForType', return_value=str(tmpdir)):
        with patch('gns3.modules.dynamips.Dynamips._md5sum', return_value='7f4ae12a098391bc0edcaf4f44caaf9d'):
            assert Dynamips.getDefaultIdlePC('fake') == '0x80358a60'
