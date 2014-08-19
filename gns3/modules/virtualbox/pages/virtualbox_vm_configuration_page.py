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
Configuration page for VirtualBox VMs.
"""

from gns3.qt import QtGui
from gns3.dialogs.node_configurator_dialog import ConfigurationError

from ..ui.virtualbox_vm_configuration_page_ui import Ui_virtualBoxVMConfigPageWidget


class virtualBoxVMConfigurationPage(QtGui.QWidget, Ui_virtualBoxVMConfigPageWidget):
    """
    QWidget configuration page for VirtualBox VMs.
    """

    def __init__(self):

        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.uiAdapterTypesComboBox.clear()
        self.uiAdapterTypesComboBox.addItems(["Automatic",
                                              "PCnet-PCI II (Am79C970A)",
                                              "PCNet-FAST III (Am79C973)",
                                              "Intel PRO/1000 MT Desktop (82540EM)",
                                              "Intel PRO/1000 T Server (82543GC)",
                                              "Intel PRO/1000 MT Server (82545EM)",
                                              "Paravirtualized Network (virtio-net)"])

        #TODO: finish VM name change
        self.uiVMListLabel.hide()
        self.uiVMListComboBox.hide()

        #self.uiIOUImageComboBox.currentIndexChanged.connect(self._IOUImageSelectedSlot)
        #self._current_iou_image = ""

    # def _IOUImageSelectedSlot(self, index):
    #     """
    #     Warn about changing the IOU image of a device.
    #
    #     :param index: ignored
    #     """
    #
    #     #TODO: finish IOU image switch tests
    #     if self._current_iou_image and self._current_iou_image != self.uiIOUImageComboBox.currentText():
    #         QtGui.QMessageBox.warning(self, "IOU image", "The IOU image has been changed, your device may not boot correctly if you apply the new settings")
    #         self._current_iou_image = ""

    def loadSettings(self, settings, node, group=False):
        """
        Loads the VirtualBox VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        if not group:

            # set the device name
            name = self.uiNameLineEdit.text()
            if not name:
                QtGui.QMessageBox.critical(self, "Name", "VirtualBox name cannot be empty!")
            else:
                settings["name"] = name

            self.uiConsolePortSpinBox.setValue(settings["console"])

            # load the available IOU images
            #iou_images = IOU.instance().iouImages()
            #for iou_image in iou_images.values():
            #    if iou_image["server"] == "local" and node.server().isLocal() or iou_image["server"] == node.server().host:
            #        self.uiIOUImageComboBox.addItem(iou_image["image"], iou_image["path"])

            #index = self.uiIOUImageComboBox.findText(os.path.basename(settings["path"]))
            #if index != -1:
            #    self.uiIOUImageComboBox.setCurrentIndex(index)
            #    self._current_iou_image = iou_image["image"]

        else:
            self.uiNameLabel.hide()
            self.uiNameLineEdit.hide()
            self.uiConsolePortLabel.hide()
            self.uiConsolePortSpinBox.hide()
            self.uiVMListLabel.hide()
            self.uiVMListComboBox.hide()

        self.uiAdaptersSpinBox.setValue(settings["adapters"])
        index = self.uiAdapterTypesComboBox.findText(settings["adapter_type"])
        if index != -1:
            self.uiAdapterTypesComboBox.setCurrentIndex(index)
        self.uiHeadlessModeCheckBox.setChecked(settings["headless"])

    def saveSettings(self, settings, node, group=False):
        """
        Saves the VirtualBox VM settings.

        :param settings: the settings (dictionary)
        :param node: Node instance
        :param group: indicates the settings apply to a group of VMs
        """

        # these settings cannot be shared by nodes and updated
        # in the node configurator.
        if not group:
            settings["name"] = self.uiNameLineEdit.text()
            settings["console"] = self.uiConsolePortSpinBox.value()

            # initial_config = self.uiInitialConfigLineEdit.text()
            # if initial_config != settings["initial_config"]:
            #     if os.access(initial_config, os.R_OK):
            #         settings["initial_config"] = initial_config
            #     else:
            #         QtGui.QMessageBox.critical(self, "Initial-config", "Cannot read the initial-config file")
            #
            # # save the IOU image path
            # index = self.uiIOUImageComboBox.currentIndex()
            # ios_path = self.uiIOUImageComboBox.itemData(index)
            # settings["path"] = ios_path
        else:
            del settings["name"]
            del settings["console"]

        settings["adapter_type"] = self.uiAdapterTypesComboBox.currentText()
        settings["headless"] = self.uiHeadlessModeCheckBox.isChecked()

        adapters = self.uiAdaptersSpinBox.value()
        if settings["adapters"] != adapters:
            # check if the adapters settings have changed
            node_ports = node.ports()
            for node_port in node_ports:
                if not node_port.isFree():
                    QtGui.QMessageBox.critical(self, node.name(), "Changing the number of adapters while links are connected isn't supported yet! Please delete all the links first.")
                    raise ConfigurationError()

        settings["adapters"] = adapters
