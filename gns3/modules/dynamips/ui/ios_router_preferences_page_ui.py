# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/dynamips/ui/ios_router_preferences_page.ui'
#
# Created: Wed Mar 11 22:03:56 2015
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

class Ui_IOSRouterPreferencesPageWidget(object):
    def setupUi(self, IOSRouterPreferencesPageWidget):
        IOSRouterPreferencesPageWidget.setObjectName(_fromUtf8("IOSRouterPreferencesPageWidget"))
        IOSRouterPreferencesPageWidget.resize(560, 518)
        self.gridLayout = QtGui.QGridLayout(IOSRouterPreferencesPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiIOSRoutersTreeWidget = QtGui.QTreeWidget(IOSRouterPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOSRoutersTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiIOSRoutersTreeWidget.setSizePolicy(sizePolicy)
        self.uiIOSRoutersTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiIOSRoutersTreeWidget.setFont(font)
        self.uiIOSRoutersTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiIOSRoutersTreeWidget.setRootIsDecorated(False)
        self.uiIOSRoutersTreeWidget.setObjectName(_fromUtf8("uiIOSRoutersTreeWidget"))
        self.uiIOSRoutersTreeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.uiIOSRoutersTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiIOSRoutersTreeWidget, 0, 0, 2, 1)
        self.uiIOSRouterInfoTreeWidget = QtGui.QTreeWidget(IOSRouterPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOSRouterInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiIOSRouterInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiIOSRouterInfoTreeWidget.setIndentation(10)
        self.uiIOSRouterInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiIOSRouterInfoTreeWidget.setObjectName(_fromUtf8("uiIOSRouterInfoTreeWidget"))
        self.uiIOSRouterInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiIOSRouterInfoTreeWidget, 0, 1, 1, 1)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.uiNewIOSRouterPushButton = QtGui.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiNewIOSRouterPushButton.setObjectName(_fromUtf8("uiNewIOSRouterPushButton"))
        self.horizontalLayout_6.addWidget(self.uiNewIOSRouterPushButton)
        self.uiDecompressIOSPushButton = QtGui.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiDecompressIOSPushButton.setEnabled(False)
        self.uiDecompressIOSPushButton.setObjectName(_fromUtf8("uiDecompressIOSPushButton"))
        self.horizontalLayout_6.addWidget(self.uiDecompressIOSPushButton)
        self.uiEditIOSRouterPushButton = QtGui.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiEditIOSRouterPushButton.setEnabled(False)
        self.uiEditIOSRouterPushButton.setObjectName(_fromUtf8("uiEditIOSRouterPushButton"))
        self.horizontalLayout_6.addWidget(self.uiEditIOSRouterPushButton)
        self.uiDeleteIOSRouterPushButton = QtGui.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiDeleteIOSRouterPushButton.setEnabled(False)
        self.uiDeleteIOSRouterPushButton.setObjectName(_fromUtf8("uiDeleteIOSRouterPushButton"))
        self.horizontalLayout_6.addWidget(self.uiDeleteIOSRouterPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_6, 1, 1, 1, 1)

        self.retranslateUi(IOSRouterPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(IOSRouterPreferencesPageWidget)

    def retranslateUi(self, IOSRouterPreferencesPageWidget):
        IOSRouterPreferencesPageWidget.setWindowTitle(_translate("IOSRouterPreferencesPageWidget", "IOS routers", None))
        IOSRouterPreferencesPageWidget.setAccessibleName(_translate("IOSRouterPreferencesPageWidget", "IOS router templates", None))
        self.uiIOSRouterInfoTreeWidget.headerItem().setText(0, _translate("IOSRouterPreferencesPageWidget", "1", None))
        self.uiIOSRouterInfoTreeWidget.headerItem().setText(1, _translate("IOSRouterPreferencesPageWidget", "2", None))
        self.uiNewIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&New", None))
        self.uiDecompressIOSPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Decompress", None))
        self.uiEditIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Edit", None))
        self.uiDeleteIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Delete", None))

