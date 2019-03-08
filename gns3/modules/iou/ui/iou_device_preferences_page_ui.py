# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/iou/ui/iou_device_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IOUDevicePreferencesPageWidget(object):
    def setupUi(self, IOUDevicePreferencesPageWidget):
        IOUDevicePreferencesPageWidget.setObjectName("IOUDevicePreferencesPageWidget")
        IOUDevicePreferencesPageWidget.resize(542, 449)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(IOUDevicePreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(IOUDevicePreferencesPageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiIOUDevicesTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
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
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiIOUDeviceInfoTreeWidget = QtWidgets.QTreeWidget(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOUDeviceInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiIOUDeviceInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiIOUDeviceInfoTreeWidget.setIndentation(10)
        self.uiIOUDeviceInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiIOUDeviceInfoTreeWidget.setObjectName("uiIOUDeviceInfoTreeWidget")
        self.uiIOUDeviceInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiIOUDeviceInfoTreeWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiNewIOUDevicePushButton = QtWidgets.QPushButton(self.widget)
        self.uiNewIOUDevicePushButton.setObjectName("uiNewIOUDevicePushButton")
        self.horizontalLayout.addWidget(self.uiNewIOUDevicePushButton)
        self.uiCopyIOUDevicePushButton = QtWidgets.QPushButton(self.widget)
        self.uiCopyIOUDevicePushButton.setEnabled(False)
        self.uiCopyIOUDevicePushButton.setObjectName("uiCopyIOUDevicePushButton")
        self.horizontalLayout.addWidget(self.uiCopyIOUDevicePushButton)
        self.uiEditIOUDevicePushButton = QtWidgets.QPushButton(self.widget)
        self.uiEditIOUDevicePushButton.setEnabled(False)
        self.uiEditIOUDevicePushButton.setObjectName("uiEditIOUDevicePushButton")
        self.horizontalLayout.addWidget(self.uiEditIOUDevicePushButton)
        self.uiDeleteIOUDevicePushButton = QtWidgets.QPushButton(self.widget)
        self.uiDeleteIOUDevicePushButton.setEnabled(False)
        self.uiDeleteIOUDevicePushButton.setObjectName("uiDeleteIOUDevicePushButton")
        self.horizontalLayout.addWidget(self.uiDeleteIOUDevicePushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(IOUDevicePreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(IOUDevicePreferencesPageWidget)
        IOUDevicePreferencesPageWidget.setTabOrder(self.uiNewIOUDevicePushButton, self.uiDeleteIOUDevicePushButton)

    def retranslateUi(self, IOUDevicePreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        IOUDevicePreferencesPageWidget.setWindowTitle(_translate("IOUDevicePreferencesPageWidget", "IOU Devices"))
        IOUDevicePreferencesPageWidget.setAccessibleName(_translate("IOUDevicePreferencesPageWidget", "IOU device templates"))
        self.uiIOUDeviceInfoTreeWidget.headerItem().setText(0, _translate("IOUDevicePreferencesPageWidget", "1"))
        self.uiIOUDeviceInfoTreeWidget.headerItem().setText(1, _translate("IOUDevicePreferencesPageWidget", "2"))
        self.uiNewIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&New"))
        self.uiCopyIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&Copy"))
        self.uiEditIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&Edit"))
        self.uiDeleteIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&Delete"))

