# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/custom_adapters_configuration_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CustomAdaptersConfigurationDialog(object):
    def setupUi(self, CustomAdaptersConfigurationDialog):
        CustomAdaptersConfigurationDialog.setObjectName("CustomAdaptersConfigurationDialog")
        CustomAdaptersConfigurationDialog.resize(718, 450)
        CustomAdaptersConfigurationDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(CustomAdaptersConfigurationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiAdaptersTreeWidget = QtWidgets.QTreeWidget(CustomAdaptersConfigurationDialog)
        self.uiAdaptersTreeWidget.setObjectName("uiAdaptersTreeWidget")
        self.verticalLayout.addWidget(self.uiAdaptersTreeWidget)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(CustomAdaptersConfigurationDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Reset)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.verticalLayout.addWidget(self.uiButtonBox)

        self.retranslateUi(CustomAdaptersConfigurationDialog)
        self.uiButtonBox.accepted.connect(CustomAdaptersConfigurationDialog.accept)
        self.uiButtonBox.rejected.connect(CustomAdaptersConfigurationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CustomAdaptersConfigurationDialog)

    def retranslateUi(self, CustomAdaptersConfigurationDialog):
        _translate = QtCore.QCoreApplication.translate
        CustomAdaptersConfigurationDialog.setWindowTitle(_translate("CustomAdaptersConfigurationDialog", "Custom adapters configuration"))
        self.uiAdaptersTreeWidget.headerItem().setText(0, _translate("CustomAdaptersConfigurationDialog", "Adapter number"))
        self.uiAdaptersTreeWidget.headerItem().setText(1, _translate("CustomAdaptersConfigurationDialog", "Port name"))

from . import resources_rc
