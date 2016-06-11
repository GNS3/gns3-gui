# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/builtin/ui/ethernet_switch_preferences_page.ui'
#
# Created: Fri Jun 10 17:15:20 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EthernetSwitchPreferencesPageWidget(object):
    def setupUi(self, EthernetSwitchPreferencesPageWidget):
        EthernetSwitchPreferencesPageWidget.setObjectName("EthernetSwitchPreferencesPageWidget")
        EthernetSwitchPreferencesPageWidget.resize(546, 455)
        EthernetSwitchPreferencesPageWidget.setAccessibleDescription("")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(EthernetSwitchPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(EthernetSwitchPreferencesPageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiEthernetSwitchesTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiEthernetSwitchesTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiEthernetSwitchesTreeWidget.setSizePolicy(sizePolicy)
        self.uiEthernetSwitchesTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiEthernetSwitchesTreeWidget.setFont(font)
        self.uiEthernetSwitchesTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiEthernetSwitchesTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiEthernetSwitchesTreeWidget.setRootIsDecorated(False)
        self.uiEthernetSwitchesTreeWidget.setObjectName("uiEthernetSwitchesTreeWidget")
        self.uiEthernetSwitchesTreeWidget.headerItem().setText(0, "1")
        self.uiEthernetSwitchesTreeWidget.header().setVisible(False)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiEthernetSwitchInfoTreeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiEthernetSwitchInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiEthernetSwitchInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiEthernetSwitchInfoTreeWidget.setIndentation(10)
        self.uiEthernetSwitchInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiEthernetSwitchInfoTreeWidget.setObjectName("uiEthernetSwitchInfoTreeWidget")
        self.uiEthernetSwitchInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiEthernetSwitchInfoTreeWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewEthernetSwitchPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiNewEthernetSwitchPushButton.setObjectName("uiNewEthernetSwitchPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewEthernetSwitchPushButton)
        self.uiEditEthernetSwitchPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiEditEthernetSwitchPushButton.setEnabled(False)
        self.uiEditEthernetSwitchPushButton.setObjectName("uiEditEthernetSwitchPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditEthernetSwitchPushButton)
        self.uiDeleteEthernetSwitchPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDeleteEthernetSwitchPushButton.setEnabled(False)
        self.uiDeleteEthernetSwitchPushButton.setObjectName("uiDeleteEthernetSwitchPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteEthernetSwitchPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(EthernetSwitchPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(EthernetSwitchPreferencesPageWidget)
        EthernetSwitchPreferencesPageWidget.setTabOrder(self.uiNewEthernetSwitchPushButton, self.uiDeleteEthernetSwitchPushButton)

    def retranslateUi(self, EthernetSwitchPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        EthernetSwitchPreferencesPageWidget.setWindowTitle(_translate("EthernetSwitchPreferencesPageWidget", "Ethernet switches"))
        EthernetSwitchPreferencesPageWidget.setAccessibleName(_translate("EthernetSwitchPreferencesPageWidget", "Ethernet switch templates"))
        self.uiEthernetSwitchInfoTreeWidget.headerItem().setText(0, _translate("EthernetSwitchPreferencesPageWidget", "1"))
        self.uiEthernetSwitchInfoTreeWidget.headerItem().setText(1, _translate("EthernetSwitchPreferencesPageWidget", "2"))
        self.uiNewEthernetSwitchPushButton.setText(_translate("EthernetSwitchPreferencesPageWidget", "&New"))
        self.uiEditEthernetSwitchPushButton.setText(_translate("EthernetSwitchPreferencesPageWidget", "&Edit"))
        self.uiDeleteEthernetSwitchPushButton.setText(_translate("EthernetSwitchPreferencesPageWidget", "&Delete"))

