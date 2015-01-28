# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/symbol_selection_dialog.ui'
#
# Created: Thu Dec 11 23:26:53 2014
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_SymbolSelectionDialog(object):

    def setupUi(self, SymbolSelectionDialog):
        SymbolSelectionDialog.setObjectName(_fromUtf8("SymbolSelectionDialog"))
        SymbolSelectionDialog.resize(319, 389)
        SymbolSelectionDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(SymbolSelectionDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiSymbolListWidget = QtGui.QListWidget(SymbolSelectionDialog)
        self.uiSymbolListWidget.setMinimumSize(QtCore.QSize(0, 300))
        self.uiSymbolListWidget.setObjectName(_fromUtf8("uiSymbolListWidget"))
        self.gridLayout.addWidget(self.uiSymbolListWidget, 0, 0, 1, 2)
        self.uiCategoryLabel = QtGui.QLabel(SymbolSelectionDialog)
        self.uiCategoryLabel.setObjectName(_fromUtf8("uiCategoryLabel"))
        self.gridLayout.addWidget(self.uiCategoryLabel, 1, 0, 1, 1)
        self.uiCategoryComboBox = QtGui.QComboBox(SymbolSelectionDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCategoryComboBox.sizePolicy().hasHeightForWidth())
        self.uiCategoryComboBox.setSizePolicy(sizePolicy)
        self.uiCategoryComboBox.setObjectName(_fromUtf8("uiCategoryComboBox"))
        self.gridLayout.addWidget(self.uiCategoryComboBox, 1, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiButtonBox = QtGui.QDialogButtonBox(SymbolSelectionDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.horizontalLayout.addWidget(self.uiButtonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)

        self.retranslateUi(SymbolSelectionDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SymbolSelectionDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SymbolSelectionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SymbolSelectionDialog)

    def retranslateUi(self, SymbolSelectionDialog):
        SymbolSelectionDialog.setWindowTitle(_translate("SymbolSelectionDialog", "Symbol selection", None))
        self.uiCategoryLabel.setText(_translate("SymbolSelectionDialog", "Category:", None))

from . import resources_rc
