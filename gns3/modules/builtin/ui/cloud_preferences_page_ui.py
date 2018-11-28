# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/builtin/ui/cloud_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CloudPreferencesPageWidget(object):
    def setupUi(self, CloudPreferencesPageWidget):
        CloudPreferencesPageWidget.setObjectName("CloudPreferencesPageWidget")
        CloudPreferencesPageWidget.resize(546, 455)
        CloudPreferencesPageWidget.setAccessibleDescription("")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(CloudPreferencesPageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(CloudPreferencesPageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiCloudNodesTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCloudNodesTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiCloudNodesTreeWidget.setSizePolicy(sizePolicy)
        self.uiCloudNodesTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiCloudNodesTreeWidget.setFont(font)
        self.uiCloudNodesTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiCloudNodesTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiCloudNodesTreeWidget.setRootIsDecorated(False)
        self.uiCloudNodesTreeWidget.setObjectName("uiCloudNodesTreeWidget")
        self.uiCloudNodesTreeWidget.headerItem().setText(0, "1")
        self.uiCloudNodesTreeWidget.header().setVisible(False)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiCloudNodeInfoTreeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCloudNodeInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiCloudNodeInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiCloudNodeInfoTreeWidget.setIndentation(10)
        self.uiCloudNodeInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiCloudNodeInfoTreeWidget.setObjectName("uiCloudNodeInfoTreeWidget")
        self.uiCloudNodeInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiCloudNodeInfoTreeWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewCloudNodePushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiNewCloudNodePushButton.setObjectName("uiNewCloudNodePushButton")
        self.horizontalLayout_5.addWidget(self.uiNewCloudNodePushButton)
        self.uiEditCloudNodePushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiEditCloudNodePushButton.setEnabled(False)
        self.uiEditCloudNodePushButton.setObjectName("uiEditCloudNodePushButton")
        self.horizontalLayout_5.addWidget(self.uiEditCloudNodePushButton)
        self.uiDeleteCloudNodePushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDeleteCloudNodePushButton.setEnabled(False)
        self.uiDeleteCloudNodePushButton.setObjectName("uiDeleteCloudNodePushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteCloudNodePushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(CloudPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(CloudPreferencesPageWidget)
        CloudPreferencesPageWidget.setTabOrder(self.uiNewCloudNodePushButton, self.uiDeleteCloudNodePushButton)

    def retranslateUi(self, CloudPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        CloudPreferencesPageWidget.setWindowTitle(_translate("CloudPreferencesPageWidget", "Cloud nodes"))
        CloudPreferencesPageWidget.setAccessibleName(_translate("CloudPreferencesPageWidget", "Cloud node templates"))
        self.uiCloudNodeInfoTreeWidget.headerItem().setText(0, _translate("CloudPreferencesPageWidget", "1"))
        self.uiCloudNodeInfoTreeWidget.headerItem().setText(1, _translate("CloudPreferencesPageWidget", "2"))
        self.uiNewCloudNodePushButton.setText(_translate("CloudPreferencesPageWidget", "&New"))
        self.uiEditCloudNodePushButton.setText(_translate("CloudPreferencesPageWidget", "&Edit"))
        self.uiDeleteCloudNodePushButton.setText(_translate("CloudPreferencesPageWidget", "&Delete"))

