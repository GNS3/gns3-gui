# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_configuration_page.ui'
#
# Created: Tue Aug 26 13:50:21 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_virtualBoxVMConfigPageWidget(object):
    def setupUi(self, virtualBoxVMConfigPageWidget):
        virtualBoxVMConfigPageWidget.setObjectName(_fromUtf8("virtualBoxVMConfigPageWidget"))
        virtualBoxVMConfigPageWidget.resize(375, 363)
        self.verticalLayout = QtGui.QVBoxLayout(virtualBoxVMConfigPageWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiGeneralgroupBox = QtGui.QGroupBox(virtualBoxVMConfigPageWidget)
        self.uiGeneralgroupBox.setStyleSheet(_fromUtf8(""))
        self.uiGeneralgroupBox.setObjectName(_fromUtf8("uiGeneralgroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.uiGeneralgroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiNameLabel = QtGui.QLabel(self.uiGeneralgroupBox)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(self.uiGeneralgroupBox)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiVMListLabel = QtGui.QLabel(self.uiGeneralgroupBox)
        self.uiVMListLabel.setObjectName(_fromUtf8("uiVMListLabel"))
        self.gridLayout.addWidget(self.uiVMListLabel, 1, 0, 1, 1)
        self.uiVMListComboBox = QtGui.QComboBox(self.uiGeneralgroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMListComboBox.sizePolicy().hasHeightForWidth())
        self.uiVMListComboBox.setSizePolicy(sizePolicy)
        self.uiVMListComboBox.setObjectName(_fromUtf8("uiVMListComboBox"))
        self.gridLayout.addWidget(self.uiVMListComboBox, 1, 1, 1, 1)
        self.uiConsolePortLabel = QtGui.QLabel(self.uiGeneralgroupBox)
        self.uiConsolePortLabel.setObjectName(_fromUtf8("uiConsolePortLabel"))
        self.gridLayout.addWidget(self.uiConsolePortLabel, 2, 0, 1, 1)
        self.uiConsolePortSpinBox = QtGui.QSpinBox(self.uiGeneralgroupBox)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName(_fromUtf8("uiConsolePortSpinBox"))
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 2, 1, 1, 1)
        self.uiEnableConsoleCheckBox = QtGui.QCheckBox(self.uiGeneralgroupBox)
        self.uiEnableConsoleCheckBox.setObjectName(_fromUtf8("uiEnableConsoleCheckBox"))
        self.gridLayout.addWidget(self.uiEnableConsoleCheckBox, 3, 0, 1, 2)
        self.uiHeadlessModeCheckBox = QtGui.QCheckBox(self.uiGeneralgroupBox)
        self.uiHeadlessModeCheckBox.setChecked(False)
        self.uiHeadlessModeCheckBox.setObjectName(_fromUtf8("uiHeadlessModeCheckBox"))
        self.gridLayout.addWidget(self.uiHeadlessModeCheckBox, 4, 0, 1, 2)
        self.verticalLayout.addWidget(self.uiGeneralgroupBox)
        self.groupBox = QtGui.QGroupBox(virtualBoxVMConfigPageWidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.uiAdaptersLabel = QtGui.QLabel(self.groupBox)
        self.uiAdaptersLabel.setObjectName(_fromUtf8("uiAdaptersLabel"))
        self.gridLayout_2.addWidget(self.uiAdaptersLabel, 0, 0, 1, 1)
        self.uiAdaptersSpinBox = QtGui.QSpinBox(self.groupBox)
        self.uiAdaptersSpinBox.setMinimum(1)
        self.uiAdaptersSpinBox.setMaximum(36)
        self.uiAdaptersSpinBox.setObjectName(_fromUtf8("uiAdaptersSpinBox"))
        self.gridLayout_2.addWidget(self.uiAdaptersSpinBox, 0, 1, 1, 1)
        self.uiAdapterStartIndexLabel = QtGui.QLabel(self.groupBox)
        self.uiAdapterStartIndexLabel.setObjectName(_fromUtf8("uiAdapterStartIndexLabel"))
        self.gridLayout_2.addWidget(self.uiAdapterStartIndexLabel, 1, 0, 1, 1)
        self.uiAdapterStartIndexSpinBox = QtGui.QSpinBox(self.groupBox)
        self.uiAdapterStartIndexSpinBox.setMinimum(0)
        self.uiAdapterStartIndexSpinBox.setMaximum(35)
        self.uiAdapterStartIndexSpinBox.setProperty("value", 0)
        self.uiAdapterStartIndexSpinBox.setObjectName(_fromUtf8("uiAdapterStartIndexSpinBox"))
        self.gridLayout_2.addWidget(self.uiAdapterStartIndexSpinBox, 1, 1, 1, 1)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_2.addWidget(self.label, 2, 0, 1, 1)
        self.uiAdapterTypesComboBox = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiAdapterTypesComboBox.sizePolicy().hasHeightForWidth())
        self.uiAdapterTypesComboBox.setSizePolicy(sizePolicy)
        self.uiAdapterTypesComboBox.setObjectName(_fromUtf8("uiAdapterTypesComboBox"))
        self.gridLayout_2.addWidget(self.uiAdapterTypesComboBox, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        spacerItem = QtGui.QSpacerItem(263, 212, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(virtualBoxVMConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(virtualBoxVMConfigPageWidget)

    def retranslateUi(self, virtualBoxVMConfigPageWidget):
        virtualBoxVMConfigPageWidget.setWindowTitle(_translate("virtualBoxVMConfigPageWidget", "VirtualBox VM configuration", None))
        self.uiGeneralgroupBox.setTitle(_translate("virtualBoxVMConfigPageWidget", "General", None))
        self.uiNameLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Name:", None))
        self.uiVMListLabel.setText(_translate("virtualBoxVMConfigPageWidget", "VM name:", None))
        self.uiConsolePortLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Console port:", None))
        self.uiEnableConsoleCheckBox.setText(_translate("virtualBoxVMConfigPageWidget", "Enable console", None))
        self.uiHeadlessModeCheckBox.setText(_translate("virtualBoxVMConfigPageWidget", "Start VM in headless mode", None))
        self.groupBox.setTitle(_translate("virtualBoxVMConfigPageWidget", "Networking", None))
        self.uiAdaptersLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Adapters:", None))
        self.uiAdapterStartIndexLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Start at:", None))
        self.label.setText(_translate("virtualBoxVMConfigPageWidget", "Type:", None))

