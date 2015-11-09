# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/docker/ui/docker_vm_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DockerVMPreferencesPageWidget(object):

    def setupUi(self, DockerVMPreferencesPageWidget):
        DockerVMPreferencesPageWidget.setObjectName("DockerVMPreferencesPageWidget")
        DockerVMPreferencesPageWidget.resize(505, 350)
        DockerVMPreferencesPageWidget.setAccessibleDescription("")
        self.gridLayout = QtWidgets.QGridLayout(DockerVMPreferencesPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewDockerVMPushButton = QtWidgets.QPushButton(DockerVMPreferencesPageWidget)
        self.uiNewDockerVMPushButton.setObjectName("uiNewDockerVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewDockerVMPushButton)
        self.uiEditDockerVMPushButton = QtWidgets.QPushButton(DockerVMPreferencesPageWidget)
        self.uiEditDockerVMPushButton.setEnabled(False)
        self.uiEditDockerVMPushButton.setObjectName("uiEditDockerVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditDockerVMPushButton)
        self.uiDeleteDockerVMPushButton = QtWidgets.QPushButton(DockerVMPreferencesPageWidget)
        self.uiDeleteDockerVMPushButton.setEnabled(False)
        self.uiDeleteDockerVMPushButton.setObjectName("uiDeleteDockerVMPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteDockerVMPushButton)
        self.gridLayout.addLayout(self.horizontalLayout_5, 1, 1, 1, 1)
        self.uiDockerVMInfoTreeWidget = QtWidgets.QTreeWidget(DockerVMPreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiDockerVMInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiDockerVMInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiDockerVMInfoTreeWidget.setIndentation(10)
        self.uiDockerVMInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiDockerVMInfoTreeWidget.setObjectName("uiDockerVMInfoTreeWidget")
        self.uiDockerVMInfoTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiDockerVMInfoTreeWidget, 0, 1, 1, 1)
        self.uiDockerVMsTreeWidget = QtWidgets.QTreeWidget(DockerVMPreferencesPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiDockerVMsTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiDockerVMsTreeWidget.setSizePolicy(sizePolicy)
        self.uiDockerVMsTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiDockerVMsTreeWidget.setFont(font)
        self.uiDockerVMsTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiDockerVMsTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiDockerVMsTreeWidget.setRootIsDecorated(False)
        self.uiDockerVMsTreeWidget.setObjectName("uiDockerVMsTreeWidget")
        self.uiDockerVMsTreeWidget.headerItem().setText(0, "1")
        self.uiDockerVMsTreeWidget.header().setVisible(False)
        self.gridLayout.addWidget(self.uiDockerVMsTreeWidget, 0, 0, 2, 1)

        self.retranslateUi(DockerVMPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(DockerVMPreferencesPageWidget)
        DockerVMPreferencesPageWidget.setTabOrder(self.uiNewDockerVMPushButton, self.uiDeleteDockerVMPushButton)

    def retranslateUi(self, DockerVMPreferencesPageWidget):
        _translate = QtCore.QCoreApplication.translate
        DockerVMPreferencesPageWidget.setWindowTitle(_translate("DockerVMPreferencesPageWidget", "Docker Containers"))
        DockerVMPreferencesPageWidget.setAccessibleName(_translate("DockerVMPreferencesPageWidget", "Docker VM templates"))
        self.uiNewDockerVMPushButton.setText(_translate("DockerVMPreferencesPageWidget", "&New"))
        self.uiEditDockerVMPushButton.setText(_translate("DockerVMPreferencesPageWidget", "&Edit"))
        self.uiDeleteDockerVMPushButton.setText(_translate("DockerVMPreferencesPageWidget", "&Delete"))
        self.uiDockerVMInfoTreeWidget.headerItem().setText(0, _translate("DockerVMPreferencesPageWidget", "1"))
        self.uiDockerVMInfoTreeWidget.headerItem().setText(1, _translate("DockerVMPreferencesPageWidget", "2"))
