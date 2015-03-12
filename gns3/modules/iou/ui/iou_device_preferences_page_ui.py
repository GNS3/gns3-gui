# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/iou/ui/iou_device_preferences_page.ui'
#
# Created: Wed Mar 11 22:01:55 2015
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

class Ui_IOUDevicePreferencesPageWidget(object):
    def setupUi(self, IOUDevicePreferencesPageWidget):
        IOUDevicePreferencesPageWidget.setObjectName(_fromUtf8("IOUDevicePreferencesPageWidget"))
        IOUDevicePreferencesPageWidget.resize(506, 508)
        self.gridLayout = QtGui.QGridLayout(IOUDevicePreferencesPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiIOUDevicesTreeWidget = QtGui.QTreeWidget(IOUDevicePreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
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
        self.uiIOUDevicesTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiIOUDevicesTreeWidget.setRootIsDecorated(False)
        self.uiIOUDevicesTreeWidget.setObjectName(_fromUtf8("uiIOUDevicesTreeWidget"))
        self.uiIOUDevicesTreeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.uiIOUDevicesTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiIOUDevicesTreeWidget, 0, 0, 2, 1)
        self.uiIOUDeviceInfoTreeWidget = QtGui.QTreeWidget(IOUDevicePreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOUDeviceInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiIOUDeviceInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiIOUDeviceInfoTreeWidget.setIndentation(10)
        self.uiIOUDeviceInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiIOUDeviceInfoTreeWidget.setObjectName(_fromUtf8("uiIOUDeviceInfoTreeWidget"))
        self.uiIOUDeviceInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiIOUDeviceInfoTreeWidget, 0, 1, 1, 1)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.uiNewIOUDevicePushButton = QtGui.QPushButton(IOUDevicePreferencesPageWidget)
        self.uiNewIOUDevicePushButton.setObjectName(_fromUtf8("uiNewIOUDevicePushButton"))
        self.horizontalLayout_6.addWidget(self.uiNewIOUDevicePushButton)
        self.uiEditIOUDevicePushButton = QtGui.QPushButton(IOUDevicePreferencesPageWidget)
        self.uiEditIOUDevicePushButton.setEnabled(False)
        self.uiEditIOUDevicePushButton.setObjectName(_fromUtf8("uiEditIOUDevicePushButton"))
        self.horizontalLayout_6.addWidget(self.uiEditIOUDevicePushButton)
        self.uiDeleteIOUDevicePushButton = QtGui.QPushButton(IOUDevicePreferencesPageWidget)
        self.uiDeleteIOUDevicePushButton.setEnabled(False)
        self.uiDeleteIOUDevicePushButton.setObjectName(_fromUtf8("uiDeleteIOUDevicePushButton"))
        self.horizontalLayout_6.addWidget(self.uiDeleteIOUDevicePushButton)
        self.gridLayout.addLayout(self.horizontalLayout_6, 1, 1, 1, 1)

        self.retranslateUi(IOUDevicePreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(IOUDevicePreferencesPageWidget)

    def retranslateUi(self, IOUDevicePreferencesPageWidget):
        IOUDevicePreferencesPageWidget.setWindowTitle(_translate("IOUDevicePreferencesPageWidget", "IOU devices", None))
        IOUDevicePreferencesPageWidget.setAccessibleName(_translate("IOUDevicePreferencesPageWidget", "IOU device templates", None))
        self.uiIOUDeviceInfoTreeWidget.headerItem().setText(0, _translate("IOUDevicePreferencesPageWidget", "1", None))
        self.uiIOUDeviceInfoTreeWidget.headerItem().setText(1, _translate("IOUDevicePreferencesPageWidget", "2", None))
        self.uiNewIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&New", None))
        self.uiEditIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&Edit", None))
        self.uiDeleteIOUDevicePushButton.setText(_translate("IOUDevicePreferencesPageWidget", "&Delete", None))

