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
Configuration page for clouds.
"""

import re
from gns3.qt import QtCore, QtWidgets
from ..ui.cloud_configuration_page_ui import Ui_cloudConfigPageWidget


class CloudConfigurationPage(QtWidgets.QWidget, Ui_cloudConfigPageWidget):

    """
    QWidget configuration page for clouds.
    """

    def __init__(self):

        super().__init__()
        self.setupUi(self)
        self._nios = set()

        # connect NIO generic Ethernet slots
        self.uiGenericEthernetComboBox.currentIndexChanged.connect(self._genericEthernetSelectedSlot)
        self.uiGenericEthernetListWidget.itemSelectionChanged.connect(self._genericEthernetChangedSlot)
        self.uiAddGenericEthernetPushButton.clicked.connect(self._genericEthernetAddSlot)
        self.uiDeleteGenericEthernetPushButton.clicked.connect(self._genericEthernetDeleteSlot)

        # connect NIO Linux Ethernet slots
        self.uiLinuxEthernetComboBox.currentIndexChanged.connect(self._linuxEthernetSelectedSlot)
        self.uiLinuxEthernetListWidget.itemSelectionChanged.connect(self._linuxEthernetChangedSlot)
        self.uiAddLinuxEthernetPushButton.clicked.connect(self._linuxEthernetAddSlot)
        self.uiDeleteLinuxEthernetPushButton.clicked.connect(self._linuxEthernetDeleteSlot)

        # connect NIO NAT slots
        self.uiNIONATListWidget.currentRowChanged.connect(self._NIONATSelectedSlot)
        self.uiNIONATListWidget.itemSelectionChanged.connect(self._NIONATChangedSlot)
        self.uiAddNIONATPushButton.clicked.connect(self._NIONATAddSlot)
        self.uiDeleteNIONATPushButton.clicked.connect(self._NIONATDeleteSlot)

        # connect NIO UDP slots
        self.uiNIOUDPListWidget.currentRowChanged.connect(self._NIOUDPSelectedSlot)
        self.uiNIOUDPListWidget.itemSelectionChanged.connect(self._NIOUDPChangedSlot)
        self.uiAddNIOUDPPushButton.clicked.connect(self._NIOUDPAddSlot)
        self.uiDeleteNIOUDPPushButton.clicked.connect(self._NIOUDPDeleteSlot)

        # connect NIO TAP slots
        self.uiNIOTAPListWidget.currentRowChanged.connect(self._NIOTAPSelectedSlot)
        self.uiNIOTAPListWidget.itemSelectionChanged.connect(self._NIOTAPChangedSlot)
        self.uiAddNIOTAPPushButton.clicked.connect(self._NIOTAPAddSlot)
        self.uiDeleteNIOTAPPushButton.clicked.connect(self._NIOTAPDeleteSlot)

        # connect NIO UNIX slots
        self.uiNIOUNIXListWidget.currentRowChanged.connect(self._NIOUNIXSelectedSlot)
        self.uiNIOUNIXListWidget.itemSelectionChanged.connect(self._NIOUNIXChangedSlot)
        self.uiAddNIOUNIXPushButton.clicked.connect(self._NIOUNIXAddSlot)
        self.uiDeleteNIOUNIXPushButton.clicked.connect(self._NIOUNIXDeleteSlot)

        # connect NIO VDE slots
        self.uiNIOVDEListWidget.currentRowChanged.connect(self._NIOVDESelectedSlot)
        self.uiNIOVDEListWidget.itemSelectionChanged.connect(self._NIOVDEChangedSlot)
        self.uiAddNIOVDEPushButton.clicked.connect(self._NIOVDEAddSlot)
        self.uiDeleteNIOVDEPushButton.clicked.connect(self._NIOVDEDeleteSlot)

        # connect NIO NULL slots
        self.uiNIONullListWidget.currentRowChanged.connect(self._NIONullSelectedSlot)
        self.uiNIONullListWidget.itemSelectionChanged.connect(self._NIONullChangedSlot)
        self.uiAddNIONullPushButton.clicked.connect(self._NIONullAddSlot)
        self.uiDeleteNIONullPushButton.clicked.connect(self._NIONullDeleteSlot)

    def _genericEthernetSelectedSlot(self, index):
        """
        Loads the selected generic Ethernet interface in lineEdit.

        :param index: ignored
        """

        self.uiGenericEthernetLineEdit.setText(self.uiGenericEthernetComboBox.currentText())

    def _genericEthernetChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiGenericEthernetListWidget.currentItem()
        if item:
            self.uiDeleteGenericEthernetPushButton.setEnabled(True)
        else:
            self.uiDeleteGenericEthernetPushButton.setEnabled(False)

    def _genericEthernetAddSlot(self):
        """
        Adds a new generic Ethernet NIO.
        """

        interface = self.uiGenericEthernetLineEdit.text()
        if interface:
            nio = "nio_gen_eth:{interface}".format(interface=interface)
            if nio not in self._nios:
                self.uiGenericEthernetListWidget.addItem(nio)
                self._nios.add(nio)

    def _genericEthernetDeleteSlot(self):
        """
        Deletes the selected generic Ethernet NIO.
        """

        item = self.uiGenericEthernetListWidget.currentItem()
        if item:
            nio = item.text()
            # check we can delete that NIO
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.name() == nio and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to NIO {}, please remove it first".format(nio))
                    return
            self._nios.remove(nio)
            self.uiGenericEthernetListWidget.takeItem(self.uiGenericEthernetListWidget.currentRow())

    def _linuxEthernetSelectedSlot(self, index):
        """
        Loads the selected Linux interface in lineEdit.

        :param index: ignored
        """

        self.uiLinuxEthernetLineEdit.setText(self.uiLinuxEthernetComboBox.currentText())

    def _linuxEthernetChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiLinuxEthernetListWidget.currentItem()
        if item:
            self.uiDeleteLinuxEthernetPushButton.setEnabled(True)
        else:
            self.uiDeleteLinuxEthernetPushButton.setEnabled(False)

    def _linuxEthernetAddSlot(self):
        """
        Adds a new Linux Ethernet NIO.
        """

        interface = self.uiLinuxEthernetLineEdit.text()
        if interface:
            nio = "nio_gen_linux:{interface}".format(interface=interface)
            if nio not in self._nios:
                self.uiLinuxEthernetListWidget.addItem(nio)
                self._nios.add(nio)

    def _linuxEthernetDeleteSlot(self):
        """
        Deletes the selected Linux Ethernet NIO.
        """

        item = self.uiLinuxEthernetListWidget.currentItem()
        if item:
            nio = item.text()
            # check we can delete that NIO
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.name() == nio and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to NIO {}, please remove it first".format(nio))
                    return
            self._nios.remove(nio)
            self.uiLinuxEthernetListWidget.takeItem(self.uiLinuxEthernetListWidget.currentRow())

    def _NIONATSelectedSlot(self, index):
        """
        Loads a selected NAT NIO.

        :param index: ignored
        """

        item = self.uiNIONATListWidget.currentItem()
        if item:
            nio = item.text()
            match = re.search(r"""^nio_nat:(.+)$""", nio)
            if match:
                self.uiNIONATIdentiferLineEdit.setText(match.group(1))

    def _NIONATChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiNIONATListWidget.currentItem()
        if item:
            self.uiDeleteNIONATPushButton.setEnabled(True)
        else:
            self.uiDeleteNIONATPushButton.setEnabled(False)

    def _NIONATAddSlot(self):
        """
        Adds a new NAT NIO.
        """

        identifier = self.uiNIONATIdentiferLineEdit.text()
        if identifier:
            nio = "nio_nat:{}".format(identifier)
            if nio not in self._nios:
                self.uiNIONATListWidget.addItem(nio)
                self._nios.add(nio)

    def _NIONATDeleteSlot(self):
        """
        Deletes a NAT NIO.
        """

        item = self.uiNIONATListWidget.currentItem()
        if item:
            nio = item.text()
            # check we can delete that NIO
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.name() == nio and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to NIO {}, please remove it first".format(nio))
                    return
            self._nios.remove(nio)
            self.uiNIONATListWidget.takeItem(self.uiNIONATListWidget.currentRow())

    def _NIOUDPSelectedSlot(self, index):
        """
        Loads a selected UDP.

        :param index: ignored
        """

        item = self.uiNIOUDPListWidget.currentItem()
        if item:
            nio = item.text()
            match = re.search(r"""^nio_udp:(\d+):(.+):(\d+)$""", nio)
            if match:
                self.uiLocalPortSpinBox.setValue(int(match.group(1)))
                self.uiRemoteHostLineEdit.setText(match.group(2))
                self.uiRemotePortSpinBox.setValue(int(match.group(3)))

    def _NIOUDPChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiNIOUDPListWidget.currentItem()
        if item:
            self.uiDeleteNIOUDPPushButton.setEnabled(True)
        else:
            self.uiDeleteNIOUDPPushButton.setEnabled(False)

    def _NIOUDPAddSlot(self):
        """
        Adds a new UDP NIO.
        """

        local_port = self.uiLocalPortSpinBox.value()
        remote_host = self.uiRemoteHostLineEdit.text()
        remote_port = self.uiRemotePortSpinBox.value()
        if remote_host:
            nio = "nio_udp:{lport}:{rhost}:{rport}".format(lport=local_port,
                                                           rhost=remote_host,
                                                           rport=remote_port)
            if nio not in self._nios:
                self.uiNIOUDPListWidget.addItem(nio)
                self._nios.add(nio)
                self.uiLocalPortSpinBox.setValue(local_port + 1)
                self.uiRemotePortSpinBox.setValue(remote_port + 1)

    def _NIOUDPDeleteSlot(self):
        """
        Deletes an UDP NIO.
        """

        item = self.uiNIOUDPListWidget.currentItem()
        if item:
            nio = item.text()
            # check we can delete that NIO
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.name() == nio and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to NIO {}, please remove it first".format(nio))
                    return
            self._nios.remove(nio)
            self.uiNIOUDPListWidget.takeItem(self.uiNIOUDPListWidget.currentRow())

    def _NIOTAPSelectedSlot(self, index):
        """
        Loads the selected NIO TAP in lineEdit.

        :param index: ignored
        """

        item = self.uiNIOTAPListWidget.currentItem()
        if item:
            nio = item.text()
            match = re.search(r"""^nio_tap:(.+)$""", nio)
            if match:
                self.uiNIOTAPLineEdit.setText(match.group(1))

    def _NIOTAPChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiNIOTAPListWidget.currentItem()
        if item:
            self.uiDeleteNIOTAPPushButton.setEnabled(True)
        else:
            self.uiDeleteNIOTAPPushButton.setEnabled(False)

    def _NIOTAPAddSlot(self):
        """
        Adds a new UDP NIO.
        """

        tap_interface = self.uiNIOTAPLineEdit.text()
        if tap_interface:
            nio = "nio_tap:{}".format(tap_interface.lower())
            if nio not in self._nios:
                self.uiNIOTAPListWidget.addItem(nio)
                self._nios.add(nio)

    def _NIOTAPDeleteSlot(self):
        """
        Deletes a TAP NIO.
        """

        item = self.uiNIOTAPListWidget.currentItem()
        if item:
            nio = item.text()
            # check we can delete that NIO
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.name() == nio and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to NIO {}, please remove it first".format(nio))
                    return
            self._nios.remove(nio)
            self.uiNIOTAPListWidget.takeItem(self.uiNIOTAPListWidget.currentRow())

    def _NIOUNIXSelectedSlot(self, index):
        """
        Loads a selected UNIX NIO.

        :param index: ignored
        """

        item = self.uiNIOUNIXListWidget.currentItem()
        if item:
            nio = item.text()
            match = re.search(r"""^nio_unix:(.+):(.+)$""", nio)
            if match:
                self.uiLocalFileLineEdit.setText(match.group(1))
                self.uiRemoteFileLineEdit.setText(match.group(2))

    def _NIOUNIXChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiNIOUNIXListWidget.currentItem()
        if item:
            self.uiDeleteNIOUNIXPushButton.setEnabled(True)
        else:
            self.uiDeleteNIOUNIXPushButton.setEnabled(False)

    def _NIOUNIXAddSlot(self):
        """
        Adds a new UNIX NIO.
        """

        local_file = self.uiLocalFileLineEdit.text()
        remote_file = self.uiRemoteFileLineEdit.text()
        if local_file and remote_file:
            nio = "nio_unix:{local}:{remote}".format(local=local_file,
                                                     remote=remote_file)
            if nio not in self._nios:
                self.uiNIOUNIXListWidget.addItem(nio)
                self._nios.add(nio)

    def _NIOUNIXDeleteSlot(self):
        """
        Deletes an UNIX NIO.
        """

        item = self.uiNIOUNIXListWidget.currentItem()
        if item:
            nio = item.text()
            # check we can delete that NIO
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.name() == nio and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to NIO {}, please remove it first".format(nio))
                    return
            self._nios.remove(nio)
            self.uiNIOUNIXListWidget.takeItem(self.uiNIOUNIXListWidget.currentRow())

    def _NIOVDESelectedSlot(self, index):
        """
        Loads a selected VDE NIO.

        :param index: ignored
        """

        item = self.uiNIOVDEListWidget.currentItem()
        if item:
            nio = item.text()
            match = re.search(r"""^nio_vde:(.+):(.+)$""", nio)
            if match:
                self.uiVDEControlFileLineEdit.setText(match.group(1))
                self.uiVDELocalFileLineEdit.setText(match.group(2))

    def _NIOVDEChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiNIOVDEListWidget.currentItem()
        if item:
            self.uiDeleteNIOVDEPushButton.setEnabled(True)
        else:
            self.uiDeleteNIOVDEPushButton.setEnabled(False)

    def _NIOVDEAddSlot(self):
        """
        Adds a new VDE NIO.
        """

        control_file = self.uiVDEControlFileLineEdit.text()
        local_file = self.uiVDELocalFileLineEdit.text()
        if local_file and control_file:
            nio = "nio_vde:{control}:{local}".format(control=control_file, local=local_file)
            if nio not in self._nios:
                self.uiNIOVDEListWidget.addItem(nio)
                self._nios.add(nio)

    def _NIOVDEDeleteSlot(self):
        """
        Deletes a VDE NIO.
        """

        item = self.uiNIOVDEListWidget.currentItem()
        if item:
            nio = item.text()
            # check we can delete that NIO
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.name() == nio and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to NIO {}, please remove it first".format(nio))
                    return
            self._nios.remove(nio)
            self.uiNIOVDEListWidget.takeItem(self.uiNIOVDEListWidget.currentRow())

    def _NIONullSelectedSlot(self, index):
        """
        Loads a selected NULL NIO.

        :param index: ignored
        """

        item = self.uiNIONullListWidget.currentItem()
        if item:
            nio = item.text()
            match = re.search(r"""^nio_null:(.+)$""", nio)
            if match:
                self.uiNIONullIdentiferLineEdit.setText(match.group(1))

    def _NIONullChangedSlot(self):
        """
        Enables the use of the delete button.
        """

        item = self.uiNIONullListWidget.currentItem()
        if item:
            self.uiDeleteNIONullPushButton.setEnabled(True)
        else:
            self.uiDeleteNIONullPushButton.setEnabled(False)

    def _NIONullAddSlot(self):
        """
        Adds a new NULL NIO.
        """

        identifier = self.uiNIONullIdentiferLineEdit.text()
        if identifier:
            nio = "nio_null:{}".format(identifier)
            if nio not in self._nios:
                self.uiNIONullListWidget.addItem(nio)
                self._nios.add(nio)

    def _NIONullDeleteSlot(self):
        """
        Deletes a NULL NIO.
        """

        item = self.uiNIONullListWidget.currentItem()
        if item:
            nio = item.text()
            # check we can delete that NIO
            node_ports = self._node.ports()
            for node_port in node_ports:
                if node_port.name() == nio and not node_port.isFree():
                    QtWidgets.QMessageBox.critical(self, self._node.name(), "A link is connected to NIO {}, please remove it first".format(nio))
                    return
            self._nios.remove(nio)
            self.uiNIONullListWidget.takeItem(self.uiNIONullListWidget.currentRow())

    def loadSettings(self, settings, node, group=False):
        """
        Loads the cloud settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            self.uiNameLineEdit.setText(settings["name"])
        else:
            self.uiNameLineEdit.setEnabled(False)

        self._node = node

        # load all network interfaces
        self.uiGenericEthernetComboBox.clear()
        index = 0
        for interface in settings["interfaces"]:
            if interface["name"].startswith("tap"):
                # do not add TAP interfaces
                continue
            self.uiGenericEthernetComboBox.addItem(interface["name"])
            self.uiGenericEthernetComboBox.setItemData(index, interface["id"], QtCore.Qt.ToolTipRole)
            index += 1
        self.uiGenericEthernetComboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

        # load all network interfaces
        self.uiLinuxEthernetComboBox.clear()
        index = 0
        for interface in settings["interfaces"]:
            if not interface["name"].startswith(r"\Device\NPF_") and not interface["name"].startswith("tap"):
                self.uiLinuxEthernetComboBox.addItem(interface["name"])
                self.uiLinuxEthernetComboBox.setItemData(index, interface["id"], QtCore.Qt.ToolTipRole)
                index += 1
        self.uiLinuxEthernetComboBox.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

        # populate the NIO lists
        self.nios = set()
        self.uiGenericEthernetListWidget.clear()
        self.uiLinuxEthernetListWidget.clear()
        self.uiNIOUDPListWidget.clear()
        self.uiNIOTAPListWidget.clear()
        self.uiNIOUNIXListWidget.clear()
        self.uiNIOVDEListWidget.clear()
        self.uiNIONullListWidget.clear()

        for nio in settings["nios"]:
            self._nios.add(nio)
            if nio.lower().startswith("nio_gen_eth"):
                self.uiGenericEthernetListWidget.addItem(nio)
            elif nio.lower().startswith("nio_gen_linux"):
                self.uiLinuxEthernetListWidget.addItem(nio)
            elif nio.lower().startswith("nio_udp"):
                self.uiNIOUDPListWidget.addItem(nio)
            elif nio.lower().startswith("nio_tap"):
                self.uiNIOTAPListWidget.addItem(nio)
            elif nio.lower().startswith("nio_unix"):
                self.uiNIOUNIXListWidget.addItem(nio)
            elif nio.lower().startswith("nio_vde"):
                self.uiNIOVDEListWidget.addItem(nio)
            elif nio.lower().startswith("nio_null"):
                self.uiNIONullListWidget.addItem(nio)

    def saveSettings(self, settings, node, group=False):
        """
        Saves the cloud settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group
        """

        if not group:
            settings["name"] = self.uiNameLineEdit.text()
        else:
            del settings["name"]

        settings["nios"] = list(self._nios)
