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


from .progress_dialog import ProgressDialog
from .wait_for_connection_thread import WaitForConnectionThread


def ConnectToServer(parent, server):

    thread = WaitForConnectionThread(server.host, server.port)
    thread.deleteLater()
    progress_dialog = ProgressDialog(thread,
                                     "Server {}".format(server.host),
                                     "Connecting to server {} on port {}...".format(server.host, server.port),
                                     "Cancel", busy=True, parent=parent)
    progress_dialog.show()
    success = progress_dialog.exec_()
    if not success:
        return False
    return True
