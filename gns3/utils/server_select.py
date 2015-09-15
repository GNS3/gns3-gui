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


from ..servers import Servers
from ..modules import MODULES
from ..qt import QtWidgets


def server_select(parent):
    """
    Show a popup asking user to choose a server

    If only local server is available return it by default

    :params parent: Parent window
    :returns: Server or None
    """

    # check all other modules to find if they
    # are using a local server
    using_local_server = []
    for module in MODULES:
        if hasattr(module, "settings"):
            module_settings = module.instance().settings()
            if "use_local_server" in module_settings:
                using_local_server.append(module_settings["use_local_server"])

    servers = Servers.instance()
    local_server = servers.localServer()
    remote_servers = servers.remoteServers()
    gns3_vm = Servers.instance().vmServer()


    server_list = ["Local server ({})".format(local_server.url())]

    if not all(using_local_server) and (gns3_vm or len(remote_servers)):
        # a module is not using a local server
        server_list = ["Local server ({})".format(local_server.url())]
        if gns3_vm:
            server_list.append("GNS3 VM ({})".format(gns3_vm.url()))
        if len(remote_servers):
            if True not in using_local_server and len(remote_servers) == 1:
                # no module is using a local server and there is only one
                # remote server available, so no need to ask the user.
                return next(iter(servers))
            for remote_server in remote_servers.values():
                server_list.append("{}".format(remote_server.url()))

        (selection, ok) = QtWidgets.QInputDialog.getItem(parent, "Server", "Please choose a server", server_list, 0, False)
        if ok:
            if selection.startswith("Local server"):
                return local_server
            elif selection.startswith("GNS3 VM"):
                return gns3_vm
            else:
                for server in remote_servers.values():
                    if selection == server.url():
                        return server
        else:
            return None
    return local_server

