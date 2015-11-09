# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/vmware/ui/vmware_vm_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VMwareVMPreferencesPageWidget(object):

    def setupUi(self, VMwareVMPreferencesPageWidget):
        VMwareVMPreferencesPageWidget.setObjectName("VMwareVMPreferencesPageWidget")
        VMwareVMPreferencesPageWidget.resize(505, 350)
        VMwareVMPreferencesPageWidget.setAccessibleDescription("")
        self.gridLayout = QtWidgets.QGridLayout(VMwareVMPreferencesPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewVMwareVMPushButton = QtWidgets.QPushButton(VMwareVMPreferencesPageWidget)
        self.uiNewVMwareVMPushButton.setObjectName("uiNewVMwareVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewVMwareVMPushButton)
        self.uiEditVMwareVMPushButton = QtWidgets.QPushButton(VMwareVMPreferencesPageWidget)
        self.uiEditVMwareVMPushButton.setEnabled(False)
        self.uiEditVMwareVMPushButton.setObjectName("uiEditVMwareVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditVMwareVMPushButton)
        self.uiDeleteVMwareVMPushButton = QtWidgets.QPushButton(VMwareVMPreferencesPageWidget)
        self.uiDeleteVMwareVMPushButton.setEnabled(False)
        self.uiDeleteVMwareVMPushButton.setObjectName("uiDeleteVMwareVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteVMwareVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)
        self.uiVMwareVMInfoTreeWidget = QtWidgets.QTreeWidget(VMwareVMPreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMwareVMInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVMwareVMInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiVMwareVMInfoTreeWidget.setIndentation(10)
        self.uiVMwareVMInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiVMwareVMInfoTreeWidget.setObjectName("uiVMwareVMInfoTreeWidget")
        self.uiVMwareVMInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiVMwareVMInfoTreeWidget, 0, 1, 1, 1)
        self.uiVMwareVMsTreeWidget = QtWidgets.QTreeWidget(VMwareVMPreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMwareVMsTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVMwareVMsTreeWidget.setSizePolicy(sizePolicy)
        self.uiVMwareVMsTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiVMwareVMsTreeWidget.setFont(font)
        self.uiVMwareVMsTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiVMwareVMsTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiVMwareVMsTreeWidget.setRootIsDecorated(False)
        self.uiVMwareVMsTreeWidget.setObjectName("uiVMwareVMsTreeWidget")
        self.uiVMwareVMsTreeWidget.headerItem().setText(0, "1")
        self.uiVMwareVMsTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiVMwareVMsTreeWidget, 0, 0, 2, 1)

        self.retranslateUi(VMwareVMPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(VMwareVMPreferencesPageWidget)
        VMwareVMPreferencesPageWidget.setTabOrder(self.uiNewVMwareVMPushButton, self.uiDeleteVMwareVMPushButton)

    def retranslateUi(self, VMwareVMPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        VMwareVMPreferencesPageWidget.setWindowTitle(_translate("VMwareVMPreferencesPageWidget", "VMware VMs"))
        VMwareVMPreferencesPageWidget.setAccessibleName(_translate("VMwareVMPreferencesPageWidget", "VMware VM templates"))
        self.uiNewVMwareVMPushButton.setText(_translate("VMwareVMPreferencesPageWidget", "&New"))
        self.uiEditVMwareVMPushButton.setText(_translate("VMwareVMPreferencesPageWidget", "&Edit"))
        self.uiDeleteVMwareVMPushButton.setText(_translate("VMwareVMPreferencesPageWidget", "&Delete"))
        self.uiVMwareVMInfoTreeWidget.headerItem().setText(0, _translate("VMwareVMPreferencesPageWidget", "1"))
        self.uiVMwareVMInfoTreeWidget.headerItem().setText(1, _translate("VMwareVMPreferencesPageWidget", "2"))
