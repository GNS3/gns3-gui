# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'vpcs_device_configuration_page.ui'
#
# Created: Mon Jun 22 14:28:27 2015
#      by: PyQt5 UI code generator 5.2.1
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
        self.uiNameLineEdit = QtWidgets.QLineEdit(VPCSDeviceConfigPageWidget)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiSymbolLabel = QtWidgets.QLabel(VPCSDeviceConfigPageWidget)
        self.uiSymbolLabel.setObjectName("uiSymbolLabel")
        self.gridLayout.addWidget(self.uiSymbolLabel, 2, 0, 1, 1)
        self.uiConsolePortSpinBox = QtWidgets.QSpinBox(VPCSDeviceConfigPageWidget)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName("uiConsolePortSpinBox")
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 4, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(263, 212, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 1, 1, 1)
        self.uiConsolePortLabel = QtWidgets.QLabel(VPCSDeviceConfigPageWidget)
        self.uiConsolePortLabel.setObjectName("uiConsolePortLabel")
        self.gridLayout.addWidget(self.uiConsolePortLabel, 4, 0, 1, 1)
        self.uiNameLabel = QtWidgets.QLabel(VPCSDeviceConfigPageWidget)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.uiSymbolLineEdit = QtWidgets.QLineEdit(VPCSDeviceConfigPageWidget)
        self.uiSymbolLineEdit.setObjectName("uiSymbolLineEdit")
        self.horizontalLayout_7.addWidget(self.uiSymbolLineEdit)
        self.uiSymbolToolButton = QtWidgets.QToolButton(VPCSDeviceConfigPageWidget)
        self.uiSymbolToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiSymbolToolButton.setObjectName("uiSymbolToolButton")
        self.horizontalLayout_7.addWidget(self.uiSymbolToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_7, 2, 1, 1, 1)
        self.uiCategoryLabel = QtWidgets.QLabel(VPCSDeviceConfigPageWidget)
        self.uiCategoryLabel.setObjectName("uiCategoryLabel")
        self.gridLayout.addWidget(self.uiCategoryLabel, 3, 0, 1, 1)
        self.uiCategoryComboBox = QtWidgets.QComboBox(VPCSDeviceConfigPageWidget)
        self.uiCategoryComboBox.setObjectName("uiCategoryComboBox")
        self.gridLayout.addWidget(self.uiCategoryComboBox, 3, 1, 1, 1)

        self.retranslateUi(VPCSDeviceConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(VPCSDeviceConfigPageWidget)

    def retranslateUi(self, VPCSDeviceConfigPageWidget):
        _translate = gns3.qt.translate
        VPCSDeviceConfigPageWidget.setWindowTitle(_translate("VPCSDeviceConfigPageWidget", "VPCS device configuration"))
        self.uiSymbolLabel.setText(_translate("VPCSDeviceConfigPageWidget", "Symbol:"))
        self.uiConsolePortLabel.setText(_translate("VPCSDeviceConfigPageWidget", "Console port:"))
        self.uiNameLabel.setText(_translate("VPCSDeviceConfigPageWidget", "Name:"))
        self.uiSymbolToolButton.setText(_translate("VPCSDeviceConfigPageWidget", "&Browse..."))
        self.uiCategoryLabel.setText(_translate("VPCSDeviceConfigPageWidget", "Category:"))

