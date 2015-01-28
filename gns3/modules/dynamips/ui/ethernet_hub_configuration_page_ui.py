# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/workspace/git/gns3-gui/gns3/modules/dynamips/ui/ethernet_hub_configuration_page.ui'
#
# Created: Sun Mar 16 11:16:57 2014
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_ethernetHubConfigPageWidget(object):

    def setupUi(self, ethernetHubConfigPageWidget):
        ethernetHubConfigPageWidget.setObjectName(_fromUtf8("ethernetHubConfigPageWidget"))
        ethernetHubConfigPageWidget.resize(381, 270)
        self.gridlayout = QtGui.QGridLayout(ethernetHubConfigPageWidget)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.uiSettingsGroupBox = QtGui.QGroupBox(ethernetHubConfigPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiSettingsGroupBox.sizePolicy().hasHeightForWidth())
        self.uiSettingsGroupBox.setSizePolicy(sizePolicy)
        self.uiSettingsGroupBox.setObjectName(_fromUtf8("uiSettingsGroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.uiSettingsGroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiNameLabel = QtGui.QLabel(self.uiSettingsGroupBox)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(self.uiSettingsGroupBox)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiPortsLabel = QtGui.QLabel(self.uiSettingsGroupBox)
        self.uiPortsLabel.setObjectName(_fromUtf8("uiPortsLabel"))
        self.gridLayout.addWidget(self.uiPortsLabel, 1, 0, 1, 1)
        self.uiPortsSpinBox = QtGui.QSpinBox(self.uiSettingsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPortsSpinBox.sizePolicy().hasHeightForWidth())
        self.uiPortsSpinBox.setSizePolicy(sizePolicy)
        self.uiPortsSpinBox.setMinimum(0)
        self.uiPortsSpinBox.setMaximum(65535)
        self.uiPortsSpinBox.setProperty("value", 1)
        self.uiPortsSpinBox.setObjectName(_fromUtf8("uiPortsSpinBox"))
        self.gridLayout.addWidget(self.uiPortsSpinBox, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 71, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.gridlayout.addWidget(self.uiSettingsGroupBox, 0, 1, 1, 1)

        self.retranslateUi(ethernetHubConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(ethernetHubConfigPageWidget)

    def retranslateUi(self, ethernetHubConfigPageWidget):
        ethernetHubConfigPageWidget.setWindowTitle(_translate("ethernetHubConfigPageWidget", "Ethernet hub", None))
        self.uiSettingsGroupBox.setTitle(_translate("ethernetHubConfigPageWidget", "Settings", None))
        self.uiNameLabel.setText(_translate("ethernetHubConfigPageWidget", "Name:", None))
        self.uiPortsLabel.setText(_translate("ethernetHubConfigPageWidget", "Number of ports:", None))
