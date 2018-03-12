# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 GNS3 Technologies Inc.
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

from unittest.mock import MagicMock


@pytest.fixture
def real_main_window():
    from gns3.main_window import MainWindow
    return MainWindow()


def test_main_window_settings_changed_signal(real_main_window):
    settings = real_main_window.settings()
    signal = MagicMock()
    real_main_window.settings_updated_signal = signal
    real_main_window.setSettings(settings)
    assert signal.emit.called


def test_main_window_settings_changed_slot(real_main_window):
    instance = MagicMock()
    manager = MagicMock()
    manager.instance.return_value = instance
    real_main_window._appliance_manager =  manager
    real_main_window.settingsChangedSlot()
    assert instance.refresh.called
