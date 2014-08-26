# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_preferences_page.ui'
#
# Created: Tue Aug 26 13:47:33 2014
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

class Ui_VirtualBoxVMPreferencesPageWidget(object):
    def setupUi(self, VirtualBoxVMPreferencesPageWidget):
        VirtualBoxVMPreferencesPageWidget.setObjectName(_fromUtf8("VirtualBoxVMPreferencesPageWidget"))
        VirtualBoxVMPreferencesPageWidget.resize(415, 555)
        self.vboxlayout = QtGui.QVBoxLayout(VirtualBoxVMPreferencesPageWidget)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTabWidget = QtGui.QTabWidget(VirtualBoxVMPreferencesPageWidget)
        self.uiTabWidget.setEnabled(True)
        self.uiTabWidget.setObjectName(_fromUtf8("uiTabWidget"))
        self.uiVirtualBoxVMTabWidget = QtGui.QWidget()
        self.uiVirtualBoxVMTabWidget.setObjectName(_fromUtf8("uiVirtualBoxVMTabWidget"))
        self.gridLayout = QtGui.QGridLayout(self.uiVirtualBoxVMTabWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiVirtualBoxVMsTreeWidget = QtGui.QTreeWidget(self.uiVirtualBoxVMTabWidget)
        self.uiVirtualBoxVMsTreeWidget.setObjectName(_fromUtf8("uiVirtualBoxVMsTreeWidget"))
        self.gridLayout.addWidget(self.uiVirtualBoxVMsTreeWidget, 0, 0, 1, 2)
        self.uiVMListLabel = QtGui.QLabel(self.uiVirtualBoxVMTabWidget)
        self.uiVMListLabel.setObjectName(_fromUtf8("uiVMListLabel"))
        self.gridLayout.addWidget(self.uiVMListLabel, 1, 0, 1, 1)
        self.uiVMListComboBox = QtGui.QComboBox(self.uiVirtualBoxVMTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMListComboBox.sizePolicy().hasHeightForWidth())
        self.uiVMListComboBox.setSizePolicy(sizePolicy)
        self.uiVMListComboBox.setObjectName(_fromUtf8("uiVMListComboBox"))
        self.gridLayout.addWidget(self.uiVMListComboBox, 1, 1, 1, 1)
        self.uiAdaptersLabel = QtGui.QLabel(self.uiVirtualBoxVMTabWidget)
        self.uiAdaptersLabel.setObjectName(_fromUtf8("uiAdaptersLabel"))
        self.gridLayout.addWidget(self.uiAdaptersLabel, 2, 0, 1, 1)
        self.uiAdaptersSpinBox = QtGui.QSpinBox(self.uiVirtualBoxVMTabWidget)
        self.uiAdaptersSpinBox.setMinimum(1)
        self.uiAdaptersSpinBox.setMaximum(36)
        self.uiAdaptersSpinBox.setObjectName(_fromUtf8("uiAdaptersSpinBox"))
        self.gridLayout.addWidget(self.uiAdaptersSpinBox, 2, 1, 1, 1)
        self.uiAdapterStartIndexLabel = QtGui.QLabel(self.uiVirtualBoxVMTabWidget)
        self.uiAdapterStartIndexLabel.setObjectName(_fromUtf8("uiAdapterStartIndexLabel"))
        self.gridLayout.addWidget(self.uiAdapterStartIndexLabel, 3, 0, 1, 1)
        self.uiAdapterStartIndexSpinBox = QtGui.QSpinBox(self.uiVirtualBoxVMTabWidget)
        self.uiAdapterStartIndexSpinBox.setMinimum(0)
        self.uiAdapterStartIndexSpinBox.setMaximum(35)
        self.uiAdapterStartIndexSpinBox.setObjectName(_fromUtf8("uiAdapterStartIndexSpinBox"))
        self.gridLayout.addWidget(self.uiAdapterStartIndexSpinBox, 3, 1, 1, 1)
        self.label = QtGui.QLabel(self.uiVirtualBoxVMTabWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 4, 0, 1, 1)
        self.uiAdapterTypesComboBox = QtGui.QComboBox(self.uiVirtualBoxVMTabWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiAdapterTypesComboBox.sizePolicy().hasHeightForWidth())
        self.uiAdapterTypesComboBox.setSizePolicy(sizePolicy)
        self.uiAdapterTypesComboBox.setObjectName(_fromUtf8("uiAdapterTypesComboBox"))
        self.gridLayout.addWidget(self.uiAdapterTypesComboBox, 4, 1, 1, 1)
        self.uiEnableConsoleCheckBox = QtGui.QCheckBox(self.uiVirtualBoxVMTabWidget)
        self.uiEnableConsoleCheckBox.setObjectName(_fromUtf8("uiEnableConsoleCheckBox"))
        self.gridLayout.addWidget(self.uiEnableConsoleCheckBox, 5, 0, 1, 2)
        self.uiHeadlessModeCheckBox = QtGui.QCheckBox(self.uiVirtualBoxVMTabWidget)
        self.uiHeadlessModeCheckBox.setChecked(False)
        self.uiHeadlessModeCheckBox.setObjectName(_fromUtf8("uiHeadlessModeCheckBox"))
        self.gridLayout.addWidget(self.uiHeadlessModeCheckBox, 6, 0, 1, 2)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.uiRefreshPushButton = QtGui.QPushButton(self.uiVirtualBoxVMTabWidget)
        self.uiRefreshPushButton.setObjectName(_fromUtf8("uiRefreshPushButton"))
        self.horizontalLayout_5.addWidget(self.uiRefreshPushButton)
        self.uiSaveVirtualBoxVMPushButton = QtGui.QPushButton(self.uiVirtualBoxVMTabWidget)
        self.uiSaveVirtualBoxVMPushButton.setObjectName(_fromUtf8("uiSaveVirtualBoxVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiSaveVirtualBoxVMPushButton)
        self.uiDeleteVirtualBoxVMPushButton = QtGui.QPushButton(self.uiVirtualBoxVMTabWidget)
        self.uiDeleteVirtualBoxVMPushButton.setEnabled(False)
        self.uiDeleteVirtualBoxVMPushButton.setObjectName(_fromUtf8("uiDeleteVirtualBoxVMPushButton"))
        self.horizontalLayout_5.addWidget(self.uiDeleteVirtualBoxVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 7, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 1)
        self.uiTabWidget.addTab(self.uiVirtualBoxVMTabWidget, _fromUtf8(""))
        self.vboxlayout.addWidget(self.uiTabWidget)

        self.retranslateUi(VirtualBoxVMPreferencesPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxVMPreferencesPageWidget)

    def retranslateUi(self, VirtualBoxVMPreferencesPageWidget):
        VirtualBoxVMPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VMs", None))
        self.uiVirtualBoxVMsTreeWidget.headerItem().setText(0, _translate("VirtualBoxVMPreferencesPageWidget", "VM", None))
        self.uiVirtualBoxVMsTreeWidget.headerItem().setText(1, _translate("VirtualBoxVMPreferencesPageWidget", "Server", None))
        self.uiVMListLabel.setText(_translate("VirtualBoxVMPreferencesPageWidget", "VM name:", None))
        self.uiAdaptersLabel.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Adapters:", None))
        self.uiAdapterStartIndexLabel.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Start at:", None))
        self.label.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Type:", None))
        self.uiEnableConsoleCheckBox.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Enable console", None))
        self.uiHeadlessModeCheckBox.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Start VM in headless mode", None))
        self.uiRefreshPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Refresh VM list", None))
        self.uiSaveVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Save", None))
        self.uiDeleteVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "Delete", None))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.uiVirtualBoxVMTabWidget), _translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VMs", None))

