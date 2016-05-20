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


from ..compute_manager import ComputeManager
from ..qt import QtWidgets


def server_select(parent, allow_local_server=True):
    """
    Show a popup asking user to choose a server

    If only local server is available return it by default

    :params parent: Parent window
    :params allow_local_server: Boolean Is local server allowed
    :returns: Server or None
    """

    server_list = []

    for compute in ComputeManager.instance().computes():
        if compute.id() == "local" and allow_local_server:
            server_list.append(compute.name())

    for compute in ComputeManager.instance().computes():
        if not compute.id() == "local":
            server_list.append(compute.name())

    if len(server_list) == 0:
        raise ValueError("No server available")
    elif len(server_list) == 1:
        selection = server_list[0]
    else:
        print(server_list)
        (selection, ok) = QtWidgets.QInputDialog.getItem(parent, "Server", "Please choose a server", server_list, 0, False)
        if not ok:
            return None

    for compute in ComputeManager.instance().computes():
        if selection == compute.name():
            return compute
