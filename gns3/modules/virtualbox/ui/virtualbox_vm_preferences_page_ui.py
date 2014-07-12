# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/workspace/git/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_preferences_page.ui'
#
# Created: Sat Jul 12 12:53:36 2014
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

class Ui_VirtualBoxVMPreferencesPageWidget(object):
    def setupUi(self, VirtualBoxVMPreferencesPageWidget):
        VirtualBoxVMPreferencesPageWidget.setObjectName(_fromUtf8("VirtualBoxVMPreferencesPageWidget"))
        VirtualBoxVMPreferencesPageWidget.resize(355, 461)
        self.vboxlayout = QtGui.QVBoxLayout(VirtualBoxVMPreferencesPageWidget)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTabWidget = QtGui.QTabWidget(VirtualBoxVMPreferencesPageWidget)
        self.uiTabWidget.setEnabled(True)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiVirtualBoxVMTabWidget = QtGui.QWidget()
        self.uiVirtualBoxVMTabWidget.setObjectName(_fromUtf8("uiVirtualBoxVMTabWidget"))
        self.gridLayout = QtGui.QGridLayout(self.uiVirtualBoxVMTabWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiAdaptersLabel = QtGui.QLabel(self.uiVirtualBoxVMTabWidget)
        self.uiAdaptersLabel.setObjectName(_fromUtf8("uiAdaptersLabel"))
        self.gridLayout.addWidget(self.uiAdaptersLabel, 2, 0, 1, 1)
        self.uiAdaptersSpinBox = QtGui.QSpinBox(self.uiVirtualBoxVMTabWidget)
        self.uiAdaptersSpinBox.setMinimum(1)
        self.uiAdaptersSpinBox.setMaximum(32)
        self.uiAdaptersSpinBox.setObjectName(_fromUtf8("uiAdaptersSpinBox"))
        self.gridLayout.addWidget(self.uiAdaptersSpinBox, 2, 1, 1, 1)
        self.uiEnableConsoleSupportCheckBox = QtGui.QCheckBox(self.uiVirtualBoxVMTabWidget)
        self.uiEnableConsoleSupportCheckBox.setChecked(True)
        self.uiEnableConsoleSupportCheckBox.setObjectName(_fromUtf8("uiEnableConsoleSupportCheckBox"))
        self.gridLayout.addWidget(self.uiEnableConsoleSupportCheckBox, 3, 0, 1, 2)
        self.uiNameLabel = QtGui.QLabel(self.uiVirtualBoxVMTabWidget)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 1, 0, 1, 1)
        self.uiVirtualBoxVMsTreeWidget = QtGui.QTreeWidget(self.uiVirtualBoxVMTabWidget)
        self.uiVirtualBoxVMsTreeWidget.setObjectName(_fromUtf8("uiVirtualBoxVMsTreeWidget"))
        self.gridLayout.addWidget(self.uiVirtualBoxVMsTreeWidget, 0, 0, 1, 2)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiSaveVirtualBoxVMPushButton = QtGui.QPushButton(self.uiVirtualBoxVMTabWidget)
        self.uiSaveVirtualBoxVMPushButton.setObjectName(_fromUtf8("uiSaveVirtualBoxVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiSaveVirtualBoxVMPushButton)
        self.uiDeleteVirtualBoxVMPushButton = QtGui.QPushButton(self.uiVirtualBoxVMTabWidget)
        self.uiDeleteVirtualBoxVMPushButton.setEnabled(False)
        self.uiDeleteVirtualBoxVMPushButton.setObjectName(_fromUtf8("uiDeleteVirtualBoxVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiDeleteVirtualBoxVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 6, 0, 1, 2)
        self.uiNameLineEdit = QtGui.QLineEdit(self.uiVirtualBoxVMTabWidget)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 1, 1, 1, 1)
        self.uiEnableConsoleServerCheckBox = QtGui.QCheckBox(self.uiVirtualBoxVMTabWidget)
        self.uiEnableConsoleServerCheckBox.setEnabled(True)
        self.uiEnableConsoleServerCheckBox.setChecked(False)
        self.uiEnableConsoleServerCheckBox.setObjectName(_fromUtf8("uiEnableConsoleServerCheckBox"))
        self.gridLayout.addWidget(self.uiEnableConsoleServerCheckBox, 4, 0, 1, 2)
        self.uiHeadlessModeCheckBox = QtGui.QCheckBox(self.uiVirtualBoxVMTabWidget)
        self.uiHeadlessModeCheckBox.setChecked(False)
        self.uiHeadlessModeCheckBox.setObjectName(_fromUtf8("uiHeadlessModeCheckBox"))
        self.gridLayout.addWidget(self.uiHeadlessModeCheckBox, 5, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 7, 0, 1, 1)
        self.uiTabWidget.addTab(self.uiVirtualBoxVMTabWidget, _fromUtf8(""))
        self.vboxlayout.addWidget(self.uiTabWidget)

        self.retranslateUi(VirtualBoxVMPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxVMPreferencesPageWidget)

    def retranslateUi(self, VirtualBoxVMPreferencesPageWidget):
        VirtualBoxVMPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VMs", None))
        self.uiAdaptersLabel.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Adapters:", None))
        self.uiEnableConsoleSupportCheckBox.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Enable console support", None))
        self.uiNameLabel.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Name:", None))
        self.uiVirtualBoxVMsTreeWidget.headerItem().setText(0, _translate("VirtualBoxVMPreferencesPageWidget", "VM", None))
        self.uiVirtualBoxVMsTreeWidget.headerItem().setText(1, _translate("VirtualBoxVMPreferencesPageWidget", "Server", None))
        self.uiSaveVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Save", None))
        self.uiDeleteVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Delete", None))
        self.uiEnableConsoleServerCheckBox.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Enable console server", None))
        self.uiHeadlessModeCheckBox.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Start VM in headless mode", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiVirtualBoxVMTabWidget), _translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VMs", None))

