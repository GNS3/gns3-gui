# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/symbol_selection_dialog.ui'
#
# Created: Wed Jul 15 12:22:31 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SymbolSelectionDialog(object):
    def setupUi(self, SymbolSelectionDialog):
        SymbolSelectionDialog.setObjectName("SymbolSelectionDialog")
        SymbolSelectionDialog.resize(356, 466)
        SymbolSelectionDialog.setModal(True)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(SymbolSelectionDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(SymbolSelectionDialog)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.uiSymbolLabel = QtWidgets.QLabel(self.groupBox)
        self.uiSymbolLabel.setObjectName("uiSymbolLabel")
        self.gridLayout.addWidget(self.uiSymbolLabel, 0, 0, 1, 1)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.uiSymbolLineEdit = QtWidgets.QLineEdit(self.groupBox)
        self.uiSymbolLineEdit.setObjectName("uiSymbolLineEdit")
        self.horizontalLayout_7.addWidget(self.uiSymbolLineEdit)
        self.uiSymbolToolButton = QtWidgets.QToolButton(self.groupBox)
        self.uiSymbolToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiSymbolToolButton.setObjectName("uiSymbolToolButton")
        self.horizontalLayout_7.addWidget(self.uiSymbolToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_7, 0, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.uiBuiltInGroupBox = QtWidgets.QGroupBox(SymbolSelectionDialog)
        self.uiBuiltInGroupBox.setObjectName("uiBuiltInGroupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.uiBuiltInGroupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiSymbolListWidget = QtWidgets.QListWidget(self.uiBuiltInGroupBox)
        self.uiSymbolListWidget.setMinimumSize(QtCore.QSize(0, 300))
        self.uiSymbolListWidget.setObjectName("uiSymbolListWidget")
        self.verticalLayout.addWidget(self.uiSymbolListWidget)
        self.verticalLayout_2.addWidget(self.uiBuiltInGroupBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(SymbolSelectionDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.horizontalLayout.addWidget(self.uiButtonBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 34, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)

        self.retranslateUi(SymbolSelectionDialog)
        self.uiButtonBox.accepted.connect(SymbolSelectionDialog.accept)
        self.uiButtonBox.rejected.connect(SymbolSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SymbolSelectionDialog)

    def retranslateUi(self, SymbolSelectionDialog):
        _translate = QtCore.QCoreApplication.translate
        SymbolSelectionDialog.setWindowTitle(_translate("SymbolSelectionDialog", "Symbol selection"))
        self.groupBox.setTitle(_translate("SymbolSelectionDialog", "Custom symbol"))
        self.uiSymbolLabel.setText(_translate("SymbolSelectionDialog", "Path:"))
        self.uiSymbolToolButton.setText(_translate("SymbolSelectionDialog", "&Browse..."))
        self.uiBuiltInGroupBox.setTitle(_translate("SymbolSelectionDialog", "Built-in symbols"))

from . import resources_rc
