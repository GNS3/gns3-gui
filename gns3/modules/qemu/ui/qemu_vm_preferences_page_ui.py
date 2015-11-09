# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/qemu/ui/qemu_vm_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_QemuVMPreferencesPageWidget(object):

    def setupUi(self, QemuVMPreferencesPageWidget):
        QemuVMPreferencesPageWidget.setObjectName("QemuVMPreferencesPageWidget")
        QemuVMPreferencesPageWidget.resize(505, 350)
        QemuVMPreferencesPageWidget.setAccessibleDescription("")
        self.gridLayout = QtWidgets.QGridLayout(QemuVMPreferencesPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewQemuVMPushButton = QtWidgets.QPushButton(QemuVMPreferencesPageWidget)
        self.uiNewQemuVMPushButton.setObjectName("uiNewQemuVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewQemuVMPushButton)
        self.uiEditQemuVMPushButton = QtWidgets.QPushButton(QemuVMPreferencesPageWidget)
        self.uiEditQemuVMPushButton.setEnabled(False)
        self.uiEditQemuVMPushButton.setObjectName("uiEditQemuVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditQemuVMPushButton)
        self.uiDeleteQemuVMPushButton = QtWidgets.QPushButton(QemuVMPreferencesPageWidget)
        self.uiDeleteQemuVMPushButton.setEnabled(False)
        self.uiDeleteQemuVMPushButton.setObjectName("uiDeleteQemuVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteQemuVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)
        self.uiQemuVMInfoTreeWidget = QtWidgets.QTreeWidget(QemuVMPreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiQemuVMInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiQemuVMInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiQemuVMInfoTreeWidget.setIndentation(10)
        self.uiQemuVMInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiQemuVMInfoTreeWidget.setObjectName("uiQemuVMInfoTreeWidget")
        self.uiQemuVMInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiQemuVMInfoTreeWidget, 0, 1, 1, 1)
        self.uiQemuVMsTreeWidget = QtWidgets.QTreeWidget(QemuVMPreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiQemuVMsTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiQemuVMsTreeWidget.setSizePolicy(sizePolicy)
        self.uiQemuVMsTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiQemuVMsTreeWidget.setFont(font)
        self.uiQemuVMsTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiQemuVMsTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiQemuVMsTreeWidget.setRootIsDecorated(False)
        self.uiQemuVMsTreeWidget.setObjectName("uiQemuVMsTreeWidget")
        self.uiQemuVMsTreeWidget.headerItem().setText(0, "1")
        self.uiQemuVMsTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiQemuVMsTreeWidget, 0, 0, 2, 1)

        self.retranslateUi(QemuVMPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(QemuVMPreferencesPageWidget)
        QemuVMPreferencesPageWidget.setTabOrder(self.uiNewQemuVMPushButton, self.uiDeleteQemuVMPushButton)

    def retranslateUi(self, QemuVMPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        QemuVMPreferencesPageWidget.setWindowTitle(_translate("QemuVMPreferencesPageWidget", "Qemu VMs"))
        QemuVMPreferencesPageWidget.setAccessibleName(_translate("QemuVMPreferencesPageWidget", "Qemu VM templates"))
        self.uiNewQemuVMPushButton.setText(_translate("QemuVMPreferencesPageWidget", "&New"))
        self.uiEditQemuVMPushButton.setText(_translate("QemuVMPreferencesPageWidget", "&Edit"))
        self.uiDeleteQemuVMPushButton.setText(_translate("QemuVMPreferencesPageWidget", "&Delete"))
        self.uiQemuVMInfoTreeWidget.headerItem().setText(0, _translate("QemuVMPreferencesPageWidget", "1"))
        self.uiQemuVMInfoTreeWidget.headerItem().setText(1, _translate("QemuVMPreferencesPageWidget", "2"))
