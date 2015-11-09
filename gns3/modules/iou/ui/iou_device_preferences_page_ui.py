# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/iou/ui/iou_device_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IOUDevicePreferencesPageWidget(object):

    def setupUi(self, IOUDevicePreferencesPageWidget):
        IOUDevicePreferencesPageWidget.setObjectName("IOUDevicePreferencesPageWidget")
        IOUDevicePreferencesPageWidget.resize(505, 350)
        IOUDevicePreferencesPageWidget.setAccessibleDescription("")
        self.gridLayout = QtWidgets.QGridLayout(IOUDevicePreferencesPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewIOUDevicePushButton = QtWidgets.QPushButton(IOUDevicePreferencesPageWidget)
        self.uiNewIOUDevicePushButton.setObjectName("uiNewIOUDevicePushButton")
        self.horizontalLayout_5.addWidget(self.uiNewIOUDevicePushButton)
        self.uiEditIOUDevicePushButton = QtWidgets.QPushButton(IOUDevicePreferencesPageWidget)
        self.uiEditIOUDevicePushButton.setEnabled(False)
        self.uiEditIOUDevicePushButton.setObjectName("uiEditIOUDevicePushButton")
        self.horizontalLayout_5.addWidget(self.uiEditIOUDevicePushButton)
        self.uiDeleteIOUDevicePushButton = QtWidgets.QPushButton(IOUDevicePreferencesPageWidget)
        self.uiDeleteIOUDevicePushButton.setEnabled(False)
        self.uiDeleteIOUDevicePushButton.setObjectName("uiDeleteIOUDevicePushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteIOUDevicePushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)
        self.uiIOUDeviceInfoTreeWidget = QtWidgets.QTreeWidget(IOUDevicePreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOUDeviceInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiIOUDeviceInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiIOUDeviceInfoTreeWidget.setIndentation(10)
        self.uiIOUDeviceInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiIOUDeviceInfoTreeWidget.setObjectName("uiIOUDeviceInfoTreeWidget")
        self.uiIOUDeviceInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiIOUDeviceInfoTreeWidget, 0, 1, 1, 1)
        self.uiIOUDevicesTreeWidget = QtWidgets.QTreeWidget(IOUDevicePreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOUDevicesTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiIOUDevicesTreeWidget.setSizePolicy(sizePolicy)
        self.uiIOUDevicesTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiIOUDevicesTreeWidget.setFont(font)
        self.uiIOUDevicesTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiIOUDevicesTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiIOUDevicesTreeWidget.setRootIsDecorated(False)
        self.uiIOUDevicesTreeWidget.setObjectName("uiIOUDevicesTreeWidget")
        self.uiIOUDevicesTreeWidget.headerItem().setText(0, "1")
        self.uiIOUDevicesTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiIOUDevicesTreeWidget, 0, 0, 2, 1)

        self.retranslateUi(IOUDevicePreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(IOUDevicePreferencesPageWidget)
        IOUDevicePreferencesPageWidget.setTabOrder(self.uiNewIOUDevicePushButton, self.uiDeleteIOUDevicePushButton)

    def retranslateUi(self, IOUDevicePreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        IOUDevicePreferencesPageWidget.setWindowTitle(_translate("IOUDevicePreferencesPageWidget", "IOU Devices"))
        IOUDevicePreferencesPageWidget.setAccessibleName(_translate("IOUDevicePreferencesPageWidget", "IOU Device templates"))
        self.uiNewIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&New"))
        self.uiEditIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&Edit"))
        self.uiDeleteIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&Delete"))
        self.uiIOUDeviceInfoTreeWidget.headerItem().setText(0, _translate("IOUDevicePreferencesPageWidget", "1"))
        self.uiIOUDeviceInfoTreeWidget.headerItem().setText(1, _translate("IOUDevicePreferencesPageWidget", "2"))
