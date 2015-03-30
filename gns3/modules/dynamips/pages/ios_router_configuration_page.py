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

from gns3.qt import QtCore, QtGui
from gns3.dialogs.node_configurator_dialog import ConfigurationError
from ..ui.ios_router_configuration_page_ui import Ui_iosRouterConfigPageWidget
from ..settings import CHASSIS, ADAPTER_MATRIX, WIC_MATRIX


class IOSRouterConfigurationPage(QtGui.QWidget, Ui_iosRouterConfigPageWidget):

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
        self.uiIOSImageToolButton.clicked.connect(self._iosImageBrowserSlot)

        self._idle_valid = False
        idle_pc_rgx = QtCore.QRegExp("^(0x[0-9a-fA-F]{8})?$")
        validator = QtGui.QRegExpValidator(idle_pc_rgx, self)
        self.uiIdlepcLineEdit.setValidator(validator)
        self.uiIdlepcLineEdit.textChanged.connect(self._idlePCValidateSlot)
        self.uiIdlepcLineEdit.textChanged.emit(self.uiIdlepcLineEdit.text())

    def _idlePCValidateSlot(self):
        """
        Slot to validate the entered Idle-PC Value
        """

        validator = self.uiIdlepcLineEdit.validator()
        state = validator.validate(self.uiIdlepcLineEdit.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#A2C964'  # green
            self._idle_valid = True
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a'  # yellow
            self._idle_valid = False
        else:
            color = '#f6989d'  # red
            self._idle_valid = False
        self.uiIdlepcLineEdit.setStyleSheet('QLineEdit { background-color: %s }' % color)

    def _iosImageBrowserSlot(self):
        """
        Slot to open a file browser and select an IOU image.
        """

        from ..pages.ios_router_preferences_page import IOSRouterPreferencesPage
        path = IOSRouterPreferencesPage.getIOSImage(self)
        if not path:
            return
        self.uiIOSImageLineEdit.clear()
        self.uiIOSImageLineEdit.setText(path)

        # try to guess the platform
        image = os.path.basename(path)
        match = re.match("^(c[0-9]+)\\-\w+", image)
        if not match:
            QtGui.QMessageBox.warning(self, "IOS image", "Could not detect the platform, make sure this is a valid IOS image!")
            return

        detected_platform = match.group(1)
        detected_chassis = ""
        # IOS images for the 3600 platform start with the chassis name (c3620 etc.)
        for platform, chassis in CHASSIS.items():
            if detected_platform[1:] in chassis:
                detected_chassis = detected_platform[1:]
                detected_platform = platform
                break

        platform = self.uiPlatformTextLabel.text()
        chassis = self.uiChassisTextLabel.text()

        if detected_platform != platform:
            QtGui.QMessageBox.warning(self, "IOS image", "Using an IOS image made for another platform will likely not work!")

        if detected_chassis and chassis and detected_chassis != chassis:
            QtGui.QMessageBox.warning(self, "IOS image", "Using an IOS image made for another chassis will likely not work!")

    def _startupConfigBrowserSlot(self):
        """
        Slot to open a file browser and select a startup-config file.
        """

        config_dir = os.path.join(os.path.dirname(QtCore.QSettings().fileName()), "base_configs")
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

        config_dir = os.path.join(os.path.dirname(QtCore.QSettings().fileName()), "base_configs")
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

            if isinstance(slot_adapters, str):
                # only one default adapter for this slot.
                self._widget_slots[slot_number].addItem(slot_adapters)
            else:
                # list of adapters
                module_list = list(slot_adapters)
                if platform == "c7200" and slot_number == 0:
                    # special case
                    self._widget_slots[slot_number].addItems(module_list)
                else:
                    self._widget_slots[slot_number].addItems([""] + module_list)

            # set the combox box to the correct slot adapter if configured.
            if settings["slot" + str(slot_number)]:
                index = self._widget_slots[slot_number].findText(settings["slot" + str(slot_number)])
                if index != -1:
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
                    if index != -1:
                        self._widget_wics[wic_number].setCurrentIndex(index)

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the router settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])

            if "console" in settings:
                self.uiConsolePortSpinBox.setValue(settings["console"])
            else:
                self.uiConsolePortLabel.hide()
                self.uiConsolePortSpinBox.hide()

            if "aux" in settings:
                if settings["aux"] is None:
                    self.uiAuxPortSpinBox.setValue(0)
                else:
                    self.uiAuxPortSpinBox.setValue(settings["aux"])
            else:
                self.uiAuxPortLabel.hide()
                self.uiAuxPortSpinBox.hide()

            # load the MAC address setting
            self.uiBaseMACLineEdit.setInputMask("HHHH.HHHH.HHHH;_")

#             regexp = QtCore.QRegExp("([0-9a-fA-F]{4}\.){2}[0-9a-fA-F]{4}")
#             validator = QtGui.QRegExpValidator(regexp)
#             self.uiBaseMACLineEdit.setValidator(validator)

            if settings["mac_addr"]:
                self.uiBaseMACLineEdit.setText(settings["mac_addr"])
            else:
                self.uiBaseMACLineEdit.clear()

            self.uiIOSImageLineEdit.setText(settings["image"])
        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiIOSImageLabel.hide()
            self.uiIOSImageLineEdit.hide()
            self.uiIOSImageToolButton.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiAuxPortLabel.hide()
            self.uiAuxPortSpinBox.hide()
            self.uiBaseMacLabel.hide()
            self.uiBaseMACLineEdit.hide()

        if not node:
            # load the startup-config
            self.uiStartupConfigLineEdit.setText(settings["startup_config"])
            # load the private-config
            self.uiPrivateConfigLineEdit.setText(settings["private_config"])
        else:
            self.uiStartupConfigLabel.hide()
            self.uiStartupConfigLineEdit.hide()
            self.uiStartupConfigToolButton.hide()
            self.uiPrivateConfigLabel.hide()
            self.uiPrivateConfigLineEdit.hide()
            self.uiPrivateConfigToolButton.hide()

        # show the platform and chassis if applicable
        platform = settings["platform"]
        self.uiPlatformTextLabel.setText(platform)
        chassis = ""
        if "chassis" in settings and settings["chassis"]:
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

            if "sensors" in settings:
                # load the sensor settings
                self.uiSensor1SpinBox.setValue(settings["sensors"][0])
                self.uiSensor2SpinBox.setValue(settings["sensors"][1])
                self.uiSensor3SpinBox.setValue(settings["sensors"][2])
                self.uiSensor4SpinBox.setValue(settings["sensors"][3])

            if "power_supplies" in settings:
                if settings["power_supplies"][0] == 1:
                    self.uiPowerSupply1ComboBox.setCurrentIndex(0)
                else:
                    self.uiPowerSupply1ComboBox.setCurrentIndex(1)

                if settings["power_supplies"][1] == 1:
                    self.uiPowerSupply2ComboBox.setCurrentIndex(0)
                else:
                    self.uiPowerSupply2ComboBox.setCurrentIndex(1)
            else:
                self.uiTabWidget.removeTab(4)  # environment tab

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

        if "exec_area" in settings:
            # load the exec area setting
            self.uiExecAreaSpinBox.setValue(settings["exec_area"])
        else:
            self.uiExecAreaLabel.hide()
            self.uiExecAreaSpinBox.hide()

        # load the Idle-PC setting
        self.uiIdlepcLineEdit.setText(settings["idlepc"])

        if "idlemax" in settings:
            # load the idlemax setting
            self.uiIdlemaxSpinBox.setValue(settings["idlemax"])
        else:
            self.uiIdlemaxLabel.hide()
            self.uiIdlemaxSpinBox.hide()

        if "idlesleep" in settings:
            # load the idlesleep setting
            self.uiIdlesleepSpinBox.setValue(settings["idlesleep"])
        else:
            self.uiIdlesleepLabel.hide()
            self.uiIdlesleepSpinBox.hide()

        # load the mmap setting
        if "mmap" in settings:
            self.uiMmapCheckBox.setChecked(settings["mmap"])
        else:
            self.uiMmapCheckBox.hide()

        if "sparsemem" in settings:
            # load the sparsemem setting
            self.uiSparseMemoryCheckBox.setChecked(settings["sparsemem"])
        else:
            self.uiSparseMemoryCheckBox.hide()

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
            if node_port.adapterNumber() == slot_number and node_port.portNumber() <= 15 and not node_port.isFree():
                adapter = settings["slot" + str(slot_number)]
                index = self._widget_slots[slot_number].findText(adapter)
                if index != -1:
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
            if node_port.adapterNumber() == wic_number and node_port.portNumber() > 15 and not node_port.isFree():
                wic = settings["wic" + str(wic_number)]
                index = self._widget_wics[wic_number].findText(wic)
                if index != -1:
                    self._widget_wics[wic_number].setCurrentIndex(index)
                QtGui.QMessageBox.critical(self, node.name(), "A link is connected to port {} on {}, please remove it first".format(node_port.name(),
                                                                                                                                    wic))
                raise ConfigurationError()

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the router settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of routers
        """

        if not group:

            # Check if the Idle-PC value has been validated okay
            if not self._idle_valid:
                idle_pc = self.uiIdlepcLineEdit.text()
                QtGui.QMessageBox.critical(self, "Idle-PC", "{} is not a valid Idle-PC value ".format(idle_pc))
                raise ConfigurationError()

            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtGui.QMessageBox.critical(self, "Name", "IOS router name cannot be empty!")
            elif node and not node.validateHostname(name):
                QtGui.QMessageBox.critical(self, "Name", "Invalid name detected for IOS router: {}".format(name))
            else:
                settings["name"] = name

            settings["console"] = self.uiConsolePortSpinBox.value()
            aux = self.uiAuxPortSpinBox.value()
            if aux:
                settings["aux"] = aux

            # check and save the base MAC address
            # mac = self.uiBaseMACLineEdit.text()
            # if mac and not re.search(r"""^([0-9a-fA-F]{4}\.){2}[0-9a-fA-F]{4}$""", mac):
            #    QtGui.QMessageBox.critical(self, "MAC address", "Invalid MAC address (format required: hhhh.hhhh.hhhh)")
            # elif mac != "":
            #    settings["mac_addr"] = mac

            # save the IOS image path
            settings["image"] = self.uiIOSImageLineEdit.text()

        else:
            del settings["name"]
            del settings["console"]
            del settings["aux"]
            del settings["mac_addr"]
            del settings["startup_config"]
            del settings["private_config"]
            del settings["image"]

        if not node:
            startup_config = self.uiStartupConfigLineEdit.text().strip()
            if startup_config and startup_config != settings["startup_config"]:
                if os.access(startup_config, os.R_OK):
                    settings["startup_config"] = startup_config
                else:
                    QtGui.QMessageBox.critical(self, "Startup-config", "Cannot read the startup-config file")

            private_config = self.uiPrivateConfigLineEdit.text().strip()
            if private_config and private_config != settings["private_config"]:
                if os.access(private_config, os.R_OK):
                    settings["private_config"] = private_config
                else:
                    QtGui.QMessageBox.critical(self, "Private-config", "Cannot read the private-config file")

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

        # save the exec area setting
        settings["exec_area"] = self.uiExecAreaSpinBox.value()

        # save the Idle-PC setting
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
            if not widget.isEnabled():
                break
            module = widget.currentText()
            if module:
                if settings["slot" + str(slot_number)] and settings["slot" + str(slot_number)] != module:
                    if node:
                        self._checkForLinkConnectedToAdapter(slot_number, settings, node)
                settings["slot" + str(slot_number)] = module
            elif settings["slot" + str(slot_number)]:
                if node:
                    self._checkForLinkConnectedToAdapter(slot_number, settings, node)
                settings["slot" + str(slot_number)] = None

        for wic_number, widget in self._widget_wics.items():
            if not widget.isEnabled():
                break
            wic_name = str(widget.currentText())
            if wic_name:
                if settings["wic" + str(wic_number)] and settings["wic" + str(wic_number)] != wic_name:
                    if node:
                        self._checkForLinkConnectedToWIC(wic_number, settings, node)
                settings["wic" + str(wic_number)] = wic_name
            elif settings["wic" + str(wic_number)]:
                if node:
                    self._checkForLinkConnectedToWIC(wic_number, settings, node)
                settings["wic" + str(wic_number)] = None
