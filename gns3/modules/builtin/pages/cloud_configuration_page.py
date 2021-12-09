# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 GNS3 Technologies Inc.
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
Configuration page for clouds.
"""

from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.dialogs.symbol_selection_dialog import SymbolSelectionDialog
from ....dialogs.node_properties_dialog import ConfigurationError
from gns3.controller import Controller
from gns3.node import Node

from ..ui.cloud_configuration_page_ui import Ui_cloudConfigPageWidget


class CloudConfigurationPage(QtWidgets.QWidget, Ui_cloudConfigPageWidget):

    """
    QWidget configuration page for clouds.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self._node = None
        self._ports = []
        self._interfaces = []

        # add the categories
        for name, category in Node.defaultCategories().items():
            self.uiCategoryComboBox.addItem(name, category)

        # connect Ethernet slots
        self.uiEthernetListWidget.itemSelectionChanged.connect(self._EthernetChangedSlot)
        self.uiEthernetWarningPushButton.clicked.connect(self._EthernetWarningSlot)
        self.uiAddEthernetPushButton.clicked.connect(self._EthernetAddSlot)
        self.uiAddAllEthernetPushButton.clicked.connect(self._EthernetAddAllSlot)
        self.uiRefreshEthernetPushButton.clicked.connect(self._EthernetRefreshSlot)
        self.uiDeleteEthernetPushButton.clicked.connect(self._EthernetDeleteSlot)

        # connect TAP slots
        self.uiTAPComboBox.currentIndexChanged.connect(self._TAPSelectedSlot)
        self.uiTAPListWidget.itemSelectionChanged.connect(self._TAPChangedSlot)
        self.uiAddTAPPushButton.clicked.connect(self._TAPAddSlot)
        self.uiAddAllTAPPushButton.clicked.connect(self._TAPAddAllSlot)
        self.uiRefreshTAPPushButton.clicked.connect(self._TAPRefreshSlot)
        self.uiDeleteTAPPushButton.clicked.connect(self._TAPDeleteSlot)

        # connect UDP slots
        self.uiUDPTreeWidget.itemActivated.connect(self._UDPSelectedSlot)
        self.uiUDPTreeWidget.itemSelectionChanged.connect(self._UDPChangedSlot)
        self.uiAddUDPPushButton.clicked.connect(self._UDPAddSlot)
        self.uiDeleteUDPPushButton.clicked.connect(self._UDPDeleteSlot)

        # connect other slots
        self.uiShowSpecialInterfacesCheckBox.stateChanged.connect(self._showSpecialInterfacesSlot)
        self.uiSymbolToolButton.clicked.connect(self._symbolBrowserSlot)
        self.uiConsoleTypeComboBox.currentTextChanged.connect(self._consoleTypeChangedSlot)

        # add an icon to the warning button
        icon = QtGui.QIcon.fromTheme("dialog-warning")
        if icon.isNull():
            icon = QtGui.QIcon(':/icons/dialog-warning.svg')
        self.uiEthernetWarningPushButton.setIcon(icon)

    def _refreshInterfaces(self):
        """
        Refresh the network interfaces.
        """

        if self._node:
            self._interfaces = self._node.interfaces()
            self._loadNetworkInterfaces(self._interfaces)
            try:
                self._node.updated_signal.disconnect(self._refreshInterfaces)
            except (TypeError, RuntimeError):
                pass  # was not connected

    def _EthernetChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiEthernetListWidget.currentItem()
        if item:
            self.uiDeleteEthernetPushButton.setEnabled(True)
        else:
            self.uiDeleteEthernetPushButton.setEnabled(False)

    def _EthernetWarningSlot(self):
        """
        Shows a warning about Wifi Ethernet interfaces.
        """

        QtWidgets.QMessageBox.warning(self, "Ethernet interfaces", "Wifi interfaces may not work properly. It is recommended to use wired Ethernet or Loopback interfaces only.")

    def _EthernetAddSlot(self, interface=None):
        """
        Adds a new Ethernet interface.
        """

        if not interface:
            interface = self.uiEthernetComboBox.currentText()
        if interface:
            for port in self._ports:
                if port["name"] == interface and port["type"] == "ethernet":
                    return
            self.uiEthernetListWidget.addItem(interface)
            self._ports.append({"name": interface,
                                "port_number": len(self._ports),
                                "type": "ethernet",
                                "interface": interface})
            index = self.uiEthernetComboBox.findText(interface)
            if index != -1:
                self.uiEthernetComboBox.removeItem(index)

    def _EthernetAddAllSlot(self):
        """
        Adds all Ethernet interfaces.
        """

        for index in range(0, self.uiEthernetComboBox.count()):
            interface = self.uiEthernetComboBox.itemText(index)
            self._EthernetAddSlot(interface)

    def _EthernetRefreshSlot(self):
        """
        Refresh all Ethernet interfaces.
        """

        if self._node:
            self._node.update({}, force=True)
            self._node.updated_signal.connect(self._refreshInterfaces)

    def _EthernetDeleteSlot(self):
        """
        Deletes the selected Ethernet interface.
        """

        if self._node:
            for item in self.uiEthernetListWidget.selectedItems():
                interface = item.text()
                # check we can delete that interface
                for node_port in self._node.ports():
                    if node_port.name() == interface and not node_port.isFree():
                        QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to {}, please remove it first".format(interface))
                        return

        for item in self.uiEthernetListWidget.selectedItems():
            interface = item.text()
            for port in self._ports.copy():
                if port["name"] == interface:
                    self._ports.remove(port)
                    self.uiEthernetListWidget.takeItem(self.uiEthernetListWidget.row(item))
                    for interface in self._interfaces:
                        if not self.uiShowSpecialInterfacesCheckBox.isChecked() and interface["special"]:
                            continue
                        if interface["name"] == port["name"] and interface["type"] == "ethernet":
                            self.uiEthernetComboBox.addItem(interface["name"])
                            break
                    break

    def _TAPSelectedSlot(self, index):
        """
        Loads the selected TAP interface.

        :param index: ignored
        """

        self.uiTAPLineEdit.setText(self.uiTAPComboBox.currentText())

    def _TAPChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiTAPListWidget.currentItem()
        if item:
            self.uiDeleteTAPPushButton.setEnabled(True)
            self.uiTAPLineEdit.setText(item.text())
        else:
            self.uiDeleteTAPPushButton.setEnabled(False)

    def _TAPAddSlot(self, interface=None):
        """
        Adds a new TAP interface.
        """

        if not interface:
            interface = self.uiTAPLineEdit.text()
        if interface:
            for port in self._ports:
                if port["name"] == interface and port["type"] == "tap":
                    return
            self.uiTAPListWidget.addItem(interface)
            self._ports.append({"name": interface,
                                "port_number": len(self._ports),
                                "type": "tap",
                                "interface": interface})
            index = self.uiTAPComboBox.findText(interface)
            if index != -1:
                self.uiTAPComboBox.removeItem(index)

    def _TAPAddAllSlot(self):
        """
        Adds all TAP interfaces
        """

        for index in range(0, self.uiTAPComboBox.count()):
            interface = self.uiTAPComboBox.itemText(index)
            self._TAPAddSlot(interface)

    def _TAPRefreshSlot(self):
        """
        Refresh all TAP interfaces.
        """

        if self._node:
            self._node.update({}, force=True)
            self._node.updated_signal.connect(self._refreshInterfaces)

    def _TAPDeleteSlot(self):
        """
        Deletes a TAP interface.
        """

        if self._node:
            for item in self.uiTAPListWidget.selectedItems():
                interface = item.text()
                # check we can delete that interface
                for node_port in self._node.ports():
                    if node_port.name() == interface and not node_port.isFree():
                        QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to {}, please remove it first".format(interface))
                        return

        for item in self.uiTAPListWidget.selectedItems():
            interface = item.text()
            for port in self._ports.copy():
                if port["name"] == interface:
                    self._ports.remove(port)
                    self.uiTAPListWidget.takeItem(self.uiTAPListWidget.row(item))
                    for interface in self._interfaces:
                        if interface["name"] == port["name"] and interface["type"] == "tap":
                            self.uiTAPComboBox.addItem(interface["name"])
                    break

    def _UDPSelectedSlot(self, item, column):
        """
        Loads a selected UDP tunnel.

        :param item: selected TreeWidgetItem instance
        :param column: ignored
        """

        name = item.text(0)
        local_port = int(item.text(1))
        remote_host = item.text(2)
        remote_port = int(item.text(3))
        self.uiUDPNameLineEdit.setText(name)
        self.uiLocalPortSpinBox.setValue(local_port)
        self.uiRemoteHostLineEdit.setText(remote_host)
        self.uiRemotePortSpinBox.setValue(remote_port)

    def _UDPChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiUDPTreeWidget.currentItem()
        if item:
            self.uiDeleteUDPPushButton.setEnabled(True)
        else:
            self.uiDeleteUDPPushButton.setEnabled(False)

    def _UDPAddSlot(self):
        """
        Adds a new UDP tunnel
        """

        name = self.uiUDPNameLineEdit.text()
        local_port = self.uiLocalPortSpinBox.value()
        remote_host = self.uiRemoteHostLineEdit.text()
        remote_port = self.uiRemotePortSpinBox.value()
        if name and remote_host:
            for port in self._ports:
                if port["name"] == name:
                    return

            # add a new entry in the tree widget
            item = QtWidgets.QTreeWidgetItem(self.uiUDPTreeWidget)
            item.setText(0, name)
            item.setText(1, str(local_port))
            item.setText(2, remote_host)
            item.setText(3, str(remote_port))
            self.uiUDPTreeWidget.addTopLevelItem(item)
            self._ports.append({"name": name,
                                "port_number": len(self._ports),
                                "type": "udp",
                                "lport": local_port,
                                "rhost": remote_host,
                                "rport": remote_port})
            self.uiLocalPortSpinBox.setValue(local_port + 1)
            self.uiRemotePortSpinBox.setValue(remote_port + 1)
            self.uiUDPTreeWidget.resizeColumnToContents(0)
            self.uiUDPTreeWidget.resizeColumnToContents(1)
            self.uiUDPTreeWidget.resizeColumnToContents(2)
            self.uiUDPTreeWidget.resizeColumnToContents(3)
            nb_tunnels = 0
            for port in self._ports:
                if port["type"] == "udp":
                    nb_tunnels += 1
            self.uiUDPNameLineEdit.setText("UDP tunnel {}".format(nb_tunnels + 1))

    def _UDPDeleteSlot(self):
        """
        Deletes an UDP tunnel.
        """

        if self._node:
            for item in self.uiUDPTreeWidget.selectedItems():
                name = item.text(0)
                # check we can delete that UDP tunnel
                for node_port in self._node.ports():
                    if node_port.name() == name and not node_port.isFree():
                        QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to {}, please remove it first".format(name))
                        return

        for item in self.uiUDPTreeWidget.selectedItems():
            name = item.text(0)
            for port in self._ports.copy():
                if port["name"] == name:
                    self._ports.remove(port)
            self.uiUDPTreeWidget.takeTopLevelItem(self.uiUDPTreeWidget.indexOfTopLevelItem(item))
            nb_tunnels = 0
            for port in self._ports:
                if port["type"] == "udp":
                    nb_tunnels += 1
            self.uiUDPNameLineEdit.setText("UDP tunnel {}".format(nb_tunnels + 1))

    def _showSpecialInterfacesSlot(self, state):
        """
        Shows special Ethernet interfaces.
        """

        self.uiEthernetComboBox.clear()
        index = 0
        for interface in self._interfaces:
            if interface["type"] == "ethernet":
                if not state and interface["special"]:
                    continue
                if self.uiEthernetListWidget.findItems(interface["name"], QtCore.Qt.MatchFixedString):
                    continue
                self.uiEthernetComboBox.addItem(interface["name"])
                index += 1

    def _symbolBrowserSlot(self):
        """
        Slot to open the symbol browser and select a new symbol.
        """

        symbol_path = self.uiSymbolLineEdit.text()
        dialog = SymbolSelectionDialog(self, symbol=symbol_path)
        dialog.show()
        if dialog.exec_():
            new_symbol_path = dialog.getSymbol()
            self.uiSymbolLineEdit.setText(new_symbol_path)
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(new_symbol_path))

    def _loadNetworkInterfaces(self, interfaces):
        """
        Loads Ethernet and TAP interfaces.
        """

        self.uiEthernetComboBox.clear()
        index = 0
        for interface in interfaces:
            if interface["type"] == "ethernet" and not interface["special"]:
                self.uiEthernetComboBox.addItem(interface["name"])
                index += 1

        # load all TAP interfaces
        self.uiTAPComboBox.clear()
        index = 0
        for interface in interfaces:
            if interface["type"] == "tap":
                self.uiTAPComboBox.addItem(interface["name"])
                index += 1

    def _getInterfacesFromServerCallback(self, result, error=False, **kwargs):
        """
        Callback for retrieving the network interfaces

        :param progress_dialog: QProgressDialog instance
        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Network interfaces", "{}".format(result["message"]))
        else:
            self._interfaces = result
            self._loadNetworkInterfaces(result)

    def _consoleTypeChangedSlot(self, console_type):
        """
        Slot called when the console type has been changed.

        :param console_type: console type
        """

        if console_type in ("http", "https"):
            self.uiConsoleHttpPathLineEdit.setEnabled(True)
        else:
            self.uiConsoleHttpPathLineEdit.setEnabled(False)

        if console_type != "none":
            self.uiConsoleHostLineEdit.setEnabled(True)
            self.uiConsolePortSpinBox.setEnabled(True)
        else:
            self.uiConsoleHostLineEdit.setEnabled(False)
            self.uiConsolePortSpinBox.setEnabled(False)

    def loadSettings(self, settings, node=None, group=False):
        """
        Loads the cloud settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
            self.uiConsoleHostLineEdit.setText(settings["remote_console_host"])
            self.uiConsolePortSpinBox.setValue(settings["remote_console_port"])
            index = self.uiConsoleTypeComboBox.findText(settings["remote_console_type"])
            if index != -1:
                self.uiConsoleTypeComboBox.setCurrentIndex(index)
            self.uiConsoleHttpPathLineEdit.setText(settings["remote_console_http_path"])
        else:
            self.uiNameLineEdit.setEnabled(False)

        if not node:
            # these are template settings

            self.uiNameLabel.setText("Template name:")

            # load the default name format
            self.uiDefaultNameFormatLineEdit.setText(settings["default_name_format"])

            # load the symbol
            self.uiSymbolLineEdit.setText(settings["symbol"])
            self.uiSymbolLineEdit.setToolTip('<img src="{}"/>'.format(settings["symbol"]))

            # load the category
            index = self.uiCategoryComboBox.findData(settings["category"])
            if index != -1:
                self.uiCategoryComboBox.setCurrentIndex(index)

            Controller.instance().getCompute(
                "/network/interfaces",
                settings["compute_id"],
                self._getInterfacesFromServerCallback,
                progress_text="Retrieving network interfaces...",
                wait=True
            )

        else:
            self.uiDefaultNameFormatLabel.hide()
            self.uiDefaultNameFormatLineEdit.hide()
            self.uiSymbolLabel.hide()
            self.uiSymbolLineEdit.hide()
            self.uiSymbolToolButton.hide()
            self.uiCategoryComboBox.hide()
            self.uiCategoryLabel.hide()
            self.uiCategoryComboBox.hide()
            self._node = node
            self._interfaces = self._node.interfaces()
            self._loadNetworkInterfaces(self._interfaces)

        self.uiUsageTextEdit.setPlainText(settings["usage"])
        # load the current ports
        self._ports = []
        self.uiEthernetListWidget.clear()
        self.uiTAPListWidget.clear()
        self.uiUDPTreeWidget.clear()

        for port in settings["ports_mapping"]:
            self._ports.append(port)
            if port["type"] == "ethernet":
                self.uiEthernetListWidget.addItem(port["name"])
                index = self.uiEthernetComboBox.findText(port["name"])
                if index != -1:
                    self.uiEthernetComboBox.removeItem(index)
            elif port["type"] == "tap":
                self.uiTAPListWidget.addItem(port["name"])
                index = self.uiTAPComboBox.findText(port["name"])
                if index != -1:
                    self.uiTAPComboBox.removeItem(index)
            elif port["type"] == "udp":
                item = QtWidgets.QTreeWidgetItem(self.uiUDPTreeWidget)
                item.setText(0, port["name"])
                item.setText(1, str(port["lport"]))
                item.setText(2, port["rhost"])
                item.setText(3, str(port["rport"]))
                self.uiUDPTreeWidget.addTopLevelItem(item)
                self.uiUDPTreeWidget.resizeColumnToContents(0)
                self.uiUDPTreeWidget.resizeColumnToContents(1)
                self.uiUDPTreeWidget.resizeColumnToContents(2)
                self.uiUDPTreeWidget.resizeColumnToContents(3)

    def saveSettings(self, settings, node=None, group=False):
        """
        Saves the cloud settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            settings["name"] = self.uiNameLineEdit.text()
            console_host = self.uiConsoleHostLineEdit.text().strip()

            if self.uiConsoleTypeComboBox.currentText().lower() != "none":
                if not console_host:
                    QtWidgets.QMessageBox.critical(self, "Console host", "Console host cannot be blank if console type is not set to none")
                    raise ConfigurationError()

            settings["remote_console_host"] = console_host
            settings["remote_console_port"] = self.uiConsolePortSpinBox.value()
            settings["remote_console_type"] = self.uiConsoleTypeComboBox.currentText().lower()
            settings["remote_console_http_path"] = self.uiConsoleHttpPathLineEdit.text().strip()

        if not node:
            # these are template settings

            # save the default name format
            default_name_format = self.uiDefaultNameFormatLineEdit.text().strip()
            if '{0}' not in default_name_format and '{id}' not in default_name_format:
                QtWidgets.QMessageBox.critical(self, "Default name format", "The default name format must contain at least {0} or {id}")
            else:
                settings["default_name_format"] = default_name_format

            symbol_path = self.uiSymbolLineEdit.text()
            settings["symbol"] = symbol_path

            settings["category"] = self.uiCategoryComboBox.itemData(self.uiCategoryComboBox.currentIndex())
            settings["ports_mapping"] = self._ports
        else:
            settings["ports_mapping"] = self._ports

        settings["usage"] = self.uiUsageTextEdit.toPlainText()
        return settings
