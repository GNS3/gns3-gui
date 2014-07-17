# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_configuration_page.ui'
#
# Created: Wed Jul 16 15:15:35 2014
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
        virtualBoxVMConfigPageWidget.resize(388, 448)
        self.verticalLayout = QtGui.QVBoxLayout(virtualBoxVMConfigPageWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiGeneralgroupBox = QtGui.QGroupBox(virtualBoxVMConfigPageWidget)
        self.uiGeneralgroupBox.setStyleSheet(_fromUtf8(""))
        self.uiGeneralgroupBox.setObjectName(_fromUtf8("uiGeneralgroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.uiGeneralgroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiHeadlessModeCheckBox = QtGui.QCheckBox(self.uiGeneralgroupBox)
        self.uiHeadlessModeCheckBox.setChecked(False)
        self.uiHeadlessModeCheckBox.setObjectName(_fromUtf8("uiHeadlessModeCheckBox"))
        self.gridLayout.addWidget(self.uiHeadlessModeCheckBox, 5, 0, 1, 3)
        self.uiVMListComboBox = QtGui.QComboBox(self.uiGeneralgroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMListComboBox.sizePolicy().hasHeightForWidth())
        self.uiVMListComboBox.setSizePolicy(sizePolicy)
        self.uiVMListComboBox.setObjectName(_fromUtf8("uiVMListComboBox"))
        self.gridLayout.addWidget(self.uiVMListComboBox, 2, 2, 1, 1)
        self.uiConsolePortSpinBox = QtGui.QSpinBox(self.uiGeneralgroupBox)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName(_fromUtf8("uiConsolePortSpinBox"))
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 1, 2, 1, 1)
        self.uiConsolePortLabel = QtGui.QLabel(self.uiGeneralgroupBox)
        self.uiConsolePortLabel.setObjectName(_fromUtf8("uiConsolePortLabel"))
        self.gridLayout.addWidget(self.uiConsolePortLabel, 1, 0, 1, 2)
        self.uiNameLineEdit = QtGui.QLineEdit(self.uiGeneralgroupBox)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 2, 1, 1)
        self.uiVMListLabel = QtGui.QLabel(self.uiGeneralgroupBox)
        self.uiVMListLabel.setObjectName(_fromUtf8("uiVMListLabel"))
        self.gridLayout.addWidget(self.uiVMListLabel, 2, 0, 1, 1)
        self.uiNameLabel = QtGui.QLabel(self.uiGeneralgroupBox)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.label = QtGui.QLabel(self.uiGeneralgroupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.uiAdaptersLabel = QtGui.QLabel(self.uiGeneralgroupBox)
        self.uiAdaptersLabel.setObjectName(_fromUtf8("uiAdaptersLabel"))
        self.gridLayout.addWidget(self.uiAdaptersLabel, 3, 0, 1, 1)
        self.uiAdaptersSpinBox = QtGui.QSpinBox(self.uiGeneralgroupBox)
        self.uiAdaptersSpinBox.setMinimum(1)
        self.uiAdaptersSpinBox.setMaximum(32)
        self.uiAdaptersSpinBox.setObjectName(_fromUtf8("uiAdaptersSpinBox"))
        self.gridLayout.addWidget(self.uiAdaptersSpinBox, 3, 2, 1, 1)
        self.uiAdapterTypesComboBox = QtGui.QComboBox(self.uiGeneralgroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiAdapterTypesComboBox.sizePolicy().hasHeightForWidth())
        self.uiAdapterTypesComboBox.setSizePolicy(sizePolicy)
        self.uiAdapterTypesComboBox.setObjectName(_fromUtf8("uiAdapterTypesComboBox"))
        self.gridLayout.addWidget(self.uiAdapterTypesComboBox, 4, 2, 1, 1)
        self.verticalLayout.addWidget(self.uiGeneralgroupBox)
        spacerItem = QtGui.QSpacerItem(263, 212, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(virtualBoxVMConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(virtualBoxVMConfigPageWidget)

    def retranslateUi(self, virtualBoxVMConfigPageWidget):
        virtualBoxVMConfigPageWidget.setWindowTitle(_translate("virtualBoxVMConfigPageWidget", "VirtualBox VM configuration", None))
        self.uiGeneralgroupBox.setTitle(_translate("virtualBoxVMConfigPageWidget", "General", None))
        self.uiHeadlessModeCheckBox.setText(_translate("virtualBoxVMConfigPageWidget", "Start VM in headless mode", None))
        self.uiConsolePortLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Console port:", None))
        self.uiVMListLabel.setText(_translate("virtualBoxVMConfigPageWidget", "VM name:", None))
        self.uiNameLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Name:", None))
        self.label.setText(_translate("virtualBoxVMConfigPageWidget", "Type:", None))
        self.uiAdaptersLabel.setText(_translate("virtualBoxVMConfigPageWidget", "Adapters:", None))

