# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/dynamips/ui/ethernet_hub_configuration_page.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ethernetHubConfigPageWidget(object):

    def setupUi(self, ethernetHubConfigPageWidget):
        ethernetHubConfigPageWidget.setObjectName("ethernetHubConfigPageWidget")
        ethernetHubConfigPageWidget.resize(381, 270)
        self.gridlayout = QtWidgets.QGridLayout(ethernetHubConfigPageWidget)
        self.gridlayout.setObjectName("gridlayout")
        self.uiSettingsGroupBox = QtWidgets.QGroupBox(ethernetHubConfigPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiSettingsGroupBox.sizePolicy().hasHeightForWidth())
        self.uiSettingsGroupBox.setSizePolicy(sizePolicy)
        self.uiSettingsGroupBox.setObjectName("uiSettingsGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.uiSettingsGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.uiNameLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtWidgets.QLineEdit(self.uiSettingsGroupBox)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiPortsLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiPortsLabel.setObjectName("uiPortsLabel")
        self.gridLayout.addWidget(self.uiPortsLabel, 1, 0, 1, 1)
        self.uiPortsSpinBox = QtWidgets.QSpinBox(self.uiSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPortsSpinBox.sizePolicy().hasHeightForWidth())
        self.uiPortsSpinBox.setSizePolicy(sizePolicy)
        self.uiPortsSpinBox.setMinimum(0)
        self.uiPortsSpinBox.setMaximum(65535)
        self.uiPortsSpinBox.setProperty("value", 1)
        self.uiPortsSpinBox.setObjectName("uiPortsSpinBox")
        self.gridLayout.addWidget(self.uiPortsSpinBox, 1, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 71, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.gridlayout.addWidget(self.uiSettingsGroupBox, 0, 1, 1, 1)

        self.retranslateUi(ethernetHubConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(ethernetHubConfigPageWidget)

    def retranslateUi(self, ethernetHubConfigPageWidget):
        _translate = QtCore.QCoreApplication.translate
        ethernetHubConfigPageWidget.setWindowTitle(_translate("ethernetHubConfigPageWidget", "Ethernet hub"))
        self.uiSettingsGroupBox.setTitle(_translate("ethernetHubConfigPageWidget", "Settings"))
        self.uiNameLabel.setText(_translate("ethernetHubConfigPageWidget", "Name:"))
        self.uiPortsLabel.setText(_translate("ethernetHubConfigPageWidget", "Number of ports:"))
