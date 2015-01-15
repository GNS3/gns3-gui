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

"""
Dynamips module implementation.
"""

import os
import glob

from gns3.qt import QtCore, QtGui
from gns3.servers import Servers

from ..module import Module
from ..module_error import ModuleError
from .nodes.router import Router
from .nodes.c1700 import C1700
from .nodes.c2600 import C2600
from .nodes.c2691 import C2691
from .nodes.c3600 import C3600
from .nodes.c3725 import C3725
from .nodes.c3745 import C3745
from .nodes.c7200 import C7200
from .nodes.etherswitch_router import EtherSwitchRouter
from .nodes.ethernet_switch import EthernetSwitch
from .nodes.ethernet_hub import EthernetHub
from .nodes.frame_relay_switch import FrameRelaySwitch
from .nodes.atm_switch import ATMSwitch
from .settings import DYNAMIPS_SETTINGS, DYNAMIPS_SETTING_TYPES
from .settings import IOS_ROUTER_SETTINGS, IOS_ROUTER_SETTING_TYPES
from .settings import PLATFORMS_DEFAULT_RAM

PLATFORM_TO_CLASS = {
    "c1700": C1700,
    "c2600": C2600,
    "c2691": C2691,
    "c3600": C3600,
    "c3725": C3725,
    "c3745": C3745,
    "c7200": C7200
}


import logging
log = logging.getLogger(__name__)


class Dynamips(Module):
    """
    Dynamips module.
    """

    def __init__(self):
        Module.__init__(self)

        self._settings = {}
        self._ios_routers = {}
        self._servers = []
        self._nodes = []
        self._working_dir = ""
        self._images_dir = ""
        self._ios_images_cache = {}

        # load the settings and IOS images.
        self._loadSettings()
        self._loadIOSRouters()

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in DYNAMIPS_SETTINGS.items():
            self._settings[name] = settings.value(name, value, type=DYNAMIPS_SETTING_TYPES[name])
        settings.endGroup()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name, value in self._settings.items():
            settings.setValue(name, value)
        settings.endGroup()

    def _loadIOSRouters(self):
        """
        Load the IOS routers from the persistent settings file.
        """

        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOSRouters")

        # load the IOS images
        size = settings.beginReadArray("ios_router")
        for index in range(0, size):
            settings.setArrayIndex(index)
            name = settings.value("name")
            server = settings.value("server")
            key = "{server}:{name}".format(server=server, name=name)
            if key in self._ios_routers or not name or not server:
                continue
            self._ios_routers[key] = {}
            for setting_name, default_value in IOS_ROUTER_SETTINGS.items():
                self._ios_routers[key][setting_name] = settings.value(setting_name, default_value, IOS_ROUTER_SETTING_TYPES[setting_name])

            for slot_id in range(0, 7):
                slot = "slot{}".format(slot_id)
                if settings.contains(slot):
                    self._ios_routers[key][slot] = settings.value(slot, "")

            for wic_id in range(0, 3):
                wic = "wic{}".format(wic_id)
                if settings.contains(wic):
                    self._ios_routers[key][wic] = settings.value(wic, "")

            platform = self._ios_routers[key]["platform"]
            chassis = self._ios_routers[key]["chassis"]

            if platform == "c7200":
                self._ios_routers[key]["midplane"] = settings.value("midplane", "vxr")
                self._ios_routers[key]["npe"] = settings.value("npe", "npe-400")
                self._ios_routers[key]["slot0"] = settings.value("slot0", "C7200-IO-FE")
            else:
                self._ios_routers[key]["iomem"] = 5

            if platform in ("c3725", "c3725", "c2691"):
                self._ios_routers[key]["slot0"] = settings.value("slot0", "GT96100-FE")
            elif platform == "c3600" and chassis == "3660":
                self._ios_routers[key]["slot0"] = settings.value("slot0", "Leopard-2FE")
            elif platform == "c2600" and chassis == "2610":
                self._ios_routers[key]["slot0"] = settings.value("slot0", "C2600-MB-1E")
            elif platform == "c2600" and chassis == "2611":
                self._ios_routers[key]["slot0"] = settings.value("slot0", "C2600-MB-2E")
            elif platform == "c2600" and chassis in ("2620", "2610XM", "2620XM", "2650XM"):
                self._ios_routers[key]["slot0"] = settings.value("slot0", "C2600-MB-1FE")
            elif platform == "c2600" and chassis in ("2621", "2611XM", "2621XM", "2651XM"):
                self._ios_routers[key]["slot0"] = settings.value("slot0", "C2600-MB-2FE")
            elif platform == "c1700" and chassis in ("1720", "1721", "1750", "1751", "1760"):
                self._ios_routers[key]["slot0"] = settings.value("slot0", "C1700-MB-1FE")
            elif platform == "c1700" and chassis in ("1751", "1760"):
                self._ios_routers[key]["slot0"] = settings.value("slot0", "C1700-MB-WIC1")

        settings.endArray()
        settings.endGroup()

    def _saveIOSRouters(self):
        """
        Saves the IOS routers to the persistent settings file.
        """

        # save the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOSRouters")
        settings.remove("")

        # save the IOS images
        settings.beginWriteArray("ios_router", len(self._ios_routers))
        index = 0
        for ios_router in self._ios_routers.values():
            settings.setArrayIndex(index)
            for name, value in ios_router.items():
                settings.setValue(name, value)
            index += 1
        settings.endArray()
        settings.endGroup()

    def _delete_dynamips_files(self):
        """
        Deletes useless local Dynamips files from the working directory
        """

        files = glob.glob(os.path.join(self._working_dir, "dynamips", "*.ghost"))
        files += glob.glob(os.path.join(self._working_dir, "dynamips", "*_lock"))
        files += glob.glob(os.path.join(self._working_dir, "dynamips", "ilt_*"))
        files += glob.glob(os.path.join(self._working_dir, "dynamips", "c[0-9][0-9][0-9][0-9]_*_rommon_vars"))
        files += glob.glob(os.path.join(self._working_dir, "dynamips", "c[0-9][0-9][0-9][0-9]_*_ssa"))
        for file in files:
            try:
                log.debug("deleting file {}".format(file))
                os.remove(file)
            except OSError as e:
                log.warn("could not delete file {}: {}".format(file, e))
                continue

    def setProjectFilesDir(self, path):
        """
        Sets the project files directory path this module.

        :param path: path to the local project files directory
        """

        #self._delete_dynamips_files()  #FIXME: cause issues
        self._working_dir = path
        log.info("local working directory for Dynamips module: {}".format(self._working_dir))

        # update the server with the new working directory / project name
        for server in self._servers:
            if server.connected():
                self._sendSettings(server)

    def setImageFilesDir(self, path):
        """
        Sets the image files directory path this module.

        :param path: path to the local image files directory
        """

        self._images_dir = os.path.join(path, "IOS")

    def imageFilesDir(self):
        """
        Returns the files directory path this module.

        :returns: path to the local image files directory
        """

        return self._images_dir

    def addServer(self, server):
        """
        Adds a server to be used by this module.

        :param server: WebSocketClient instance
        """

        log.info("adding server {}:{} to Dynamips module".format(server.host, server.port))
        self._servers.append(server)
        self._sendSettings(server)

    def removeServer(self, server):
        """
        Removes a server from being used by this module.

        :param server: WebSocketClient instance
        """

        log.info("removing server {}:{} from Dynamips module".format(server.host, server.port))
        self._servers.remove(server)

    def servers(self):
        """
        Returns all the servers used by this module.

        :returns: list of WebSocketClient instances
        """

        return self._servers

    def addNode(self, node):
        """
        Adds a node to this module.

        :param node: Node instance
        """

        self._nodes.append(node)

    def removeNode(self, node):
        """
        Removes a node from this module.

        :param node: Node instance
        """

        if node in self._nodes:
            self._nodes.remove(node)

    def iosRouters(self):
        """
        Returns IOS routers settings.

        :returns: IOS routers settings (dictionary)
        """

        return self._ios_routers

    def setIOSRouters(self, new_ios_routers):
        """
        Sets IOS images settings.

        :param new_ios_routers: IOS images settings (dictionary)
        """

        self._ios_routers = new_ios_routers.copy()
        self._saveIOSRouters()

    def settings(self):
        """
        Returns the module settings

        :returns: module settings (dictionary)
        """

        return self._settings

    def setSettings(self, settings):
        """
        Sets the module settings

        :param settings: module settings (dictionary)
        """

        params = {}
        for name, value in settings.items():
            if name in self._settings and self._settings[name] != value:
                params[name] = value

        if params:
            for server in self._servers:
                if server.isLocal():
                    params.update({"working_dir": self._working_dir})
                else:
                    if "path" in params:
                        del params["path"]  # do not send Dynamips path to remote servers
                    project_name = os.path.basename(self._working_dir)
                    if project_name.endswith("-files"):
                        project_name = project_name[:-6]
                    params.update({"project_name": project_name})
                server.send_notification("dynamips.settings", params)

        self._settings.update(settings)
        self._saveSettings()

    def _sendSettings(self, server):
        """
        Sends the module settings to the server.

        :param server: WebSocketClient instance
        """

        log.info("sending Dynamips settings to server {}:{}".format(server.host, server.port))
        params = self._settings.copy()
        # send the local working directory only if this is a local server
        if server.isLocal():
            params.update({"working_dir": self._working_dir})
        else:
            if "path" in params:
                del params["path"]  # do not send Dynamips path to remote servers
            project_name = os.path.basename(self._working_dir)
            if project_name.endswith("-files"):
                project_name = project_name[:-6]
            params.update({"project_name": project_name})
        server.send_notification("dynamips.settings", params)

    def allocateServer(self, node_class, use_cloud=False):
        """
        Allocates a server.

        :param node_class: Node object

        :returns: allocated server (WebSocketClient instance)
        """

        # allocate a server for the node
        servers = Servers.instance()

        if use_cloud:
            from ...topology import Topology
            topology = Topology.instance()
            top_instance = topology.anyInstance()
            server = servers.getCloudServer(top_instance.host, top_instance.port, top_instance.ssl_ca_file)
        else:
            if self._settings["use_local_server"]:
                # use the local server
                server = servers.localServer()
            else:
                # pick up a remote server (round-robin method)
                server = next(iter(servers))
                if not server:
                    raise ModuleError("No remote server is configured")
        return server

    def createNode(self, node_class, server):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: WebSocketClient instance
        """

        log.info("creating node {}".format(node_class))

        if not server.connected():
            try:
                log.info("reconnecting to server {}:{}".format(server.host, server.port))
                server.reconnect()
            except OSError as e:
                raise ModuleError("Could not connect to server {}:{}: {}".format(server.host,
                                                                                 server.port,
                                                                                 e))
        if server not in self._servers:
            self.addServer(server)

        # create an instance of the node class
        return node_class(self, server)

    def setupNode(self, node, node_name):
        """
        Setups a node.

        :param node: Node instance
        :param node_name: Node name
        """

        log.info("configuring node {}".format(node))

        if isinstance(node, Router):

            ios_router = None
            if node_name:
                for ios_key, info in self._ios_routers.items():
                    if node_name == info["name"]:
                        ios_router = self._ios_routers[ios_key]
                        break

            # # hack for EtherSwitch router
            # if isinstance(node, EtherSwitchRouter) and node.server() == Servers.instance().localServer():
            #     for info in self._ios_routers.values():
            #         if info["platform"] == "c3725" and info["server"] == "local":
            #             ios_router = {
            #                 "platform": "c3725",
            #                 "path": info["path"],
            #                 "ram": info["ram"],
            #                 "startup_config": info["startup_config"],
            #             }
            #             break
            #     if not ios_router:
            #         raise ModuleError("Please create an c3725 IOS router in order to use an EtherSwitch router")

            if not ios_router:
                raise ModuleError("No IOS router for platform {}".format(node.settings()["platform"]))

            settings = {}
            # set initial settings like the chassis or an Idle-PC value etc.
            if "chassis" in ios_router and ios_router["chassis"]:
                settings["chassis"] = ios_router["chassis"]
            if "idlepc" in ios_router and ios_router["idlepc"]:
                settings["idlepc"] = ios_router["idlepc"]
            if ios_router["startup_config"]:
                settings["startup_config"] = ios_router["startup_config"]
            if "private_config" in ios_router and ios_router["private_config"]:
                settings["private_config"] = ios_router["private_config"]

            if ios_router["platform"] == "c7200":
                settings["midplane"] = ios_router["midplane"]
                settings["npe"] = ios_router["npe"]
            elif "iomem" in ios_router:
                settings["iomem"] = ios_router["iomem"]

            if "nvram" in ios_router and ios_router["nvram"]:
                settings["nvram"] = ios_router["nvram"]

            if "disk0" in ios_router and ios_router["disk0"]:
                settings["disk0"] = ios_router["disk0"]

            if "disk1" in ios_router and ios_router["disk1"]:
                settings["disk1"] = ios_router["disk1"]

            for slot_id in range(0, 7):
                slot = "slot{}".format(slot_id)
                if slot in ios_router:
                    settings[slot] = ios_router[slot]
            for wic_id in range(0, 3):
                wic = "wic{}".format(wic_id)
                if wic in ios_router:
                    settings[wic] = ios_router[wic]

            base_name = "R"
            if "slot1" in settings and settings["slot1"] == "NM-16ESW":
                # must be an EtherSwitch router
                base_name = "ESW"
            node.setup(ios_router["path"], ios_router["ram"], initial_settings=settings, base_name=base_name)
        else:
            node.setup()

    def updateImageIdlepc(self, image_path, idlepc):
        """
        Updates the Idle-PC for an IOS image.

        :param image_path: path to the IOS image
        :param idlepc: Idle-PC value
        """

        for ios_router in self._ios_routers.values():
            if ios_router["path"] == image_path:
                if ios_router["idlepc"] != idlepc:
                    ios_router["idlepc"] = idlepc
                    self._saveIOSRouters()
                break

    def reset(self):
        """
        Resets the servers and nodes.
        """

        log.info("Dynamips module reset")
        for server in self._servers:
            if server.connected():
                server.send_notification("dynamips.reset")
        self._servers.clear()

        for node in self._nodes:
            node.reset()
        self._nodes.clear()

    def notification(self, destination, params):
        """
        To received notifications from the server.

        :param destination: JSON-RPC method
        :param params: JSON-RPC params
        """

        if "devices" in params:
            for node in self._nodes:
                for device in params["devices"]:
                    if node.name() == device:
                        message = "node {}: {}".format(node.name(), params["message"])
                        self.notification_signal.emit(message, params["details"])
                        if hasattr(node, "stop"):
                            node.stop()

    def exportConfigs(self, directory):
        """
        Exports all configs for all nodes to a directory.

        :param directory: destination directory path
        """

        for node in self._nodes:
            if isinstance(node, Router) and node.initialized():
                node.exportConfigToDirectory(directory)

    def importConfigs(self, directory):
        """
        Imports configs to all nodes from a directory.

        :param directory: source directory path
        """

        for node in self._nodes:
            if isinstance(node, Router) and node.initialized():
                node.importConfigFromDirectory(directory)

    def findAlternativeIOSImage(self, image, node):
        """
        Tries to find an alternative IOS image.

        :param image: image name
        :param node: requesting Node instance

        :return: IOS image (dictionary)
        """

        if image in self._ios_images_cache:
            return self._ios_images_cache[image]

        from gns3.main_window import MainWindow
        mainwindow = MainWindow.instance()
        ios_routers = self.iosRouters()
        candidate_ios_images = {}
        alternative_image = {"path": image,
                             "ram": None,
                             "idlepc": None}

        # find all images with the same platform and local server
        for ios_router in ios_routers.values():
            if ios_router["platform"] == node.settings()["platform"] and ios_router["server"] == "local":
                candidate_ios_images[ios_router["image"]] = ios_router

        if candidate_ios_images:
            selection, ok = QtGui.QInputDialog.getItem(mainwindow,
                                                       "IOS image", "IOS image {} could not be found\nPlease select an alternative from your existing images:".format(image),
                                                       list(candidate_ios_images.keys()), 0, False)
            if ok:
                ios_image = candidate_ios_images[selection]
                alternative_image["path"] = ios_router["path"]
                alternative_image["ram"] = ios_router["ram"]
                alternative_image["idlepc"] = ios_router["idlepc"]
                self._ios_images_cache[image] = alternative_image
                return alternative_image

        # no registered IOS image is used, let's just ask for an IOS image path
        QtGui.QMessageBox.critical(mainwindow, "IOS image", "Could not find the {} IOS image \nPlease select a similar IOS image!".format(image))
        from .pages.ios_router_preferences_page import IOSRouterPreferencesPage
        path = IOSRouterPreferencesPage.getIOSImage(mainwindow)
        if path:
            alternative_image["path"] = path
            self._ios_images_cache[image] = alternative_image
        return alternative_image

    @staticmethod
    def getNodeClass(name):
        """
        Returns the object with the corresponding name.

        :param name: object name
        """

        if name in globals():
            return globals()[name]
        return None

    @staticmethod
    def classes():
        """
        Returns all the node classes supported by this module.

        :returns: list of classes
        """

        return [C1700, C2600, C2691, C3600, C3725, C3745, C7200, EtherSwitchRouter, EthernetSwitch, EthernetHub, FrameRelaySwitch, ATMSwitch]

    def nodes(self):
        """
        Returns all the node data necessary to represent a node
        in the nodes view and create a node on the scene.
        """

        server = "local"
        if not self._settings["use_local_server"]:
            # pick up a remote server (round-robin method)
            remote_server = next(iter(Servers.instance()))
            if remote_server:
                server = "{}:{}".format(remote_server.host, remote_server.port)

        nodes = []
        for node_class in [EthernetSwitch, EthernetHub, FrameRelaySwitch, ATMSwitch]:
            nodes.append(
                {"class": node_class.__name__,
                 "name": node_class.symbolName(),
                 "server": server,
                 "categories": node_class.categories(),
                 "default_symbol": node_class.defaultSymbol(),
                 "hover_symbol": node_class.hoverSymbol()}
            )

        for ios_router in self._ios_routers.values():
            node_class = PLATFORM_TO_CLASS[ios_router["platform"]]
            nodes.append(
                {"class": node_class.__name__,
                 "name": ios_router["name"],
                 "server": ios_router["server"],
                 "default_symbol": ios_router["default_symbol"],
                 "hover_symbol": ios_router["hover_symbol"],
                 "categories": [ios_router["category"]]}
            )

        return nodes

    @staticmethod
    def preferencePages():
        """
        :returns: QWidget object list
        """

        from .pages.dynamips_preferences_page import DynamipsPreferencesPage
        from .pages.ios_router_preferences_page import IOSRouterPreferencesPage
        return [DynamipsPreferencesPage, IOSRouterPreferencesPage]

    @staticmethod
    def instance():
        """
        Singleton to return only on instance of Dynamips.

        :returns: instance of Dynamips
        """

        if not hasattr(Dynamips, "_instance"):
            Dynamips._instance = Dynamips()
        return Dynamips._instance
