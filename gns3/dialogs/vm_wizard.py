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

import sys

from gns3.qt import QtCore, QtWidgets
from gns3.settings import ENABLE_CLOUD
from gns3.servers import Servers


class VMWizard(QtWidgets.QWizard):

    """
    Base class for VM wizard.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.setWizardStyle(QtWidgets.QWizard.ModernStyle)
        if sys.platform.startswith("darwin"):
            # we want to see the cancel button on OSX
            self.setOptions(QtWidgets.QWizard.NoDefaultButton)

        self._server = Servers.instance().localServer()
        self.uiRemoteRadioButton.toggled.connect(self._remoteServerToggledSlot)
        self.uiLoadBalanceCheckBox.toggled.connect(self._loadBalanceToggledSlot)

        if not ENABLE_CLOUD:
            self.uiCloudRadioButton.hide()

        # The list of images combo box (Qemu support multiple images)
        self._images_combo_boxes = set()

        # The list of button opening file browser for images
        self._images_browser_buttons = set()

    def _remoteServerToggledSlot(self, checked):
        """
        Slot for when the remote server radio button is toggled.

        :param checked: either the button is checked or not
        """

        if checked:
            self.uiRemoteServersGroupBox.setEnabled(True)
            for button in self._images_browser_buttons:
                button.hide()
        else:
            self.uiRemoteServersGroupBox.setEnabled(False)
            for button in self._images_browser_buttons:
                button.show()

    def initializePage(self, page_id):

        if self.page(page_id) == self.uiServerWizardPage:
            self.uiRemoteServersComboBox.clear()
            for server in Servers.instance().remoteServers().values():
                self.uiRemoteServersComboBox.addItem("{}:{}".format(server.host, server.port), server)

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if self.currentPage() == self.uiServerWizardPage:
            if self.uiRemoteRadioButton.isChecked():
                if not Servers.instance().remoteServers():
                    QtWidgets.QMessageBox.critical(self, "Remote server", "There is no remote server registered for this type of VM in preferences")
                    return False
                self._server = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex())
            else:
                self._server = Servers.instance().localServer()
        return True

    def _loadBalanceToggledSlot(self, checked):
        """
        Slot for when the load balance checkbox is toggled.

        :param checked: either the box is checked or not
        """

        if checked:
            self.uiRemoteServersComboBox.setEnabled(False)
        else:
            self.uiRemoteServersComboBox.setEnabled(True)

    def addImageSelector(self, radio_button, combo_box, line_edit, browser, image_selector):
        """
        Add a remote image selector

        :param radio_button: Radio button which toggle display of the listbox
        :param combo_box: The image choice combo box
        :param line_edit: The edit for the image
        :param browser: file upload browser button
        :param image_selector: function which display an image selector and return path
        """

        combo_box.currentIndexChanged.connect(lambda index: self._imageListIndexChangedSlot(index, combo_box, line_edit))
        self._images_combo_boxes.add(combo_box)

        browser.clicked.connect(lambda: self._imageBrowserSlot(line_edit, image_selector))

        self._images_browser_buttons.add(browser)

        self._existingImageToggledSlot(True, combo_box, line_edit, browser)
        radio_button.toggled.connect(lambda checked: self._existingImageToggledSlot(checked, combo_box, line_edit, browser))

    def _imageBrowserSlot(self, line_edit, image_selector):
        """
        Slot to open a file browser and select an image.
        """

        server = Servers.instance().getServerFromString(self.getSettings()["server"])
        path = image_selector(self, server)
        if not path:
            return
        line_edit.clear()
        line_edit.setText(path)

    def _imageListIndexChangedSlot(self, index, combo_box, line_edit):
        """
        User select a different image in the combo box
        """
        item = combo_box.itemData(index)
        if item and item["filename"]:
            line_edit.setText(item["filename"])
        else:
            line_edit.setText("")

    def _existingImageToggledSlot(self, checked, combo_box, line_edit, browser):
        """
        User select the option of using an existing image
        """

        if checked:
            combo_box.show()
            browser.hide()
            line_edit.hide()
            if combo_box.count() > 0:
                line_edit.setText(combo_box.itemData(combo_box.currentIndex())["filename"])
        else:
            combo_box.hide()
            line_edit.setText("")
            line_edit.show()
            browser.show()

    def loadImagesList(self, endpoint):
        """
        Fill the list box with available Images"

        :param endpoint: server endpoint with the list of Images
        """

        self._server.get(endpoint, self._getImagesFromServerCallback)

    def _getImagesFromServerCallback(self, result, error=False, **kwargs):
        """
        Callback for loadImagesList.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if error:
            QtWidgets.QMessageBox.critical(self, "Images", "Error while getting the VMs: {}".format(result["message"]))
            return

        for combo_box in self._images_combo_boxes:
            combo_box.clear()
            for vm in result:
                combo_box.addItem(vm["filename"], vm)
