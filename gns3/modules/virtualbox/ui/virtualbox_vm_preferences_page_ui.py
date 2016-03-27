# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/virtualbox/ui/virtualbox_vm_preferences_page.ui'
#
# Created: Sun Mar 27 12:02:29 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VirtualBoxVMPreferencesPageWidget(object):
    def setupUi(self, VirtualBoxVMPreferencesPageWidget):
        VirtualBoxVMPreferencesPageWidget.setObjectName("VirtualBoxVMPreferencesPageWidget")
        VirtualBoxVMPreferencesPageWidget.resize(572, 486)
        VirtualBoxVMPreferencesPageWidget.setAccessibleDescription("")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VirtualBoxVMPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(VirtualBoxVMPreferencesPageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiVirtualBoxVMsTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
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
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiVirtualBoxVMInfoTreeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVirtualBoxVMInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVirtualBoxVMInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiVirtualBoxVMInfoTreeWidget.setIndentation(10)
        self.uiVirtualBoxVMInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiVirtualBoxVMInfoTreeWidget.setObjectName("uiVirtualBoxVMInfoTreeWidget")
        self.uiVirtualBoxVMInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiVirtualBoxVMInfoTreeWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewVirtualBoxVMPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiNewVirtualBoxVMPushButton.setObjectName("uiNewVirtualBoxVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewVirtualBoxVMPushButton)
        self.uiEditVirtualBoxVMPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiEditVirtualBoxVMPushButton.setEnabled(False)
        self.uiEditVirtualBoxVMPushButton.setObjectName("uiEditVirtualBoxVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditVirtualBoxVMPushButton)
        self.uiDeleteVirtualBoxVMPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDeleteVirtualBoxVMPushButton.setEnabled(False)
        self.uiDeleteVirtualBoxVMPushButton.setObjectName("uiDeleteVirtualBoxVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteVirtualBoxVMPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(VirtualBoxVMPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(VirtualBoxVMPreferencesPageWidget)
        VirtualBoxVMPreferencesPageWidget.setTabOrder(self.uiNewVirtualBoxVMPushButton, self.uiDeleteVirtualBoxVMPushButton)

    def retranslateUi(self, VirtualBoxVMPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        VirtualBoxVMPreferencesPageWidget.setWindowTitle(_translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VMs"))
        VirtualBoxVMPreferencesPageWidget.setAccessibleName(_translate("VirtualBoxVMPreferencesPageWidget", "VirtualBox VM templates"))
        self.uiVirtualBoxVMInfoTreeWidget.headerItem().setText(0, _translate("VirtualBoxVMPreferencesPageWidget", "1"))
        self.uiVirtualBoxVMInfoTreeWidget.headerItem().setText(1, _translate("VirtualBoxVMPreferencesPageWidget", "2"))
        self.uiNewVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&New"))
        self.uiEditVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&Edit"))
        self.uiDeleteVirtualBoxVMPushButton.setText(_translate("VirtualBoxVMPreferencesPageWidget", "&Delete"))

