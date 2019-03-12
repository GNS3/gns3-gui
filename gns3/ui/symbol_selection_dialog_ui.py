# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/symbol_selection_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SymbolSelectionDialog(object):
    def setupUi(self, SymbolSelectionDialog):
        SymbolSelectionDialog.setObjectName("SymbolSelectionDialog")
        SymbolSelectionDialog.resize(610, 700)
        SymbolSelectionDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(SymbolSelectionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.uiCustomSymbolRadioButton = QtWidgets.QRadioButton(SymbolSelectionDialog)
        self.uiCustomSymbolRadioButton.setChecked(True)
        self.uiCustomSymbolRadioButton.setObjectName("uiCustomSymbolRadioButton")
        self.horizontalLayout_2.addWidget(self.uiCustomSymbolRadioButton)
        self.uiBuiltInSymbolRadioButton = QtWidgets.QRadioButton(SymbolSelectionDialog)
        self.uiBuiltInSymbolRadioButton.setObjectName("uiBuiltInSymbolRadioButton")
        self.horizontalLayout_2.addWidget(self.uiBuiltInSymbolRadioButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.uiCustomSymbolGroupBox = QtWidgets.QGroupBox(SymbolSelectionDialog)
        self.uiCustomSymbolGroupBox.setObjectName("uiCustomSymbolGroupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.uiCustomSymbolGroupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.uiSymbolToolButton = QtWidgets.QToolButton(self.uiCustomSymbolGroupBox)
        self.uiSymbolToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiSymbolToolButton.setObjectName("uiSymbolToolButton")
        self.gridLayout.addWidget(self.uiSymbolToolButton, 0, 2, 1, 1)
        self.uiSymbolLineEdit = QtWidgets.QLineEdit(self.uiCustomSymbolGroupBox)
        self.uiSymbolLineEdit.setObjectName("uiSymbolLineEdit")
        self.gridLayout.addWidget(self.uiSymbolLineEdit, 0, 1, 1, 1)
        self.uiSymbolLabel = QtWidgets.QLabel(self.uiCustomSymbolGroupBox)
        self.uiSymbolLabel.setObjectName("uiSymbolLabel")
        self.gridLayout.addWidget(self.uiSymbolLabel, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.uiCustomSymbolGroupBox)
        self.uiBuiltInGroupBox = QtWidgets.QGroupBox(SymbolSelectionDialog)
        self.uiBuiltInGroupBox.setObjectName("uiBuiltInGroupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.uiBuiltInGroupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.uiSymbolTreeWidget = QtWidgets.QTreeWidget(self.uiBuiltInGroupBox)
        self.uiSymbolTreeWidget.setMinimumSize(QtCore.QSize(0, 300))
        self.uiSymbolTreeWidget.setIndentation(10)
        self.uiSymbolTreeWidget.setObjectName("uiSymbolTreeWidget")
        self.uiSymbolTreeWidget.headerItem().setText(0, "1")
        self.uiSymbolTreeWidget.header().setVisible(False)
        self.gridLayout_2.addWidget(self.uiSymbolTreeWidget, 1, 0, 1, 2)
        self.uiSearchLineEdit = QtWidgets.QLineEdit(self.uiBuiltInGroupBox)
        self.uiSearchLineEdit.setObjectName("uiSearchLineEdit")
        self.gridLayout_2.addWidget(self.uiSearchLineEdit, 0, 1, 1, 1)
        self.uiSearchLabel = QtWidgets.QLabel(self.uiBuiltInGroupBox)
        self.uiSearchLabel.setObjectName("uiSearchLabel")
        self.gridLayout_2.addWidget(self.uiSearchLabel, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.uiBuiltInGroupBox)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(SymbolSelectionDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.horizontalLayout.addWidget(self.uiButtonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.uiBuiltInGroupBox.raise_()
        self.uiCustomSymbolGroupBox.raise_()

        self.retranslateUi(SymbolSelectionDialog)
        self.uiButtonBox.accepted.connect(SymbolSelectionDialog.accept)
        self.uiButtonBox.rejected.connect(SymbolSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SymbolSelectionDialog)

    def retranslateUi(self, SymbolSelectionDialog):
        _translate = QtCore.QCoreApplication.translate
        SymbolSelectionDialog.setWindowTitle(_translate("SymbolSelectionDialog", "Symbol selection"))
        self.uiCustomSymbolRadioButton.setText(_translate("SymbolSelectionDialog", "Use a custom symbol"))
        self.uiBuiltInSymbolRadioButton.setText(_translate("SymbolSelectionDialog", "Symbols library"))
        self.uiCustomSymbolGroupBox.setTitle(_translate("SymbolSelectionDialog", "Custom symbol"))
        self.uiSymbolToolButton.setText(_translate("SymbolSelectionDialog", "&Browse..."))
        self.uiSymbolLabel.setText(_translate("SymbolSelectionDialog", "Path:"))
        self.uiBuiltInGroupBox.setTitle(_translate("SymbolSelectionDialog", "Symbols"))
        self.uiSearchLabel.setText(_translate("SymbolSelectionDialog", "Filter:"))

from . import resources_rc
