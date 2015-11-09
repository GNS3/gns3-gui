# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/vpcs/ui/vpcs_device_configuration_page.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VPCSDeviceConfigPageWidget(object):

    def setupUi(self, VPCSDeviceConfigPageWidget):
        VPCSDeviceConfigPageWidget.setObjectName("VPCSDeviceConfigPageWidget")
        VPCSDeviceConfigPageWidget.resize(391, 246)
        self.gridLayout = QtWidgets.QGridLayout(VPCSDeviceConfigPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.uiNameLineEdit = QtWidgets.QLineEdit(VPCSDeviceConfigPageWidget)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiConsolePortSpinBox = QtWidgets.QSpinBox(VPCSDeviceConfigPageWidget)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName("uiConsolePortSpinBox")
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(263, 212, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.uiConsolePortLabel = QtWidgets.QLabel(VPCSDeviceConfigPageWidget)
        self.uiConsolePortLabel.setObjectName("uiConsolePortLabel")
        self.gridLayout.addWidget(self.uiConsolePortLabel, 2, 0, 1, 1)
        self.uiNameLabel = QtWidgets.QLabel(VPCSDeviceConfigPageWidget)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)

        self.retranslateUi(VPCSDeviceConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(VPCSDeviceConfigPageWidget)

    def retranslateUi(self, VPCSDeviceConfigPageWidget):
        _translate = QtCore.QCoreApplication.translate
        VPCSDeviceConfigPageWidget.setWindowTitle(_translate("VPCSDeviceConfigPageWidget", "VPCS device configuration"))
        self.uiConsolePortLabel.setText(_translate("VPCSDeviceConfigPageWidget", "Console port:"))
        self.uiNameLabel.setText(_translate("VPCSDeviceConfigPageWidget", "Name:"))
