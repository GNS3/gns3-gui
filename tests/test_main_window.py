#!/usr/bin/env python
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

from unittest.mock import patch
from gns3.main_window import MainWindow


def test_new_project_when_dialog_is_already_available():
    main_window = MainWindow()
    with patch('gns3.main_window.ProjectDialog') as project_dialog_mock, \
            patch('gns3.topology.Topology.createLoadProject') as load_project_mock:

        main_window._project_dialog = project_dialog_mock()

        project_dialog_mock().exec_.return_value = 1
        project_dialog_mock().getProjectSettings.side_effect = AttributeError("Mocked")
        main_window._newProjectActionSlot()

        # load is not called when we handle the case
        assert load_project_mock.called is False
