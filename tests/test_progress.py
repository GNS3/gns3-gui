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

from gns3.progress import Progress


def test_context():
    progress = Progress(None, min_duration=500)
    assert progress._minimum_duration == 500
    assert progress._enable

    with progress.context(min_duration=0):
        assert progress._minimum_duration == 0
        assert progress._enable
    assert progress._minimum_duration == 500

    with progress.context(enable=False):
        assert progress._minimum_duration == 500
        assert progress._enable is False
    assert progress._enable

    with progress.context(allow_cancel_query=True, cancel_button_text="Hello"):
        assert progress._cancel_button_text == "Hello"
        assert progress._allow_cancel_query is True
    assert progress._cancel_button_text == ""
    assert progress._allow_cancel_query is False
