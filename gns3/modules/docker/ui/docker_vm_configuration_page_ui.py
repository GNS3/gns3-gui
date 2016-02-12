# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/modules/docker/ui/docker_vm_configuration_page.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dockerVMConfigPageWidget(object):
    def setupUi(self, dockerVMConfigPageWidget):
        dockerVMConfigPageWidget.setObjectName("dockerVMConfigPageWidget")
        dockerVMConfigPageWidget.resize(651, 402)
        self.verticalLayout = QtWidgets.QVBoxLayout(dockerVMConfigPageWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTabWidget = QtWidgets.QTabWidget(dockerVMConfigPageWidget)
        self.uiTabWidget.setObjectName("uiTabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.gridLayout = QtWidgets.QGridLayout(self.tab)
        self.gridLayout.setObjectName("gridLayout")
        self.uiDefaultNameFormatLineEdit = QtWidgets.QLineEdit(self.tab)
        self.uiDefaultNameFormatLineEdit.setObjectName("uiDefaultNameFormatLineEdit")
        self.gridLayout.addWidget(self.uiDefaultNameFormatLineEdit, 1, 1, 1, 1)
        self.uiEnvironmentTextEdit = QtWidgets.QTextEdit(self.tab)
        self.uiEnvironmentTextEdit.setObjectName("uiEnvironmentTextEdit")
        self.gridLayout.addWidget(self.uiEnvironmentTextEdit, 5, 1, 1, 1)
        self.uiDefaultNameFormatLabel = QtWidgets.QLabel(self.tab)
        self.uiDefaultNameFormatLabel.setObjectName("uiDefaultNameFormatLabel")
        self.gridLayout.addWidget(self.uiDefaultNameFormatLabel, 1, 0, 1, 1)
        self.uiEnvironmentLabel = QtWidgets.QLabel(self.tab)
        self.uiEnvironmentLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.uiEnvironmentLabel.setWordWrap(False)
        self.uiEnvironmentLabel.setObjectName("uiEnvironmentLabel")
        self.gridLayout.addWidget(self.uiEnvironmentLabel, 5, 0, 1, 1)
        self.uiCMDLineEdit = QtWidgets.QLineEdit(self.tab)
        self.uiCMDLineEdit.setObjectName("uiCMDLineEdit")
        self.gridLayout.addWidget(self.uiCMDLineEdit, 2, 1, 1, 1)
        self.uiCMDLabel = QtWidgets.QLabel(self.tab)
        self.uiCMDLabel.setObjectName("uiCMDLabel")
        self.gridLayout.addWidget(self.uiCMDLabel, 2, 0, 1, 1)
        self.uiAdapterSpinBox = QtWidgets.QSpinBox(self.tab)
        self.uiAdapterSpinBox.setMinimum(1)
        self.uiAdapterSpinBox.setObjectName("uiAdapterSpinBox")
        self.gridLayout.addWidget(self.uiAdapterSpinBox, 3, 1, 1, 1)
        self.uiNameLineEdit = QtWidgets.QLineEdit(self.tab)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 1)
        self.uiNameLabel = QtWidgets.QLabel(self.tab)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiAdapterLabel = QtWidgets.QLabel(self.tab)
        self.uiAdapterLabel.setObjectName("uiAdapterLabel")
        self.gridLayout.addWidget(self.uiAdapterLabel, 3, 0, 1, 1)
        self.uiConsolePortLabel = QtWidgets.QLabel(self.tab)
        self.uiConsolePortLabel.setObjectName("uiConsolePortLabel")
        self.gridLayout.addWidget(self.uiConsolePortLabel, 4, 0, 1, 1)
        self.uiConsolePortSpinBox = QtWidgets.QSpinBox(self.tab)
        self.uiConsolePortSpinBox.setMaximum(65535)
        self.uiConsolePortSpinBox.setObjectName("uiConsolePortSpinBox")
        self.gridLayout.addWidget(self.uiConsolePortSpinBox, 4, 1, 1, 1)
        self.uiTabWidget.addTab(self.tab, "")
        self.verticalLayout.addWidget(self.uiTabWidget)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(dockerVMConfigPageWidget)
        self.uiTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(dockerVMConfigPageWidget)

    def retranslateUi(self, dockerVMConfigPageWidget):
        _translate = QtCore.QCoreApplication.translate
        dockerVMConfigPageWidget.setWindowTitle(_translate("dockerVMConfigPageWidget", "Docker image configuration"))
        self.uiDefaultNameFormatLabel.setText(_translate("dockerVMConfigPageWidget", "Default name format"))
        self.uiEnvironmentLabel.setText(_translate("dockerVMConfigPageWidget", "Environment (KEY=VALUE one by line):"))
        self.uiCMDLabel.setText(_translate("dockerVMConfigPageWidget", "Start command:"))
        self.uiNameLabel.setText(_translate("dockerVMConfigPageWidget", "Name:"))
        self.uiAdapterLabel.setText(_translate("dockerVMConfigPageWidget", "Adapters:"))
        self.uiConsolePortLabel.setText(_translate("dockerVMConfigPageWidget", "Console port:"))
        self.uiTabWidget.setTabText(self.uiTabWidget.indexOf(self.tab), _translate("dockerVMConfigPageWidget", "General settings"))

