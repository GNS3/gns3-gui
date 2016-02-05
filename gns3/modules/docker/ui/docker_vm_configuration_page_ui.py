# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/docker/ui/docker_vm_configuration_page.ui'
#
# Created: Fri Feb  5 11:58:01 2016
#      by: PyQt5 UI code generator 5.2.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dockerVMConfigPageWidget(object):
    def setupUi(self, dockerVMConfigPageWidget):
        dockerVMConfigPageWidget.setObjectName("dockerVMConfigPageWidget")
        dockerVMConfigPageWidget.resize(509, 346)
        self.verticalLayout = QtWidgets.QVBoxLayout(dockerVMConfigPageWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTabWidget = QtWidgets.QTabWidget(dockerVMConfigPageWidget)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.uiCMDLabel = QtWidgets.QLabel(self.tab)
        self.uiCMDLabel.setObjectName("uiCMDLabel")
        self.gridLayout.addWidget(self.uiCMDLabel, 2, 0, 1, 1)
        self.uiCMDLineEdit = QtWidgets.QLineEdit(self.tab)
        self.uiCMDLineEdit.setObjectName("uiCMDLineEdit")
        self.gridLayout.addWidget(self.uiCMDLineEdit, 2, 1, 1, 1)
        self.uiImageListLabel = QtWidgets.QLabel(self.tab)
        self.uiImageListLabel.setObjectName("uiImageListLabel")
        self.gridLayout.addWidget(self.uiImageListLabel, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.uiImageListComboBox = QtWidgets.QComboBox(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiImageListComboBox.sizePolicy().hasHeightForWidth())
        self.uiImageListComboBox.setSizePolicy(sizePolicy)
        self.uiImageListComboBox.setObjectName("uiImageListComboBox")
        self.gridLayout.addWidget(self.uiImageListComboBox, 3, 1, 1, 1)
        self.uiNameLabel = QtWidgets.QLabel(self.tab)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtWidgets.QLineEdit(self.tab)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiDefaultNameFormatLabel = QtWidgets.QLabel(self.tab)
        self.uiDefaultNameFormatLabel.setObjectName("uiDefaultNameFormatLabel")
        self.gridLayout.addWidget(self.uiDefaultNameFormatLabel, 1, 0, 1, 1)
        self.uiDefaultNameFormatLineEdit = QtWidgets.QLineEdit(self.tab)
        self.uiDefaultNameFormatLineEdit.setObjectName("uiDefaultNameFormatLineEdit")
        self.gridLayout.addWidget(self.uiDefaultNameFormatLineEdit, 1, 1, 1, 1)
        self.uiTabWidget.addTab(self.tab, "")
        self.verticalLayout.addWidget(self.uiTabWidget)

        self.retranslateUi(dockerVMConfigPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(dockerVMConfigPageWidget)

    def retranslateUi(self, dockerVMConfigPageWidget):
        _translate = QtCore.QCoreApplication.translate
        dockerVMConfigPageWidget.setWindowTitle(_translate("dockerVMConfigPageWidget", "Docker image configuration"))
        self.uiCMDLabel.setText(_translate("dockerVMConfigPageWidget", "CMD:"))
        self.uiImageListLabel.setText(_translate("dockerVMConfigPageWidget", "Image name:"))
        self.uiNameLabel.setText(_translate("dockerVMConfigPageWidget", "Name:"))
        self.uiDefaultNameFormatLabel.setText(_translate("dockerVMConfigPageWidget", "Default name format:"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.tab), _translate("dockerVMConfigPageWidget", "General settings"))

