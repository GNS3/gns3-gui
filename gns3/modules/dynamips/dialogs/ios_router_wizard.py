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
Wizard for IOS routers.
"""

import os
import re

from gns3.qt import QtCore, QtGui, QtWidgets
from gns3.servers import Servers
from gns3.node import Node
from gns3.utils.run_in_terminal import RunInTerminal
from gns3.utils.get_resource import get_resource
from gns3.utils.get_default_base_config import get_default_base_config
from gns3.dialogs.vm_with_images_wizard import VMWithImagesWizard

from ..ui.ios_router_wizard_ui import Ui_IOSRouterWizard
from ..settings import PLATFORMS_DEFAULT_RAM, PLATFORMS_DEFAULT_NVRAM, CHASSIS, ADAPTER_MATRIX, WIC_MATRIX
from .. import Dynamips
from ..nodes.c1700 import C1700
from ..nodes.c2600 import C2600
from ..nodes.c2691 import C2691
from ..nodes.c3600 import C3600
from ..nodes.c3725 import C3725
from ..nodes.c3745 import C3745
from ..nodes.c7200 import C7200

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


class IOSRouterWizard(VMWithImagesWizard, Ui_IOSRouterWizard):

    """
    Wizard to create an IOS router.

    :param parent: parent widget
    :param ios_routers: existing IOS routers
    """

    def __init__(self, ios_routers, parent):

        super().__init__(ios_routers, Dynamips.instance().settings()["use_local_server"], parent)
        self.setPixmap(QtWidgets.QWizard.LogoPixmap, QtGui.QPixmap(":/symbols/router.svg"))

        self.uiTestIOSImagePushButton.clicked.connect(self._testIOSImageSlot)
        self.uiIdlePCFinderPushButton.clicked.connect(self._idlePCFinderSlot)
        self.uiEtherSwitchCheckBox.stateChanged.connect(self._etherSwitchSlot)
        self.uiPlatformComboBox.currentIndexChanged[str].connect(self._platformChangedSlot)
        self.uiPlatformComboBox.addItems(list(PLATFORMS_DEFAULT_RAM.keys()))

        self._router = None
        # Validate the Idle PC value
        self._idle_valid = False
        idle_pc_rgx = QtCore.QRegExp("^(0x[0-9a-fA-F]{8})?$")
        validator = QtGui.QRegExpValidator(idle_pc_rgx, self)
        self.uiIdlepcLineEdit.setValidator(validator)
        self.uiIdlepcLineEdit.textChanged.connect(self._idlePCValidateSlot)
        self.uiIdlepcLineEdit.textChanged.emit(self.uiIdlepcLineEdit.text())

        # location of the base config templates
        self._base_startup_config_template = get_resource(os.path.join("configs", "ios_base_startup-config.txt"))
        self._base_etherswitch_startup_config_template = get_resource(os.path.join("configs", "ios_etherswitch_startup-config.txt"))

        # FIXME: hide because of issue on Windows.
        self.uiTestIOSImagePushButton.hide()

        # Mandatory fields
        self.uiNamePlatformWizardPage.registerField("name*", self.uiNameLineEdit)
        self.uiIOSImageWizardPage.registerField("image*", self.uiIOSImageLineEdit)

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

        from ..pages.ios_router_preferences_page import IOSRouterPreferencesPage
        self.addImageSelector(self.uiIOSExistingImageRadioButton,
                              self.uiIOSImageListComboBox,
                              self.uiIOSImageLineEdit,
                              self.uiIOSImageToolButton,
                              IOSRouterPreferencesPage.getIOSImage)

    def _prefillPlatform(self):
        """
        Try to guess the platform based on image name
        """
        # try to guess the platform
        image = os.path.basename(self.uiIOSImageLineEdit.text())
        match = re.match("^(c[0-9]+)p?\\-\w+", image.lower())
        if not match:
            QtWidgets.QMessageBox.warning(self, "IOS image", "Could not detect the platform, make sure this is a valid IOS image!")
            return

        detected_platform = match.group(1)
        detected_chassis = ""
        # IOS images for the 3600 platform start with the chassis name (c3620 etc.)
        for platform, chassis in CHASSIS.items():
            if detected_platform[1:] in chassis:
                detected_chassis = detected_platform[1:]
                detected_platform = platform
                break

        if detected_platform not in PLATFORMS_DEFAULT_RAM:
            QtWidgets.QMessageBox.warning(self, "IOS image", "This IOS image is for the {} platform/chassis and is not supported by this application!".format(detected_platform))
            return

        if image.lower().startswith("c7200p"):
            QtWidgets.QMessageBox.warning(self, "IOS image", "This IOS image is for c7200 PowerPC routers and is not recommended. Please use an IOS image that do not start with c7200p.")

        if image.lower().startswith("c1700") or image.lower().startswith("c2600"):
            QtWidgets.QMessageBox.warning(self, "IOS image", "Using c1700 or c2600 IOS images is not recommended, they can be unstable or buggy")

        index = self.uiPlatformComboBox.findText(detected_platform)
        if index != -1:
            self.uiPlatformComboBox.setCurrentIndex(index)

        index = self.uiChassisComboBox.findText(detected_chassis)
        if index != -1:
            self.uiChassisComboBox.setCurrentIndex(index)

    def _platformChangedSlot(self, platform):
        """
        Updates the chassis comboBox based on the selected platform.

        :param platform: selected router platform
        """

        self.uiChassisComboBox.clear()
        if platform in CHASSIS:
            self.uiChassisComboBox.addItems(CHASSIS[platform])
        if platform not in ("c2600", "c3600", "c2691", "c3725", "c3745"):
            self.uiEtherSwitchCheckBox.setChecked(False)
            self.uiEtherSwitchCheckBox.hide()
        else:
            self.uiEtherSwitchCheckBox.show()

    def _testIOSImageSlot(self):
        """
        Slot to locally test the IOS image.
        """

        platform = self.uiPlatformComboBox.currentText()
        ram = self.uiRamSpinBox.value()
        ios_image = self.uiIOSImageLineEdit.text()
        dynamips = os.path.realpath(Dynamips.instance().settings()["image"])
        if not os.path.exists(dynamips):
            QtWidgets.QMessageBox.critical(self, "IOS image", "Could not find Dynamips executable: {}".format(dynamips))
            return
        command = '"{path}" -P {platform} -r {ram} "{ios_image}"'.format(path=dynamips,
                                                                         platform=platform[1:],
                                                                         ram=ram,
                                                                         ios_image=ios_image)
        try:
            RunInTerminal(command)
        except OSError as e:
            QtWidgets.QMessageBox.critical(self, "IOS image", "Could not test the IOS image: {}".format(e))

    def _idlePCValidateSlot(self):
        """
        Slot to validate the entered Idle-PC Value
        """

        validator = self.uiIdlepcLineEdit.validator()
        text_input = self.uiIdlepcLineEdit.text()
        state = validator.validate(text_input, len(text_input))[0]
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

    def _idlePCFinderSlot(self):
        """
        Slot for the idle-PC finder.
        """

        from gns3.main_window import MainWindow
        main_window = MainWindow.instance()
        server = Servers.instance().getServerFromString(self.getSettings()["server"])
        module = Dynamips.instance()
        platform = self.uiPlatformComboBox.currentText()
        ios_image = self.uiIOSImageLineEdit.text()
        ram = self.uiRamSpinBox.value()
        router_class = PLATFORM_TO_CLASS[platform]
        self._router = router_class(module, server, main_window.project())
        self._router.setup(ios_image, ram, name="AUTOIDLEPC")
        self._router.created_signal.connect(self.createdSlot)
        self._router.server_error_signal.connect(self.serverErrorSlot)
        self.uiIdlePCFinderPushButton.setEnabled(False)

    def _etherSwitchSlot(self, state):
        """
        Slot if the EtherSwitch option is chosen or not.
        :param state: boolean
        """

        if state:
            # forces the name to EtherSwitch
            self.uiNameLineEdit.setText("EtherSwitch router")
            # self.uiNameLineEdit.setEnabled(False)
        else:
            self.uiNameLineEdit.setText(self.uiPlatformComboBox.currentText())
            # self.uiNameLineEdit.setEnabled(True)

    def createdSlot(self, node_id):
        """
        The node for the auto Idle-PC has been created.

        :param node_id: not used
        """

        self._router.computeAutoIdlepc(self._computeAutoIdlepcCallback)

    def serverErrorSlot(self, node_id, message):
        """
        The auto idle-pc node could not be created.

        :param node_id: not used
        :param message: error message from the server.
        """

        QtWidgets.QMessageBox.critical(self, "Idle-PC finder", "Could not create IOS router: {}".format(message))

    def _computeAutoIdlepcCallback(self, result, error=False, **kwargs):
        """
        Callback for computeAutoIdlepc.

        :param result: server response
        :param error: indicates an error (boolean)
        """

        if self._router:
            self._router.delete()
            self._router = None
        if error:
            QtWidgets.QMessageBox.critical(self, "Idle-PC finder", "Error: {}".format(result["message"]))
        else:
            idlepc = result["idlepc"]
            self.uiIdlepcLineEdit.setText(idlepc)
            QtWidgets.QMessageBox.information(self, "Idle-PC finder", "Idle-PC value {} has been found suitable for your IOS image".format(idlepc))

    def done(self, result):

        if self._router:
            self._router.delete()
        super().done(result)

    def _populateAdapters(self, platform, chassis):
        """
        Loads the adapter and WIC configuration.

        :param platform: the router platform (string)
        :param chassis: the router chassis (string)
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
                self._widget_slots[slot_number].addItems([""] + module_list)

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

    def initializePage(self, page_id):

        super().initializePage(page_id)

        if self.page(page_id) == self.uiIOSImageWizardPage:
            self.loadImagesList("/dynamips/vms")
        elif self.page(page_id) == self.uiNamePlatformWizardPage:
            self._prefillPlatform()
            self.uiNameLineEdit.setText(self.uiPlatformComboBox.currentText())
            ios_image = self.uiIOSImageLineEdit.text()
            self.setWindowTitle("New IOS router - {}".format(os.path.basename(ios_image)))
        elif self.page(page_id) == self.uiMemoryWizardPage:
            # set the correct amount of RAM based on the platform
            from ..pages.ios_router_preferences_page import IOSRouterPreferencesPage
            platform = self.uiPlatformComboBox.currentText()
            path = self.uiIOSImageLineEdit.text()
            if os.path.isfile(path):
                minimum_required_ram = IOSRouterPreferencesPage.getMinimumRequiredRAM(path)
                if minimum_required_ram >= PLATFORMS_DEFAULT_RAM[platform]:
                    self.uiRamSpinBox.setValue(minimum_required_ram)
                else:
                    self.uiRamSpinBox.setValue(PLATFORMS_DEFAULT_RAM[platform])
            else:
                self.uiRamSpinBox.setValue(PLATFORMS_DEFAULT_RAM[platform])

        elif self.page(page_id) == self.uiNetworkAdaptersWizardPage:
            platform = self.uiPlatformComboBox.currentText()
            chassis = self.uiChassisComboBox.currentText()
            if not chassis:
                chassis = ""
            self._populateAdapters(platform, chassis)
            if platform == "c7200":
                self.uiSlot0comboBox.setCurrentIndex(self.uiSlot0comboBox.findText("C7200-IO-FE"))
            if self.uiEtherSwitchCheckBox.isChecked():
                self.uiSlot1comboBox.setCurrentIndex(self.uiSlot1comboBox.findText("NM-16ESW"))

        elif self.page(page_id) == self.uiIdlePCWizardPage:
            path = self.uiIOSImageLineEdit.text()
            idle_pc = Dynamips.getDefaultIdlePC(path)
            if idle_pc is not None:
                self.uiIdlepcLineEdit.setText(idle_pc)

    def validateCurrentPage(self):
        """
        Validates the IOS name and checks validation state for Idle-PC value
        """

        if super().validateCurrentPage() is False:
            return False

        if self.currentPage() == self.uiMemoryWizardPage and self.uiPlatformComboBox.currentText() == "c7200":
            if self.uiRamSpinBox.value() > 512:
                QtWidgets.QMessageBox.critical(self, "c7200 RAM requirement", "c7200 routers with NPE-400 are limited to 512MB of RAM")
                return False
        if self.currentPage() == self.uiIdlePCWizardPage:
            if not self._idle_valid:
                idle_pc = self.uiIdlepcLineEdit.text()
                QtWidgets.QMessageBox.critical(self, "Idle-PC", "{} is not a valid Idle-PC value ".format(idle_pc))
                return False
        return True

    def getSettings(self):
        """
        Returns the settings set in this Wizard.

        :return: settings dict
        """

        image = self.uiIOSImageLineEdit.text()
        if self.uiLocalRadioButton.isChecked():
            server = "local"
        elif self.uiRemoteRadioButton.isChecked():
            server = self.uiRemoteServersComboBox.currentText()
        elif self.uiVMRadioButton.isChecked():
            server = "vm"

        platform = self.uiPlatformComboBox.currentText()
        settings = {
            "name": self.uiNameLineEdit.text(),
            "image": image,
            "startup_config": get_default_base_config(self._base_startup_config_template),
            "ram": self.uiRamSpinBox.value(),
            "nvram": PLATFORMS_DEFAULT_NVRAM[platform],
            "idlepc": self.uiIdlepcLineEdit.text(),
            "platform": platform,
            "chassis": self.uiChassisComboBox.currentText(),
            "server": server,
        }

        if self.uiEtherSwitchCheckBox.isChecked():
            settings["default_name_format"] = "ESW"
            settings["startup_config"] = get_default_base_config(self._base_etherswitch_startup_config_template)
            settings["symbol"] = ":/symbols/multilayer_switch.svg"
            settings["disk0"] = 1  # adds 1MB disk to store vlan.dat
            settings["category"] = Node.switches
        else:
            settings["auto_delete_disks"] = True

        image_file = os.path.basename(image)
        if image_file.lower().startswith("c7200p"):
            settings["npe"] = "npe-g2"

        for slot_id, widget in self._widget_slots.items():
            if widget.isEnabled():
                settings["slot{}".format(slot_id)] = widget.currentText()

        for wic_id, widget in self._widget_wics.items():
            if widget.isEnabled():
                settings["wic{}".format(wic_id)] = widget.currentText()

        return settings

    def nextId(self):
        """
        Wizard rules!
        """

        current_id = self.currentId()
        if self.page(current_id) == self.uiNetworkAdaptersWizardPage:
            platform = self.uiPlatformComboBox.currentText()
            if platform not in WIC_MATRIX:
                # skip the WIC modules page if the platform doesn't support any.
                return self.uiNetworkAdaptersWizardPage.nextId() + 1
        return QtWidgets.QWizard.nextId(self)
