# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/workspace/git/gns3-gui/gns3/modules/dynamips/ui/ethernet_switch_configuration_page.ui'
#
# Created: Tue Jan 21 20:35:18 2014
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

class Ui_ethernetSwitchConfigPageWidget(object):
    def setupUi(self, ethernetSwitchConfigPageWidget):
        ethernetSwitchConfigPageWidget.setObjectName(_fromUtf8("ethernetSwitchConfigPageWidget"))
        ethernetSwitchConfigPageWidget.resize(397, 315)
        self.gridlayout = QtGui.QGridLayout(ethernetSwitchConfigPageWidget)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.uiEthernetSwitchSettingsGroupBox = QtGui.QGroupBox(ethernetSwitchConfigPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiEthernetSwitchSettingsGroupBox.sizePolicy().hasHeightForWidth())
        self.uiEthernetSwitchSettingsGroupBox.setSizePolicy(sizePolicy)
        self.uiEthernetSwitchSettingsGroupBox.setObjectName(_fromUtf8("uiEthernetSwitchSettingsGroupBox"))
        self.gridlayout1 = QtGui.QGridLayout(self.uiEthernetSwitchSettingsGroupBox)
        self.gridlayout1.setObjectName(_fromUtf8("gridlayout1"))
        self.label = QtGui.QLabel(self.uiEthernetSwitchSettingsGroupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridlayout1.addWidget(self.label, 0, 0, 1, 1)
        self.uiPortSpinBox = QtGui.QSpinBox(self.uiEthernetSwitchSettingsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPortSpinBox.sizePolicy().hasHeightForWidth())
        self.uiPortSpinBox.setSizePolicy(sizePolicy)
        self.uiPortSpinBox.setMinimum(0)
        self.uiPortSpinBox.setMaximum(65535)
        self.uiPortSpinBox.setProperty("value", 1)
        self.uiPortSpinBox.setObjectName(_fromUtf8("uiPortSpinBox"))
        self.gridlayout1.addWidget(self.uiPortSpinBox, 0, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.uiEthernetSwitchSettingsGroupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridlayout1.addWidget(self.label_3, 1, 0, 1, 1)
        self.uiVlanSpinBox = QtGui.QSpinBox(self.uiEthernetSwitchSettingsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVlanSpinBox.sizePolicy().hasHeightForWidth())
        self.uiVlanSpinBox.setSizePolicy(sizePolicy)
        self.uiVlanSpinBox.setMinimum(0)
        self.uiVlanSpinBox.setMaximum(65535)
        self.uiVlanSpinBox.setProperty("value", 1)
        self.uiVlanSpinBox.setObjectName(_fromUtf8("uiVlanSpinBox"))
        self.gridlayout1.addWidget(self.uiVlanSpinBox, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.uiEthernetSwitchSettingsGroupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridlayout1.addWidget(self.label_2, 2, 0, 1, 1)
        self.uiPortTypeComboBox = QtGui.QComboBox(self.uiEthernetSwitchSettingsGroupBox)
        self.uiPortTypeComboBox.setObjectName(_fromUtf8("uiPortTypeComboBox"))
        self.uiPortTypeComboBox.addItem(_fromUtf8(""))
        self.uiPortTypeComboBox.addItem(_fromUtf8(""))
        self.uiPortTypeComboBox.addItem(_fromUtf8(""))
        self.gridlayout1.addWidget(self.uiPortTypeComboBox, 2, 1, 1, 1)
        self.gridlayout.addWidget(self.uiEthernetSwitchSettingsGroupBox, 0, 0, 1, 2)
        self.uiEthernetSwitchPortsGroupBox = QtGui.QGroupBox(ethernetSwitchConfigPageWidget)
        self.uiEthernetSwitchPortsGroupBox.setObjectName(_fromUtf8("uiEthernetSwitchPortsGroupBox"))
        self.vboxlayout = QtGui.QVBoxLayout(self.uiEthernetSwitchPortsGroupBox)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiPortsTreeWidget = QtGui.QTreeWidget(self.uiEthernetSwitchPortsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPortsTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiPortsTreeWidget.setSizePolicy(sizePolicy)
        self.uiPortsTreeWidget.setRootIsDecorated(False)
        self.uiPortsTreeWidget.setObjectName(_fromUtf8("uiPortsTreeWidget"))
        self.vboxlayout.addWidget(self.uiPortsTreeWidget)
        self.gridlayout.addWidget(self.uiEthernetSwitchPortsGroupBox, 0, 2, 3, 1)
        self.uiAddPushButton = QtGui.QPushButton(ethernetSwitchConfigPageWidget)
        self.uiAddPushButton.setObjectName(_fromUtf8("uiAddPushButton"))
        self.gridlayout.addWidget(self.uiAddPushButton, 1, 0, 1, 1)
        self.uiDeletePushButton = QtGui.QPushButton(ethernetSwitchConfigPageWidget)
        self.uiDeletePushButton.setEnabled(False)
        self.uiDeletePushButton.setObjectName(_fromUtf8("uiDeletePushButton"))
        self.gridlayout.addWidget(self.uiDeletePushButton, 1, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 71, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem, 2, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1, 3, 2, 1, 1)

        self.retranslateUi(ethernetSwitchConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(ethernetSwitchConfigPageWidget)
        ethernetSwitchConfigPageWidget.setTabOrder(self.uiPortSpinBox, self.uiVlanSpinBox)
        ethernetSwitchConfigPageWidget.setTabOrder(self.uiVlanSpinBox, self.uiPortTypeComboBox)
        ethernetSwitchConfigPageWidget.setTabOrder(self.uiPortTypeComboBox, self.uiAddPushButton)
        ethernetSwitchConfigPageWidget.setTabOrder(self.uiAddPushButton, self.uiDeletePushButton)
        ethernetSwitchConfigPageWidget.setTabOrder(self.uiDeletePushButton, self.uiPortsTreeWidget)

    def retranslateUi(self, ethernetSwitchConfigPageWidget):
        ethernetSwitchConfigPageWidget.setWindowTitle(_translate("ethernetSwitchConfigPageWidget", "Ethernet switch configuration", None))
        self.uiEthernetSwitchSettingsGroupBox.setTitle(_translate("ethernetSwitchConfigPageWidget", "Settings", None))
        self.label.setText(_translate("ethernetSwitchConfigPageWidget", "Port:", None))
        self.label_3.setText(_translate("ethernetSwitchConfigPageWidget", "VLAN:", None))
        self.label_2.setText(_translate("ethernetSwitchConfigPageWidget", "Type:", None))
        self.uiPortTypeComboBox.setItemText(0, _translate("ethernetSwitchConfigPageWidget", "access", None))
        self.uiPortTypeComboBox.setItemText(1, _translate("ethernetSwitchConfigPageWidget", "dot1q", None))
        self.uiPortTypeComboBox.setItemText(2, _translate("ethernetSwitchConfigPageWidget", "qinq", None))
        self.uiEthernetSwitchPortsGroupBox.setTitle(_translate("ethernetSwitchConfigPageWidget", "Ports", None))
        self.uiPortsTreeWidget.headerItem().setText(0, _translate("ethernetSwitchConfigPageWidget", "Port", None))
        self.uiPortsTreeWidget.headerItem().setText(1, _translate("ethernetSwitchConfigPageWidget", "VLAN", None))
        self.uiPortsTreeWidget.headerItem().setText(2, _translate("ethernetSwitchConfigPageWidget", "Type", None))
        self.uiAddPushButton.setText(_translate("ethernetSwitchConfigPageWidget", "&Add", None))
        self.uiDeletePushButton.setText(_translate("ethernetSwitchConfigPageWidget", "&Delete", None))

