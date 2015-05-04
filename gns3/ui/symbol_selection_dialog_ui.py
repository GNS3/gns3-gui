# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'symbol_selection_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

import gns3.qt
from gns3.qt import QtCore, QtGui, QtWidgets

class Ui_SymbolSelectionDialog(object):
    def setupUi(self, SymbolSelectionDialog):
        SymbolSelectionDialog.setObjectName("SymbolSelectionDialog")
        SymbolSelectionDialog.resize(319, 389)
        SymbolSelectionDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(SymbolSelectionDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.uiSymbolListWidget = QtWidgets.QListWidget(SymbolSelectionDialog)
        self.uiSymbolListWidget.setMinimumSize(QtCore.QSize(0, 300))
        self.uiSymbolListWidget.setObjectName("uiSymbolListWidget")
        self.gridLayout.addWidget(self.uiSymbolListWidget, 0, 0, 1, 2)
        self.uiCategoryLabel = QtWidgets.QLabel(SymbolSelectionDialog)
        self.uiCategoryLabel.setObjectName("uiCategoryLabel")
        self.gridLayout.addWidget(self.uiCategoryLabel, 1, 0, 1, 1)
        self.uiCategoryComboBox = QtWidgets.QComboBox(SymbolSelectionDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCategoryComboBox.sizePolicy().hasHeightForWidth())
        self.uiCategoryComboBox.setSizePolicy(sizePolicy)
        self.uiCategoryComboBox.setObjectName("uiCategoryComboBox")
        self.gridLayout.addWidget(self.uiCategoryComboBox, 1, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(SymbolSelectionDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.horizontalLayout.addWidget(self.uiButtonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)

        self.retranslateUi(SymbolSelectionDialog)
        self.uiButtonBox.accepted.connect(SymbolSelectionDialog.accept)
        self.uiButtonBox.rejected.connect(SymbolSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SymbolSelectionDialog)

    def retranslateUi(self, SymbolSelectionDialog):
        _translate = gns3.qt.translate
        SymbolSelectionDialog.setWindowTitle(_translate("SymbolSelectionDialog", "Symbol selection"))
        self.uiCategoryLabel.setText(_translate("SymbolSelectionDialog", "Category:"))

from . import resources_rc
