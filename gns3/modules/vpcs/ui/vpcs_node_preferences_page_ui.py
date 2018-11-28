# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/vpcs/ui/vpcs_node_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VPCSNodePageWidget(object):
    def setupUi(self, VPCSNodePageWidget):
        VPCSNodePageWidget.setObjectName("VPCSNodePageWidget")
        VPCSNodePageWidget.resize(546, 455)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(VPCSNodePageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(VPCSNodePageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiVPCSTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVPCSTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVPCSTreeWidget.setSizePolicy(sizePolicy)
        self.uiVPCSTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiVPCSTreeWidget.setFont(font)
        self.uiVPCSTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiVPCSTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiVPCSTreeWidget.setRootIsDecorated(False)
        self.uiVPCSTreeWidget.setObjectName("uiVPCSTreeWidget")
        self.uiVPCSTreeWidget.headerItem().setText(0, "1")
        self.uiVPCSTreeWidget.header().setVisible(False)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiVPCSInfoTreeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiVPCSInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiVPCSInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiVPCSInfoTreeWidget.setIndentation(10)
        self.uiVPCSInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiVPCSInfoTreeWidget.setObjectName("uiVPCSInfoTreeWidget")
        self.uiVPCSInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiVPCSInfoTreeWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewVPCSPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiNewVPCSPushButton.setObjectName("uiNewVPCSPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewVPCSPushButton)
        self.uiEditVPCSPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiEditVPCSPushButton.setEnabled(False)
        self.uiEditVPCSPushButton.setObjectName("uiEditVPCSPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditVPCSPushButton)
        self.uiDeleteVPCSPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDeleteVPCSPushButton.setEnabled(False)
        self.uiDeleteVPCSPushButton.setObjectName("uiDeleteVPCSPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteVPCSPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(VPCSNodePageWidget)
        QtCore.QMetaObject.connectSlotsByName(VPCSNodePageWidget)
        VPCSNodePageWidget.setTabOrder(self.uiNewVPCSPushButton, self.uiDeleteVPCSPushButton)

    def retranslateUi(self, VPCSNodePageWidget):
        _translate = QtCore.QCoreApplication.translate
        VPCSNodePageWidget.setWindowTitle(_translate("VPCSNodePageWidget", "VPCS nodes"))
        VPCSNodePageWidget.setAccessibleName(_translate("VPCSNodePageWidget", "VPCS node templates"))
        self.uiVPCSInfoTreeWidget.headerItem().setText(0, _translate("VPCSNodePageWidget", "1"))
        self.uiVPCSInfoTreeWidget.headerItem().setText(1, _translate("VPCSNodePageWidget", "2"))
        self.uiNewVPCSPushButton.setText(_translate("VPCSNodePageWidget", "&New"))
        self.uiEditVPCSPushButton.setText(_translate("VPCSNodePageWidget", "&Edit"))
        self.uiDeleteVPCSPushButton.setText(_translate("VPCSNodePageWidget", "&Delete"))

