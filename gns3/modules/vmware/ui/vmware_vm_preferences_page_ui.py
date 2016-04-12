# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/vmware/ui/vmware_vm_preferences_page.ui'
#
# Created: Sun Mar 27 12:02:29 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VMwareVMPreferencesPageWidget(object):
    def setupUi(self, VMwareVMPreferencesPageWidget):
        VMwareVMPreferencesPageWidget.setObjectName("VMwareVMPreferencesPageWidget")
        VMwareVMPreferencesPageWidget.resize(567, 488)
        VMwareVMPreferencesPageWidget.setAccessibleDescription("")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VMwareVMPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(VMwareVMPreferencesPageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiVMwareVMsTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
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
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiVMwareVMInfoTreeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVMwareVMInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVMwareVMInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiVMwareVMInfoTreeWidget.setIndentation(10)
        self.uiVMwareVMInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiVMwareVMInfoTreeWidget.setObjectName("uiVMwareVMInfoTreeWidget")
        self.uiVMwareVMInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiVMwareVMInfoTreeWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewVMwareVMPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiNewVMwareVMPushButton.setObjectName("uiNewVMwareVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewVMwareVMPushButton)
        self.uiEditVMwareVMPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiEditVMwareVMPushButton.setEnabled(False)
        self.uiEditVMwareVMPushButton.setObjectName("uiEditVMwareVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditVMwareVMPushButton)
        self.uiDeleteVMwareVMPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDeleteVMwareVMPushButton.setEnabled(False)
        self.uiDeleteVMwareVMPushButton.setObjectName("uiDeleteVMwareVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteVMwareVMPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(VMwareVMPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(VMwareVMPreferencesPageWidget)
        VMwareVMPreferencesPageWidget.setTabOrder(self.uiNewVMwareVMPushButton, self.uiDeleteVMwareVMPushButton)

    def retranslateUi(self, VMwareVMPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        VMwareVMPreferencesPageWidget.setWindowTitle(_translate("VMwareVMPreferencesPageWidget", "VMware VMs"))
        VMwareVMPreferencesPageWidget.setAccessibleName(_translate("VMwareVMPreferencesPageWidget", "VMware VM templates"))
        self.uiVMwareVMInfoTreeWidget.headerItem().setText(0, _translate("VMwareVMPreferencesPageWidget", "1"))
        self.uiVMwareVMInfoTreeWidget.headerItem().setText(1, _translate("VMwareVMPreferencesPageWidget", "2"))
        self.uiNewVMwareVMPushButton.setText(_translate("VMwareVMPreferencesPageWidget", "&New"))
        self.uiEditVMwareVMPushButton.setText(_translate("VMwareVMPreferencesPageWidget", "&Edit"))
        self.uiDeleteVMwareVMPushButton.setText(_translate("VMwareVMPreferencesPageWidget", "&Delete"))

