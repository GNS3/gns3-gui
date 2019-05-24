# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/builtin/ui/ethernet_hub_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EthernetHubPreferencesPageWidget(object):
    def setupUi(self, EthernetHubPreferencesPageWidget):
        EthernetHubPreferencesPageWidget.setObjectName("EthernetHubPreferencesPageWidget")
        EthernetHubPreferencesPageWidget.resize(546, 455)
        EthernetHubPreferencesPageWidget.setAccessibleDescription("")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(EthernetHubPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(EthernetHubPreferencesPageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiEthernetHubsTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiEthernetHubsTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiEthernetHubsTreeWidget.setSizePolicy(sizePolicy)
        self.uiEthernetHubsTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiEthernetHubsTreeWidget.setFont(font)
        self.uiEthernetHubsTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiEthernetHubsTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiEthernetHubsTreeWidget.setRootIsDecorated(False)
        self.uiEthernetHubsTreeWidget.setObjectName("uiEthernetHubsTreeWidget")
        self.uiEthernetHubsTreeWidget.headerItem().setText(0, "1")
        self.uiEthernetHubsTreeWidget.header().setVisible(False)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiEthernetHubInfoTreeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiEthernetHubInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiEthernetHubInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiEthernetHubInfoTreeWidget.setIndentation(10)
        self.uiEthernetHubInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiEthernetHubInfoTreeWidget.setObjectName("uiEthernetHubInfoTreeWidget")
        self.uiEthernetHubInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiEthernetHubInfoTreeWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewEthernetHubPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiNewEthernetHubPushButton.setObjectName("uiNewEthernetHubPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewEthernetHubPushButton)
        self.uiEditEthernetHubPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiEditEthernetHubPushButton.setEnabled(False)
        self.uiEditEthernetHubPushButton.setObjectName("uiEditEthernetHubPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditEthernetHubPushButton)
        self.uiDeleteEthernetHubPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDeleteEthernetHubPushButton.setEnabled(False)
        self.uiDeleteEthernetHubPushButton.setObjectName("uiDeleteEthernetHubPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteEthernetHubPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(EthernetHubPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(EthernetHubPreferencesPageWidget)
        EthernetHubPreferencesPageWidget.setTabOrder(self.uiNewEthernetHubPushButton, self.uiDeleteEthernetHubPushButton)

    def retranslateUi(self, EthernetHubPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        EthernetHubPreferencesPageWidget.setWindowTitle(_translate("EthernetHubPreferencesPageWidget", "Ethernet hubs"))
        EthernetHubPreferencesPageWidget.setAccessibleName(_translate("EthernetHubPreferencesPageWidget", "Ethernet hub templates"))
        self.uiEthernetHubInfoTreeWidget.headerItem().setText(0, _translate("EthernetHubPreferencesPageWidget", "1"))
        self.uiEthernetHubInfoTreeWidget.headerItem().setText(1, _translate("EthernetHubPreferencesPageWidget", "2"))
        self.uiNewEthernetHubPushButton.setText(_translate("EthernetHubPreferencesPageWidget", "&New"))
        self.uiEditEthernetHubPushButton.setText(_translate("EthernetHubPreferencesPageWidget", "&Edit"))
        self.uiDeleteEthernetHubPushButton.setText(_translate("EthernetHubPreferencesPageWidget", "&Delete"))

