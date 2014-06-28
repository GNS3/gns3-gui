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
Configuration page for Dynamips IOS routers.
"""

import os
import re
import sys
import pkg_resources
from gns3.qt import QtGui
from .. import Dynamips
from gns3.dialogs.node_configurator_dialog import ConfigurationError
from ..ui.router_configuration_page_ui import Ui_routerConfigPageWidget

# Network modules for the c2600 platform
C2600_NMS = (
    "NM-1FE-TX",
    "NM-1E",
    "NM-4E",
    "NM-16ESW"
)

# Network modules for the c3600 platform
C3600_NMS = (
    "NM-1FE-TX",
    "NM-1E",
    "NM-4E",
    "NM-16ESW",
    "NM-4T"
)

# Network modules for the c3700 platform
C3700_NMS = (
    "NM-1FE-TX",
    "NM-4T",
    "NM-16ESW",
)

# Port adapters for the c7200 platform
C7200_PAS = (
    "PA-A1",
    "PA-FE-TX",
    "PA-2FE-TX",
    "PA-GE",
    "PA-4T+",
    "PA-8T",
    "PA-4E",
    "PA-8E",
    "PA-POS-OC3",
)

# I/O controller for the c7200 platform
IO_C7200 = ("C7200-IO-FE",
            "C7200-IO-2FE",
            "C7200-IO-GE-E"
)

"""
Build the adapter compatibility matrix:

ADAPTER_MATRIX = {
    "c3600" : {                     # Router model
        "3620" : {                  # Router chassis (if applicable)
            { 0 : ("NM-1FE-TX", "NM_1E", ...)
            }
        }
    }
"""

ADAPTER_MATRIX = {}
for platform in ("c1700", "c2600", "c2691", "c3725", "c3745", "c3600", "c7200"):
    ADAPTER_MATRIX[platform] = {}

# 1700s have one interface on the MB, 2 sub-slots for WICs, an no NM slots
for chassis in ("1720", "1721", "1750", "1751", "1760"):
    ADAPTER_MATRIX["c1700"][chassis] = {0: "C1700-MB-1FE"}

# Add a fake NM in slot 1 on 1751s and 1760s to provide two WIC slots
for chassis in ("1751", "1760"):
    ADAPTER_MATRIX["c1700"][chassis][1] = "C1700_MB_WIC1"

# 2600s have one or more interfaces on the MB , 2 subslots for WICs, and an available NM slot 1
for chassis in ("2620", "2610XM", "2620XM", "2650XM"):
    ADAPTER_MATRIX["c2600"][chassis] = {0: "C2600-MB-1FE", 1: C2600_NMS}

for chassis in ("2621", "2611XM", "2621XM", "2651XM"):
    ADAPTER_MATRIX["c2600"][chassis] = {0: "C2600-MB-2FE", 1: C2600_NMS}

ADAPTER_MATRIX["c2600"]["2610"] = {0: "C2600-MB-1E", 1: C2600_NMS}
ADAPTER_MATRIX["c2600"]["2611"] = {0: "C2600-MB-2E", 1: C2600_NMS}

# 2691s have two FEs on the motherboard and one NM slot
ADAPTER_MATRIX["c2691"][""] = {0: "GT96100-FE", 1: C3700_NMS}

# 3620s have two generic NM slots
ADAPTER_MATRIX["c3600"]["3620"] = {}
for slot in range(2):
    ADAPTER_MATRIX["c3600"]["3620"][slot] = C3600_NMS

# 3640s have four generic NM slots
ADAPTER_MATRIX["c3600"]["3640"] = {}
for slot in range(4):
    ADAPTER_MATRIX["c3600"]["3640"][slot] = C3600_NMS

# 3660s have 2 FEs on the motherboard and 6 generic NM slots
ADAPTER_MATRIX["c3600"]["3660"] = {0: "Leopard-2FE"}
for slot in range(1, 7):
    ADAPTER_MATRIX["c3600"]["3660"][slot] = C3600_NMS

# 3725s have 2 FEs on the motherboard and 2 generic NM slots
ADAPTER_MATRIX["c3725"][""] = {0: "GT96100-FE"}
for slot in range(1, 3):
    ADAPTER_MATRIX["c3725"][""][slot] = C3700_NMS

# 3745s have 2 FEs on the motherboard and 4 generic NM slots
ADAPTER_MATRIX["c3745"][""] = {0: "GT96100-FE"}
for slot in range(1, 5):
    ADAPTER_MATRIX["c3745"][""][slot] = C3700_NMS

# 7206s allow an IO controller in slot 0, and a generic PA in slots 1-6
ADAPTER_MATRIX["c7200"][""] = {0: IO_C7200}
for slot in range(1, 7):
    ADAPTER_MATRIX["c7200"][""][slot] = C7200_PAS

C1700_WICS = ("WIC-1T", "WIC-2T", "WIC-1ENET")
C2600_WICS = ("WIC-1T", "WIC-2T")
C3700_WICS = ("WIC-1T", "WIC-2T")

WIC_MATRIX = {}

WIC_MATRIX["c1700"] = {0: C1700_WICS, 1: C1700_WICS}
WIC_MATRIX["c2600"] = {0: C2600_WICS, 1: C2600_WICS, 2: C2600_WICS}
WIC_MATRIX["c2691"] = {0: C3700_WICS, 1: C3700_WICS, 2: C3700_WICS}
WIC_MATRIX["c3725"] = {0: C3700_WICS, 1: C3700_WICS, 2: C3700_WICS}
WIC_MATRIX["c3745"] = {0: C3700_WICS, 1: C3700_WICS, 2: C3700_WICS}


class RouterConfigurationPage(QtGui.QWidget, Ui_routerConfigPageWidget):
    """
    QWidget configuration page for IOS routers.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self._widget_slots = {0: self.uiSlot0comboBox,
                              1: self.uiSlot1comboBox,
                              2: self.uiSlot2comboBox,
                              3: self.uiSlot3comboBox,
                              4: self.uiSlot4comboBox,
                              5: self.uiSlot5comboBox,
                              6: self.uiSlot6comboBox}

        self._widget_wics = {0: self.uiWic0comboBox,
                             1: self.uiWic1comboBox,
                             2: self.uiWic2comboBox}

        self.uiStartupConfigToolButton.clicked.connect(self._startupConfigBrowserSlot)
        self.uiPrivateConfigToolButton.clicked.connect(self._privateConfigBrowserSlot)

    def _startupConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a startup-config file.
        """

        if hasattr(sys, "frozen"):
            config_dir = "configs"
        else:
            config_dir = pkg_resources.resource_filename("gns3", "configs")
        path = QtGui.QFileDialog.getOpenFileName(self, "Select a startup configuration", config_dir)
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Startup configuration", "Cannot read {}".format(path))
            return

        self.uiStartupConfigLineEdit.clear()
        self.uiStartupConfigLineEdit.setText(path)

    def _privateConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a private-config file.
        """

        if hasattr(sys, "frozen"):
            config_dir = "configs"
        else:
            config_dir = pkg_resources.resource_filename("gns3", "configs")
        path = QtGui.QFileDialog.getOpenFileName(self, "Select a private configuration", config_dir)
        if not path:
            return

        if not os.access(path, os.R_OK):
            QtGui.QMessageBox.critical(self, "Private configuration", "Cannot read {}".format(path))
            return

        self.uiPrivateConfigLineEdit.clear()
        self.uiPrivateConfigLineEdit.setText(path)

    def _loadAdapterConfig(self, platform, chassis, settings):
        """
        Loads the adapter and WIC configuration.

        :param platform: the router platform (string)
        :param chassis: the router chassis (string)
        :param settings: the router settings (dictionary)
        """

        # clear all the slot combo boxes.
        for widget in self._widget_slots.values():
            widget.clear()
            widget.setEnabled(False)

        # load the available adapters to the correct slot for the corresponding platform and chassis
        for slot_number, slot_adapters in ADAPTER_MATRIX[platform][chassis].items():
            self._widget_slots[slot_number].setEnabled(True)

            if type(slot_adapters) == str:
                # only one default adapter for this slot.
                self._widget_slots[slot_number].addItem(slot_adapters)
#             elif platform == "c7200" and slot_number == 0 and settings["slot0"] != None:
#                 # special case
#                 self._widget_slots[slot_number].addItem(settings["slot0"])
            else:
                # list of adapters
                module_list = list(slot_adapters)
                self._widget_slots[slot_number].addItems([""] + module_list)

            # set the combox box to the correct slot adapter if configured.
            if settings["slot" + str(slot_number)]:
                index = self._widget_slots[slot_number].findText(settings["slot" + str(slot_number)])
                if (index != -1):
                    self._widget_slots[slot_number].setCurrentIndex(index)

        # clear all the WIC combo boxes.
        for widget in self._widget_wics.values():
            widget.setEnabled(False)
            widget.clear()

        # load the available WICs to the correct slot for the corresponding platform
        if platform in WIC_MATRIX:
            for wic_number, wics in WIC_MATRIX[platform].items():
                self._widget_wics[wic_number].setEnabled(True)
                wic_list = list(wics)
                self._widget_wics[wic_number].addItems([""] + wic_list)

                # set the combox box to the correct WIC if configured.
                if settings["wic" + str(wic_number)]:
                    index = self._widget_wics[wic_number].findText(settings["wic" + str(wic_number)])
                    if (index != -1):
                        self._widget_wics[wic_number].setCurrentIndex(index)

    def loadSettings(self, settings, node, group=False):
        """
        Loads the router settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
            self.uiConsolePortSpinBox.setValue(settings["console"])
            self.uiAuxPortSpinBox.setValue(settings["aux"])

            # load the startup-config
            self.uiStartupConfigLineEdit.setText(settings["startup_config"])

            # load the private-config
            self.uiPrivateConfigLineEdit.setText(settings["private_config"])

            # load the MAC address setting
            self.uiBaseMACLineEdit.setInputMask("HHHH.HHHH.HHHH;_")

#             regexp = QtCore.QRegExp("([0-9a-fA-F]{4}\.){2}[0-9a-fA-F]{4}")
#             validator = QtGui.QRegExpValidator(regexp)
#             self.uiBaseMACLineEdit.setValidator(validator)

            if settings["mac_addr"]:
                self.uiBaseMACLineEdit.setText(settings["mac_addr"])
            else:
                self.uiBaseMACLineEdit.clear()

            # load the available IOS images
            ios_images = Dynamips.instance().iosImages()
            for ios_image in ios_images.values():
                if ios_image["platform"] == settings["platform"] and \
                        (ios_image["server"] == "local" and node.server().isLocal() or ios_image["server"] == node.server().host):
                    self.uiIOSImageComboBox.addItem(ios_image["image"], ios_image["path"])

            index = self.uiIOSImageComboBox.findText(os.path.basename(settings["image"]))
            if index != -1:
                self.uiIOSImageComboBox.setCurrentIndex(index)
        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiIOSImageLabel.hide()
            self.uiIOSImageComboBox.hide()
            self.uiStartupConfigLabel.hide()
            self.uiStartupConfigLineEdit.hide()
            self.uiStartupConfigToolButton.hide()
            self.uiPrivateConfigLabel.hide()
            self.uiPrivateConfigLineEdit.hide()
            self.uiPrivateConfigToolButton.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiAuxPortLabel.hide()
            self.uiAuxPortSpinBox.hide()
            self.uiBaseMacLabel.hide()
            self.uiBaseMACLineEdit.hide()

        # show the platform and chassis if applicable
        platform = settings["platform"]
        self.uiPlatformTextLabel.setText(platform)
        chassis = ""
        if "chassis" in settings:
            chassis = settings["chassis"]
            self.uiChassisTextLabel.setText(chassis)
        else:
            self.uiChassisLabel.hide()
            self.uiChassisTextLabel.hide()

        if platform == "c7200":

            # load the midplane and NPE settings
            self.uiMidplaneComboBox.clear()
            self.uiMidplaneComboBox.addItems(["std", "vxr"])
            self.uiNPEComboBox.clear()
            self.uiNPEComboBox.addItems(["npe-100", "npe-150", "npe-175", "npe-200", "npe-225", "npe-300", "npe-400", "npe-g2"])

            if settings["midplane"]:
                index = self.uiMidplaneComboBox.findText(settings["midplane"])
                if index != -1:
                    self.uiMidplaneComboBox.setCurrentIndex(index)
            if settings["npe"]:
                index = self.uiNPEComboBox.findText(settings["npe"])
                if index != -1:
                    self.uiNPEComboBox.setCurrentIndex(index)

            # load the sensor settings
            self.uiSensor1SpinBox.setValue(settings["sensors"][0])
            self.uiSensor2SpinBox.setValue(settings["sensors"][1])
            self.uiSensor3SpinBox.setValue(settings["sensors"][2])
            self.uiSensor4SpinBox.setValue(settings["sensors"][3])

            if settings["power_supplies"][0] == 1:
                self.uiPowerSupply1ComboBox.setCurrentIndex(0)
            else:
                self.uiPowerSupply1ComboBox.setCurrentIndex(1)

            if settings["power_supplies"][1] == 1:
                self.uiPowerSupply2ComboBox.setCurrentIndex(0)
            else:
                self.uiPowerSupply2ComboBox.setCurrentIndex(1)

            # all platforms but c7200 have the iomem feature
            # let"s hide these widgets.
            self.uiIomemLabel.hide()
            self.uiIomemSpinBox.hide()
        else:
            # hide the specific c7200 widgets.
            self.uiMidplaneLabel.hide()
            self.uiMidplaneComboBox.hide()
            self.uiNPELabel.hide()
            self.uiNPEComboBox.hide()
            self.uiTabWidget.removeTab(4)  # environment tab

            # load the I/O memory setting
            self.uiIomemSpinBox.setValue(settings["iomem"])

        # load the memories and disks settings
        self.uiRamSpinBox.setValue(settings["ram"])
        self.uiNvramSpinBox.setValue(settings["nvram"])
        self.uiDisk0SpinBox.setValue(settings["disk0"])
        self.uiDisk1SpinBox.setValue(settings["disk1"])

        # load all the slots with configured adapters
        self._loadAdapterConfig(platform, chassis, settings)

        # load the system ID (processor board ID in IOS) setting
        self.uiSystemIdLineEdit.setText(settings["system_id"])

        # load the configuration register setting
        self.uiConfregLineEdit.setText(settings["confreg"])

        # load the exec area setting
        self.uiExecAreaSpinBox.setValue(settings["exec_area"])

        # load the idle-pc setting
        self.uiIdlepcLineEdit.setText(settings["idlepc"])

        # load the idlemax setting
        self.uiIdlemaxSpinBox.setValue(settings["idlemax"])

        # load the idlesleep setting
        self.uiIdlesleepSpinBox.setValue(settings["idlesleep"])

        # load the mmap setting
        self.uiMmapCheckBox.setChecked(settings["mmap"])

        # load the sparsemem setting
        self.uiSparseMemoryCheckBox.setChecked(settings["sparsemem"])

    def _checkForLinkConnectedToAdapter(self, slot_number, settings, node):
        """
        Checks if links are connected to an adapter.

        :param slot_number: adapter slot number
        :param settings: IOS router settings
        :param node: Node instance
        """

        node_ports = node.ports()
        for node_port in node_ports:
            # ports > 15 are WICs ones.
            if node_port.slotNumber() == slot_number and node_port.portNumber() <= 15 and not node_port.isFree():
                adapter = settings["slot" + str(slot_number)]
                index = self._widget_slots[slot_number].findText(adapter)
                if (index != -1):
                    self._widget_slots[slot_number].setCurrentIndex(index)
                QtGui.QMessageBox.critical(self, node.name(), "A link is connected to port {} on adapter {}, please remove it first".format(node_port.name(),
                                                                                                                                              adapter))
                raise ConfigurationError()

    def _checkForLinkConnectedToWIC(self, wic_number, settings, node):
        """
        Checks if links are connected to a WIC.

        :param wic_number: WIC slot number
        :param settings: IOS router settings
        :param node: Node instance
        """

        node_ports = node.ports()
        for node_port in node_ports:
            # ports > 15 are WICs ones.
            if node_port.slotNumber() == wic_number and node_port.portNumber() > 15 and not node_port.isFree():
                wic = settings["wic" + str(wic_number)]
                index = self._widget_wics[wic_number].findText(wic)
                if (index != -1):
                    self._widget_wics[wic_number].setCurrentIndex(index)
                QtGui.QMessageBox.critical(self, node.name(), "A link is connected to port {} on {}, please remove it first".format(node_port.name(),
                                                                                                                                    wic))
                raise ConfigurationError()

    def saveSettings(self, settings, node, group=False):
        """
        Saves the router settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        #print("saving {}".format(group))

        # these settings cannot be shared by nodes and updated
        # in the node configurator.

        if not group:
            settings["name"] = self.uiNameLineEdit.text()
            settings["console"] = self.uiConsolePortSpinBox.value()
            settings["aux"] = self.uiAuxPortSpinBox.value()

            startup_config = self.uiStartupConfigLineEdit.text()
            if startup_config != settings["startup_config"]:
                if os.access(startup_config, os.R_OK):
                    settings["startup_config"] = startup_config
                else:
                    QtGui.QMessageBox.critical(self, "Startup-config", "Cannot read the startup-config file")

            private_config = self.uiPrivateConfigLineEdit.text()
            if private_config != settings["private_config"]:
                if os.access(private_config, os.R_OK):
                    settings["private_config"] = private_config
                else:
                    QtGui.QMessageBox.critical(self, "Private-config", "Cannot read the private-config file")

            # check and save the base MAC address
            mac = self.uiBaseMACLineEdit.text()
            if mac and not re.search(r"""^([0-9a-fA-F]{4}\.){2}[0-9a-fA-F]{4}$""", mac):
                QtGui.QMessageBox.critical(self, "MAC address", "Invalid MAC address (format required: hhhh.hhhh.hhhh)")
            elif mac != "":
                settings["mac_addr"] = mac

            # save the IOS image path
            index = self.uiIOSImageComboBox.currentIndex()
            ios_path = self.uiIOSImageComboBox.itemData(index)
            settings["image"] = ios_path
        else:
            del settings["name"]
            del settings["console"]
            del settings["aux"]
            del settings["mac_addr"]
            del settings["startup_config"]
            del settings["private_config"]
            del settings["image"]

        # get the platform and chassis if applicable
        platform = settings["platform"]
        if "chassis" in settings:
            settings["chassis"] = self.uiChassisTextLabel.text()

        if platform == "c7200":
            # save the midplane and NPE settings
            settings["midplane"] = self.uiMidplaneComboBox.currentText()
            settings["npe"] = self.uiNPEComboBox.currentText()

            sensors = []
            sensors.append(self.uiSensor1SpinBox.value())
            sensors.append(self.uiSensor2SpinBox.value())
            sensors.append(self.uiSensor3SpinBox.value())
            sensors.append(self.uiSensor4SpinBox.value())
            settings["sensors"] = sensors

            power_supplies = []
            if self.uiPowerSupply1ComboBox.currentIndex() == 0:
                power_supplies.append(1)
            else:
                power_supplies.append(0)

            if self.uiPowerSupply2ComboBox.currentIndex() == 0:
                power_supplies.append(1)
            else:
                power_supplies.append(0)
            settings["power_supplies"] = power_supplies
        else:
            # save the I/O memory setting
            settings["iomem"] = self.uiIomemSpinBox.value()

        # save the memories and disks settings
        settings["ram"] = self.uiRamSpinBox.value()
        settings["nvram"] = self.uiNvramSpinBox.value()
        settings["disk0"] = self.uiDisk0SpinBox.value()
        settings["disk1"] = self.uiDisk1SpinBox.value()

        # save the system ID (processor board ID in IOS) setting
        settings["system_id"] = self.uiSystemIdLineEdit.text()

        # save the configuration register setting
        # TODO: check the format? 0xnnnn
        settings["confreg"] = self.uiConfregLineEdit.text()

        # save the exec area setting
        settings["exec_area"] = self.uiExecAreaSpinBox.value()

        # save the idle-pc setting
        # TODO: check the format?
        settings["idlepc"] = self.uiIdlepcLineEdit.text()

        # save the idlemax setting
        settings["idlemax"] = self.uiIdlemaxSpinBox.value()

        # save the idlesleep setting
        settings["idlesleep"] = self.uiIdlesleepSpinBox.value()

        # save the mmap setting
        settings["mmap"] = self.uiMmapCheckBox.isChecked()

        # load the sparsemem setting
        settings["sparsemem"] = self.uiSparseMemoryCheckBox.isChecked()

        # save the adapters and WICs configuration and
        # check if a module port is connected before removing or replacing.
        for slot_number, widget in self._widget_slots.items():
            module = widget.currentText()
            if module:
                if settings["slot" + str(slot_number)] and settings["slot" + str(slot_number)] != module:
                    self._checkForLinkConnectedToAdapter(slot_number, settings, node)
                settings["slot" + str(slot_number)] = module
            elif settings["slot" + str(slot_number)]:
                self._checkForLinkConnectedToAdapter(slot_number, settings, node)
                settings["slot" + str(slot_number)] = None

        for wic_number, widget in self._widget_wics.items():
            wic_name = str(widget.currentText())
            if wic_name:
                if settings["wic" + str(wic_number)] and settings["wic" + str(wic_number)] != wic_name:
                    self._checkForLinkConnectedToWIC(wic_number, settings, node)
                settings["wic" + str(wic_number)] = wic_name
            elif settings["wic" + str(wic_number)]:
                self._checkForLinkConnectedToWIC(wic_number, settings, node)
                settings["wic" + str(wic_number)] = None
