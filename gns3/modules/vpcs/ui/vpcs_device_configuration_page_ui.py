# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vpcs_device_configuration_page.ui'
#
# Created: Wed May  6 14:31:59 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

import gns3.qt
from gns3.qt import QtCore, QtGui, QtWidgets


class Ui_VPCSDeviceConfigPageWidget(object):

    def setupUi(self, VPCSDeviceConfigPageWidget):
        VPCSDeviceConfigPageWidget.setObjectName("VPCSDeviceConfigPageWidget")
        VPCSDeviceConfigPageWidget.resize(411, 252)
        self.gridLayout = QtWidgets.QGridLayout(VPCSDeviceConfigPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.uiNameLabel = QtWidgets.QLabel(VPCSDeviceConfigPageWidget)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtWidgets.QLineEdit(VPCSDeviceConfigPageWidget)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiConsolePortLabel = QtWidgets.QLabel(VPCSDeviceConfigPageWidget)
        self.uiConsolePortLabel.setObjectName("uiConsolePortLabel")
        self.gridLayout.addWidget(self.uiConsolePortLabel, 1, 0, 1, 1)
        self.uiConsolePortSpinBox = QtWidgets.QSpinBox(VPCSDeviceConfigPageWidget)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName("uiConsolePortSpinBox")
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(263, 212, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)

        self.retranslateUi(VPCSDeviceConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(VPCSDeviceConfigPageWidget)

    def retranslateUi(self, VPCSDeviceConfigPageWidget):
        _translate = gns3.qt.translate
        VPCSDeviceConfigPageWidget.setWindowTitle(_translate("VPCSDeviceConfigPageWidget", "VPCS device configuration"))
        self.uiNameLabel.setText(_translate("VPCSDeviceConfigPageWidget", "Name:"))
        self.uiConsolePortLabel.setText(_translate("VPCSDeviceConfigPageWidget", "Console port:"))
