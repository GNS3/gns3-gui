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

import sys
import os
import shutil

from gns3.qt import QtCore, QtGui
from gns3.servers import Servers
from gns3.local_config import LocalConfig
from gns3.local_server_config import LocalServerConfig

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
        self._nodes = []
        self._ios_images_cache = {}

        # load the settings and IOS images.
        self._loadSettings()
        self._loadIOSRouters()

    @staticmethod
    def _findDynamips(self):
        """
        Finds the Dynamips path.

        :return: path to Dynamips
        """

        if sys.platform.startswith("win") and hasattr(sys, "frozen"):
            dynamips_path = os.path.join(os.getcwd(), "dynamips", "dynamips.exe")
        elif sys.platform.startswith("darwin") and hasattr(sys, "frozen"):
            dynamips_path = os.path.join(os.getcwd(), "dynamips")
        else:
            dynamips_path = shutil.which("dynamips")

        if dynamips_path is None:
            return ""
        return dynamips_path

    def _loadSettings(self):
        """
        Loads the settings from the persistent settings file.
        """

        local_config = LocalConfig.instance()
        # restore the Dynamips settings from QSettings (for backward compatibility)
        legacy_settings = {}
        settings = QtCore.QSettings()
        settings.beginGroup(self.__class__.__name__)
        for name in DYNAMIPS_SETTINGS.keys():
            if settings.contains(name):
                legacy_settings[name] = settings.value(name, type=DYNAMIPS_SETTING_TYPES[name])
        settings.remove("")
        settings.endGroup()

        if legacy_settings:
            local_config.saveSectionSettings(self.__class__.__name__, legacy_settings)
        self._settings = local_config.loadSectionSettings(self.__class__.__name__, DYNAMIPS_SETTINGS)

        if not os.path.exists(self._settings["dynamips_path"]):
            self._settings["dynamips_path"] = self._findDynamips(self)

        # keep the config file sync
        self._saveSettings()

    def _saveSettings(self):
        """
        Saves the settings to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, self._settings)

        # save some settings to the local server config file
        server_settings = {
            "allocate_aux_console_ports": self._settings["allocate_aux_console_ports"],
            "ghost_ios_support": self._settings["ghost_ios_support"],
            "sparse_memory_support": self._settings["sparse_memory_support"],
            "mmap_support": self._settings["mmap_support"],
        }

        if self._settings["dynamips_path"]:
            server_settings["dynamips_path"] = os.path.normpath(self._settings["dynamips_path"])
        config = LocalServerConfig.instance()
        config.saveSettings(self.__class__.__name__, server_settings)

    def _loadIOSRouters(self):
        """
        Load the IOS routers from the persistent settings file.
        """

        local_config = LocalConfig.instance()

        # restore the Dynamips VM settings from QSettings (for backward compatibility)
        ios_routers = []
        # load the settings
        settings = QtCore.QSettings()
        settings.beginGroup("IOSRouters")
        # load the VMs
        size = settings.beginReadArray("ios_router")
        for index in range(0, size):
            settings.setArrayIndex(index)
            router = {}
            for setting_name, default_value in IOS_ROUTER_SETTINGS.items():
                router[setting_name] = settings.value(setting_name, default_value, IOS_ROUTER_SETTING_TYPES[setting_name])

            for slot_id in range(0, 7):
                slot = "slot{}".format(slot_id)
                if settings.contains(slot):
                    router[slot] = settings.value(slot, "")

            for wic_id in range(0, 3):
                wic = "wic{}".format(wic_id)
                if settings.contains(wic):
                    router[wic] = settings.value(wic, "")

            platform = router["platform"]
            chassis = router["chassis"]

            if platform == "c7200":
                router["midplane"] = settings.value("midplane", "vxr")
                router["npe"] = settings.value("npe", "npe-400")
                router["slot0"] = settings.value("slot0", "C7200-IO-FE")
            else:
                router["iomem"] = 5

            if platform in ("c3725", "c3725", "c2691"):
                router["slot0"] = settings.value("slot0", "GT96100-FE")
            elif platform == "c3600" and chassis == "3660":
                router["slot0"] = settings.value("slot0", "Leopard-2FE")
            elif platform == "c2600" and chassis == "2610":
                router["slot0"] = settings.value("slot0", "C2600-MB-1E")
            elif platform == "c2600" and chassis == "2611":
                router["slot0"] = settings.value("slot0", "C2600-MB-2E")
            elif platform == "c2600" and chassis in ("2620", "2610XM", "2620XM", "2650XM"):
                router["slot0"] = settings.value("slot0", "C2600-MB-1FE")
            elif platform == "c2600" and chassis in ("2621", "2611XM", "2621XM", "2651XM"):
                router["slot0"] = settings.value("slot0", "C2600-MB-2FE")
            elif platform == "c1700" and chassis in ("1720", "1721", "1750", "1751", "1760"):
                router["slot0"] = settings.value("slot0", "C1700-MB-1FE")
            elif platform == "c1700" and chassis in ("1751", "1760"):
                router["slot0"] = settings.value("slot0", "C1700-MB-WIC1")

            ios_routers.append(router)

        settings.endArray()
        settings.remove("")
        settings.endGroup()

        if ios_routers:
            local_config.saveSectionSettings(self.__class__.__name__, {"routers": ios_routers})

        settings = local_config.settings()
        if "routers" in settings.get(self.__class__.__name__, {}):
            for router in settings[self.__class__.__name__]["routers"]:
                name = router.get("name")
                server = router.get("server")
                key = "{server}:{name}".format(server=server, name=name)
                if key in self._ios_routers or not name or not server:
                    continue
                self._ios_routers[key] = router

        # keep things sync
        self._saveIOSRouters()

    def _saveIOSRouters(self):
        """
        Saves the IOS routers to the persistent settings file.
        """

        # save the settings
        LocalConfig.instance().saveSectionSettings(self.__class__.__name__, {"routers": list(self._ios_routers.values())})

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

        self._settings.update(settings)
        self._saveSettings()

    def allocateServer(self, node_class, use_cloud=False):
        """
        Allocates a server.

        :param node_class: Node object

        :returns: allocated server (HTTPClient instance)
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

    def createNode(self, node_class, server, project):
        """
        Creates a new node.

        :param node_class: Node object
        :param server: HTTPClient instance
        :param project: Project instance
        """

        log.info("creating node {}".format(node_class))

        # create an instance of the node class
        return node_class(self, server, project)

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

            if not ios_router:
                raise ModuleError("No IOS router for platform {}".format(node.settings()["platform"]))

            #  TODO: improve this part
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

            if "disk0" in ios_router:
                settings["disk0"] = ios_router["disk0"]

            if "disk1" in ios_router:
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
            node.setup(ios_router["path"], ios_router["ram"], additional_settings=settings, base_name=base_name)
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
        Resets the module.
        """

        log.info("Dynamips module reset")
        self._nodes.clear()

    def save(self):
        """
        Called when a project is saved.
        """

        # save all the configs for all nodes.
        for node in self._nodes:
            if isinstance(node, Router) and node.initialized():
                node.saveConfigs()

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
