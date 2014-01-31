# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/workspace/git/gns3-gui/gns3/modules/dynamips/ui/ethernet_hub_configuration_page.ui'
#
# Created: Tue Jan 21 20:55:02 2014
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
        self.gridlayout1 = QtGui.QGridLayout(self.uiSettingsGroupBox)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.uiPortsLabel = QtGui.QLabel(self.uiSettingsGroupBox)
        self.uiPortsLabel.setObjectName(_fromUtf8("uiPortsLabel"))
        self.gridlayout1.addWidget(self.uiPortsLabel, 0, 0, 1, 1)
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
        self.gridlayout1.addWidget(self.uiPortsSpinBox, 0, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 71, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout1.addItem(spacerItem, 1, 1, 1, 1)
        self.gridlayout.addWidget(self.uiSettingsGroupBox, 0, 0, 1, 2)

        self.retranslateUi(ethernetHubConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(ethernetHubConfigPageWidget)

    def retranslateUi(self, ethernetHubConfigPageWidget):
        ethernetHubConfigPageWidget.setWindowTitle(_translate("ethernetHubConfigPageWidget", "Ethernet hub", None))
        self.uiSettingsGroupBox.setTitle(_translate("ethernetHubConfigPageWidget", "Settings", None))
        self.uiPortsLabel.setText(_translate("ethernetHubConfigPageWidget", "Number of ports:", None))

