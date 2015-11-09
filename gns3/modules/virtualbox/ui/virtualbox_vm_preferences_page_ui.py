# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/cetko/projects/gns3/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VirtualBoxVMPreferencesPageWidget(object):

    def setupUi(self, VirtualBoxVMPreferencesPageWidget):
        VirtualBoxVMPreferencesPageWidget.setObjectName("VirtualBoxVMPreferencesPageWidget")
        VirtualBoxVMPreferencesPageWidget.resize(505, 350)
        VirtualBoxVMPreferencesPageWidget.setAccessibleDescription("")
        self.gridLayout = QtWidgets.QGridLayout(VirtualBoxVMPreferencesPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewVirtualBoxVMPushButton = QtWidgets.QPushButton(VirtualBoxVMPreferencesPageWidget)
        self.uiNewVirtualBoxVMPushButton.setObjectName("uiNewVirtualBoxVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewVirtualBoxVMPushButton)
        self.uiEditVirtualBoxVMPushButton = QtWidgets.QPushButton(VirtualBoxVMPreferencesPageWidget)
        self.uiEditVirtualBoxVMPushButton.setEnabled(False)
        self.uiEditVirtualBoxVMPushButton.setObjectName("uiEditVirtualBoxVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditVirtualBoxVMPushButton)
        self.uiDeleteVirtualBoxVMPushButton = QtWidgets.QPushButton(VirtualBoxVMPreferencesPageWidget)
        self.uiDeleteVirtualBoxVMPushButton.setEnabled(False)
        self.uiDeleteVirtualBoxVMPushButton.setObjectName("uiDeleteVirtualBoxVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteVirtualBoxVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)
        self.uiVirtualBoxVMInfoTreeWidget = QtWidgets.QTreeWidget(VirtualBoxVMPreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVirtualBoxVMInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVirtualBoxVMInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiVirtualBoxVMInfoTreeWidget.setIndentation(10)
        self.uiVirtualBoxVMInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiVirtualBoxVMInfoTreeWidget.setObjectName("uiVirtualBoxVMInfoTreeWidget")
        self.uiVirtualBoxVMInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiVirtualBoxVMInfoTreeWidget, 0, 1, 1, 1)
        self.uiVirtualBoxVMsTreeWidget = QtWidgets.QTreeWidget(VirtualBoxVMPreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVirtualBoxVMsTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVirtualBoxVMsTreeWidget.setSizePolicy(sizePolicy)
        self.uiVirtualBoxVMsTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiVirtualBoxVMsTreeWidget.setFont(font)
        self.uiVirtualBoxVMsTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiVirtualBoxVMsTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiVirtualBoxVMsTreeWidget.setRootIsDecorated(False)
        self.uiVirtualBoxVMsTreeWidget.setObjectName("uiVirtualBoxVMsTreeWidget")
        self.uiVirtualBoxVMsTreeWidget.headerItem().setText(0, "1")
        self.uiVirtualBoxVMsTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiVirtualBoxVMsTreeWidget, 0, 0, 2, 1)

        self.retranslateUi(VirtualBoxVMPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxVMPreferencesPageWidget)
        VirtualBoxVMPreferencesPageWidget.setTabOrder(self.uiNewVirtualBoxVMPushButton, self.uiDeleteVirtualBoxVMPushButton)

    def retranslateUi(self, VirtualBoxVMPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        VirtualBoxVMPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VMs"))
        VirtualBoxVMPreferencesPageWidget.setAccessibleName(_translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VM templates"))
        self.uiNewVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&New"))
        self.uiEditVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&Edit"))
        self.uiDeleteVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&Delete"))
        self.uiVirtualBoxVMInfoTreeWidget.headerItem().setText(0, _translate("VirtualBoxVMPreferencesPageWidget", "1"))
        self.uiVirtualBoxVMInfoTreeWidget.headerItem().setText(1, _translate("VirtualBoxVMPreferencesPageWidget", "2"))
