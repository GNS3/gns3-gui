# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/dynamips/ui/ios_router_preferences_page.ui'
#
# Created: Thu May  5 09:39:07 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IOSRouterPreferencesPageWidget(object):
    def setupUi(self, IOSRouterPreferencesPageWidget):
        IOSRouterPreferencesPageWidget.setObjectName("IOSRouterPreferencesPageWidget")
        IOSRouterPreferencesPageWidget.resize(575, 508)
        self.horizontalLayout = QtWidgets.QHBoxLayout(IOSRouterPreferencesPageWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(IOSRouterPreferencesPageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiIOSRoutersTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
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
        self.uiIOSRoutersTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiIOSRoutersTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiIOSRoutersTreeWidget.setRootIsDecorated(False)
        self.uiIOSRoutersTreeWidget.setObjectName("uiIOSRoutersTreeWidget")
        self.uiIOSRoutersTreeWidget.headerItem().setText(0, "1")
        self.uiIOSRoutersTreeWidget.header().setVisible(False)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiIOSRouterInfoTreeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiIOSRouterInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiIOSRouterInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiIOSRouterInfoTreeWidget.setIndentation(10)
        self.uiIOSRouterInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiIOSRouterInfoTreeWidget.setObjectName("uiIOSRouterInfoTreeWidget")
        self.uiIOSRouterInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiIOSRouterInfoTreeWidget)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.uiNewIOSRouterPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiNewIOSRouterPushButton.setObjectName("uiNewIOSRouterPushButton")
        self.horizontalLayout_6.addWidget(self.uiNewIOSRouterPushButton)
        self.uiDecompressIOSPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDecompressIOSPushButton.setEnabled(False)
        self.uiDecompressIOSPushButton.setObjectName("uiDecompressIOSPushButton")
        self.horizontalLayout_6.addWidget(self.uiDecompressIOSPushButton)
        self.uiEditIOSRouterPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiEditIOSRouterPushButton.setEnabled(False)
        self.uiEditIOSRouterPushButton.setObjectName("uiEditIOSRouterPushButton")
        self.horizontalLayout_6.addWidget(self.uiEditIOSRouterPushButton)
        self.uiDeleteIOSRouterPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDeleteIOSRouterPushButton.setEnabled(False)
        self.uiDeleteIOSRouterPushButton.setObjectName("uiDeleteIOSRouterPushButton")
        self.horizontalLayout_6.addWidget(self.uiDeleteIOSRouterPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout.addWidget(self.splitter)

        self.retranslateUi(IOSRouterPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(IOSRouterPreferencesPageWidget)

    def retranslateUi(self, IOSRouterPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        IOSRouterPreferencesPageWidget.setWindowTitle(_translate("IOSRouterPreferencesPageWidget", "IOS routers"))
        IOSRouterPreferencesPageWidget.setAccessibleName(_translate("IOSRouterPreferencesPageWidget", "IOS router templates"))
        self.uiIOSRouterInfoTreeWidget.headerItem().setText(0, _translate("IOSRouterPreferencesPageWidget", "1"))
        self.uiIOSRouterInfoTreeWidget.headerItem().setText(1, _translate("IOSRouterPreferencesPageWidget", "2"))
        self.uiNewIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&New"))
        self.uiDecompressIOSPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Decompress"))
        self.uiEditIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Edit"))
        self.uiDeleteIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Delete"))

