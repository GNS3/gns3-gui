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


from .vm_wizard import VMWizard
from gns3.qt import QtWidgets
from gns3.servers import Servers


class VMWithImagesWizard(VMWizard):
    """
    Base class for VM wizard with image management (Qemu, IOU...)

    :param devices: List of existing device for this type
    :param use_local_server: Value the use_local_server settings for this module
    :param parent: parent widget
    """

    def __init__(self, devices, use_local_server, parent):
        # The list of images combo box (Qemu support multiple images)
        self._images_combo_boxes = set()

        # The list of radio button for existing image or new images
        self._radio_existing_images_buttons = set()

        super().__init__(devices, use_local_server, parent)

    def refreshImageStepsButtons(self):
        """
        When changing the server type (remote or local)
        Refresh all the image selectors
        """
        for radio_button in self._radio_existing_images_buttons:
            radio_button.setChecked(radio_button.isChecked())

    def _vmToggledSlot(self, checked):
        super()._vmToggledSlot(checked)
        if checked:
            self.refreshImageStepsButtons()

    def _remoteServerToggledSlot(self, checked):
        super()._remoteServerToggledSlot(checked)
        if checked:
            self.refreshImageStepsButtons()

    def _localToggledSlot(self, checked):
        super()._localToggledSlot(checked)
        if checked:
            self.refreshImageStepsButtons()

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
            line_edit.setText(create_dialog.uiLocationLineEdit.text())

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
        if item and item["path"]:
            line_edit.setText(item["path"])
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
                line_edit.setText(combo_box.itemData(combo_box.currentIndex())["path"])
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

        # Wizard is closed
        if self.currentPage() is None:
            return

        if len(result) == 0:
            for radio_button in self._radio_existing_images_buttons:
                if radio_button.isChecked() and self._widgetOnCurrentPage(radio_button):
                    for button in radio_button.parent().findChildren(QtWidgets.QRadioButton):
                        if button != radio_button:
                            button.setChecked(True)
                        button.hide()
        else:
            for radio_button in self._radio_existing_images_buttons:
                if self._widgetOnCurrentPage(radio_button):
                    for button in radio_button.parent().findChildren(QtWidgets.QRadioButton):
                        if button == radio_button:
                            button.setChecked(True)
                        button.show()

        for combo_box in self._images_combo_boxes:
            if self._widgetOnCurrentPage(combo_box):
                combo_box.clear()
                for vm in result:
                    combo_box.addItem(vm["path"], vm)


    def _widgetOnCurrentPage(self, widget):
        """
        :returns Boolean True if widget is current active Wizard page
        """
        return self.currentPage().findChild(widget.__class__, widget.objectName()) is not None

