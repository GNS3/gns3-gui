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

from gns3.qt import QtWidgets
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
        self.uiVMRadioButton.toggled.connect(self._vmToggledSlot)
        self.uiLocalRadioButton.toggled.connect(self._localToggledSlot)
        self.uiLoadBalanceCheckBox.toggled.connect(self._loadBalanceToggledSlot)

        # The list of images combo box (Qemu support multiple images)
        self._images_combo_boxes = set()

        # The list of radio button for existing image or new images
        self._radio_existing_images_buttons = set()

    def refreshImageStepsButtons(self):
        """
        When changing the server type (remote or local)
        Refresh all the image selectors
        """
        for radio_button in self._radio_existing_images_buttons:
            radio_button.setChecked(radio_button.isChecked())

    def _vmToggledSlot(self, checked):
        """
        Slot for when the VM radio button is toggled.

        :param checked: either the button is checked or not
        """
        if checked:
            self.uiRemoteServersGroupBox.setEnabled(False)
            self.uiRemoteServersGroupBox.hide()
            self.refreshImageStepsButtons()

    def _remoteServerToggledSlot(self, checked):
        """
        Slot for when the remote server radio button is toggled.

        :param checked: either the button is checked or not
        """

        if checked:
            self.uiRemoteServersGroupBox.setEnabled(True)
            self.uiRemoteServersGroupBox.show()
            self.refreshImageStepsButtons()

    def _localToggledSlot(self, checked):
        """
        Slot for when the local server radio button is toggled.

        :param checked: either the button is checked or not
        """
        if checked:
            self.uiRemoteServersGroupBox.setEnabled(False)
            self.uiRemoteServersGroupBox.hide()
            self.refreshImageStepsButtons()

    def setStartId(self, index):
        """
        Which page should we use when starting the Wizard
        """
        super().setStartId(index)
        # If we skip the initial page (choosing a server)
        # we check the settings
        if index != 0:
            self.uiLocalRadioButton.setChecked(True)

    def initializePage(self, page_id):

        if self.page(page_id) == self.uiServerWizardPage:
            self.uiRemoteServersComboBox.clear()
            for server in Servers.instance().remoteServers().values():
                self.uiRemoteServersComboBox.addItem(server.url(), server)

    def validateCurrentPage(self):
        """
        Validates the server.
        """

        if self.currentPage() == self.uiServerWizardPage:
            if self.uiRemoteRadioButton.isChecked():
                if not Servers.instance().remoteServers():
                    QtWidgets.QMessageBox.critical(self, "Remote server", "There is no remote server registered in your preferences")
                    return False
                self._server = self.uiRemoteServersComboBox.itemData(self.uiRemoteServersComboBox.currentIndex())
            elif self.uiVMRadioButton.isChecked():
                gns3_vm_server = Servers.instance().vmServer()
                if gns3_vm_server is None:
                    QtWidgets.QMessageBox.critical(self, "GNS3 VM", "The GNS3 VM is not running")
                    return False
                self._server = gns3_vm_server
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

    def addImageSelector(self, radio_button, combo_box, line_edit, browser, image_selector, create_button=None, create_image_wizard=None, image_suffix=""):
        """
        Add a remote image selector

        :param radio_button: Radio button which toggle display of the listbox
        :param combo_box: The image choice combo box
        :param line_edit: The edit for the image
        :param browser: file upload browser button
        :param image_selector: function which display an image selector and return path
        :param create_button: Image create button None if you don't need one
        :param create_image_wizard: Wizard Class for creating a new image
        """

        combo_box.currentIndexChanged.connect(lambda index: self._imageListIndexChangedSlot(index, combo_box, line_edit))
        self._images_combo_boxes.add(combo_box)

        browser.clicked.connect(lambda: self._imageBrowserSlot(line_edit, image_selector))

        if create_button:
            assert create_image_wizard is not None
            create_button.clicked.connect(lambda: self._imageCreateSlot(line_edit, create_image_wizard, image_suffix))

        self._existingImageToggledSlot(True, combo_box, line_edit, browser, create_button)
        radio_button.toggled.connect(lambda checked: self._existingImageToggledSlot(checked, combo_box, line_edit, browser, create_button))
        self._radio_existing_images_buttons.add(radio_button)

    def _imageCreateSlot(self, line_edit, create_image_wizard, image_suffix):
        server = Servers.instance().getServerFromString(self.getSettings()["server"])

        create_dialog = create_image_wizard(self, server, self.uiNameLineEdit.text() + image_suffix)
        if QtWidgets.QDialog.Accepted == create_dialog.exec_():
            line_edit.setText(create_dialog.uiLocationLineEdit.text() + image_suffix)

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

    def _existingImageToggledSlot(self, checked, combo_box, line_edit, browser, create_button):
        """
        User select the option of using an existing image
        """

        if create_button:
            create_button.hide()

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
            if create_button:
                create_button.show()

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
