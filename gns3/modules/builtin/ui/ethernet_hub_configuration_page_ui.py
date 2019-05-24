# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/builtin/ui/ethernet_hub_configuration_page.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ethernetHubConfigPageWidget(object):
    def setupUi(self, ethernetHubConfigPageWidget):
        ethernetHubConfigPageWidget.setObjectName("ethernetHubConfigPageWidget")
        ethernetHubConfigPageWidget.resize(591, 352)
        self.verticalLayout = QtWidgets.QVBoxLayout(ethernetHubConfigPageWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiSettingsGroupBox = QtWidgets.QGroupBox(ethernetHubConfigPageWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiSettingsGroupBox.sizePolicy().hasHeightForWidth())
        self.uiSettingsGroupBox.setSizePolicy(sizePolicy)
        self.uiSettingsGroupBox.setObjectName("uiSettingsGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.uiSettingsGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.uiNameLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiDefaultNameFormatLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiDefaultNameFormatLabel.setObjectName("uiDefaultNameFormatLabel")
        self.gridLayout.addWidget(self.uiDefaultNameFormatLabel, 1, 0, 1, 2)
        self.uiDefaultNameFormatLineEdit = QtWidgets.QLineEdit(self.uiSettingsGroupBox)
        self.uiDefaultNameFormatLineEdit.setObjectName("uiDefaultNameFormatLineEdit")
        self.gridLayout.addWidget(self.uiDefaultNameFormatLineEdit, 1, 2, 1, 1)
        self.uiSymbolLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiSymbolLabel.setObjectName("uiSymbolLabel")
        self.gridLayout.addWidget(self.uiSymbolLabel, 2, 0, 1, 2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.uiSymbolLineEdit = QtWidgets.QLineEdit(self.uiSettingsGroupBox)
        self.uiSymbolLineEdit.setObjectName("uiSymbolLineEdit")
        self.horizontalLayout_7.addWidget(self.uiSymbolLineEdit)
        self.uiSymbolToolButton = QtWidgets.QToolButton(self.uiSettingsGroupBox)
        self.uiSymbolToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiSymbolToolButton.setObjectName("uiSymbolToolButton")
        self.horizontalLayout_7.addWidget(self.uiSymbolToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_7, 2, 2, 1, 1)
        self.uiCategoryLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiCategoryLabel.setObjectName("uiCategoryLabel")
        self.gridLayout.addWidget(self.uiCategoryLabel, 3, 0, 1, 2)
        self.uiCategoryComboBox = QtWidgets.QComboBox(self.uiSettingsGroupBox)
        self.uiCategoryComboBox.setObjectName("uiCategoryComboBox")
        self.gridLayout.addWidget(self.uiCategoryComboBox, 3, 2, 1, 1)
        self.uiPortsLabel = QtWidgets.QLabel(self.uiSettingsGroupBox)
        self.uiPortsLabel.setObjectName("uiPortsLabel")
        self.gridLayout.addWidget(self.uiPortsLabel, 4, 0, 1, 1)
        self.uiPortsSpinBox = QtWidgets.QSpinBox(self.uiSettingsGroupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiPortsSpinBox.sizePolicy().hasHeightForWidth())
        self.uiPortsSpinBox.setSizePolicy(sizePolicy)
        self.uiPortsSpinBox.setMinimum(0)
        self.uiPortsSpinBox.setMaximum(65535)
        self.uiPortsSpinBox.setProperty("value", 1)
        self.uiPortsSpinBox.setObjectName("uiPortsSpinBox")
        self.gridLayout.addWidget(self.uiPortsSpinBox, 4, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 71, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 2, 1, 1)
        self.uiNameLineEdit = QtWidgets.QLineEdit(self.uiSettingsGroupBox)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 2, 1, 1)
        self.verticalLayout.addWidget(self.uiSettingsGroupBox)

        self.retranslateUi(ethernetHubConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(ethernetHubConfigPageWidget)

    def retranslateUi(self, ethernetHubConfigPageWidget):
        _translate = QtCore.QCoreApplication.translate
        ethernetHubConfigPageWidget.setWindowTitle(_translate("ethernetHubConfigPageWidget", "Ethernet hub template configuration"))
        self.uiSettingsGroupBox.setTitle(_translate("ethernetHubConfigPageWidget", "Settings"))
        self.uiNameLabel.setText(_translate("ethernetHubConfigPageWidget", "Name:"))
        self.uiDefaultNameFormatLabel.setText(_translate("ethernetHubConfigPageWidget", "Default name format:"))
        self.uiSymbolLabel.setText(_translate("ethernetHubConfigPageWidget", "Symbol:"))
        self.uiSymbolToolButton.setText(_translate("ethernetHubConfigPageWidget", "&Browse..."))
        self.uiCategoryLabel.setText(_translate("ethernetHubConfigPageWidget", "Category:"))
        self.uiPortsLabel.setText(_translate("ethernetHubConfigPageWidget", "Number of ports:"))

