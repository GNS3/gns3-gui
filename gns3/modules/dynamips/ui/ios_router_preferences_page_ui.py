# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/dynamips/ui/ios_router_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IOSRouterPreferencesPageWidget(object):
    def setupUi(self, IOSRouterPreferencesPageWidget):
        IOSRouterPreferencesPageWidget.setObjectName("IOSRouterPreferencesPageWidget")
        IOSRouterPreferencesPageWidget.resize(700, 511)
        self.gridLayout = QtWidgets.QGridLayout(IOSRouterPreferencesPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.uiIOSRoutersTreeWidget = QtWidgets.QTreeWidget(IOSRouterPreferencesPageWidget)
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
        self.gridLayout.addWidget(self.uiIOSRoutersTreeWidget, 0, 0, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiIOSRouterInfoTreeWidget = QtWidgets.QTreeWidget(IOSRouterPreferencesPageWidget)
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
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiNewIOSRouterPushButton = QtWidgets.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiNewIOSRouterPushButton.setObjectName("uiNewIOSRouterPushButton")
        self.horizontalLayout.addWidget(self.uiNewIOSRouterPushButton)
        self.uiDecompressIOSPushButton = QtWidgets.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiDecompressIOSPushButton.setEnabled(False)
        self.uiDecompressIOSPushButton.setObjectName("uiDecompressIOSPushButton")
        self.horizontalLayout.addWidget(self.uiDecompressIOSPushButton)
        self.uiCopyIOSRouterPushButton = QtWidgets.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiCopyIOSRouterPushButton.setEnabled(False)
        self.uiCopyIOSRouterPushButton.setObjectName("uiCopyIOSRouterPushButton")
        self.horizontalLayout.addWidget(self.uiCopyIOSRouterPushButton)
        self.uiEditIOSRouterPushButton = QtWidgets.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiEditIOSRouterPushButton.setEnabled(False)
        self.uiEditIOSRouterPushButton.setObjectName("uiEditIOSRouterPushButton")
        self.horizontalLayout.addWidget(self.uiEditIOSRouterPushButton)
        self.uiDeleteIOSRouterPushButton = QtWidgets.QPushButton(IOSRouterPreferencesPageWidget)
        self.uiDeleteIOSRouterPushButton.setEnabled(False)
        self.uiDeleteIOSRouterPushButton.setObjectName("uiDeleteIOSRouterPushButton")
        self.horizontalLayout.addWidget(self.uiDeleteIOSRouterPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 1, 1, 1)

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
        self.uiCopyIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Copy"))
        self.uiEditIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Edit"))
        self.uiDeleteIOSRouterPushButton.setText(_translate("IOSRouterPreferencesPageWidget", "&Delete"))

