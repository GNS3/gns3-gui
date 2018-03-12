# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/traceng/ui/traceng_node_configuration_page.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TraceNGNodeConfigPageWidget(object):
    def setupUi(self, TraceNGNodeConfigPageWidget):
        TraceNGNodeConfigPageWidget.setObjectName("TraceNGNodeConfigPageWidget")
        TraceNGNodeConfigPageWidget.resize(722, 262)
        self.gridLayout = QtWidgets.QGridLayout(TraceNGNodeConfigPageWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.uiNameLabel = QtWidgets.QLabel(TraceNGNodeConfigPageWidget)
        self.uiNameLabel.setObjectName("uiNameLabel")
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtWidgets.QLineEdit(TraceNGNodeConfigPageWidget)
        self.uiNameLineEdit.setObjectName("uiNameLineEdit")
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 2, 1, 1)
        self.uiDefaultNameFormatLabel = QtWidgets.QLabel(TraceNGNodeConfigPageWidget)
        self.uiDefaultNameFormatLabel.setObjectName("uiDefaultNameFormatLabel")
        self.gridLayout.addWidget(self.uiDefaultNameFormatLabel, 1, 0, 1, 2)
        self.uiDefaultNameFormatLineEdit = QtWidgets.QLineEdit(TraceNGNodeConfigPageWidget)
        self.uiDefaultNameFormatLineEdit.setObjectName("uiDefaultNameFormatLineEdit")
        self.gridLayout.addWidget(self.uiDefaultNameFormatLineEdit, 1, 2, 1, 1)
        self.uiSymbolLabel = QtWidgets.QLabel(TraceNGNodeConfigPageWidget)
        self.uiSymbolLabel.setObjectName("uiSymbolLabel")
        self.gridLayout.addWidget(self.uiSymbolLabel, 2, 0, 1, 2)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.uiSymbolLineEdit = QtWidgets.QLineEdit(TraceNGNodeConfigPageWidget)
        self.uiSymbolLineEdit.setObjectName("uiSymbolLineEdit")
        self.horizontalLayout_7.addWidget(self.uiSymbolLineEdit)
        self.uiSymbolToolButton = QtWidgets.QToolButton(TraceNGNodeConfigPageWidget)
        self.uiSymbolToolButton.setToolButtonStyle(QtCore.Qt.ToolButtonTextOnly)
        self.uiSymbolToolButton.setObjectName("uiSymbolToolButton")
        self.horizontalLayout_7.addWidget(self.uiSymbolToolButton)
        self.gridLayout.addLayout(self.horizontalLayout_7, 2, 2, 1, 1)
        self.uiCategoryLabel = QtWidgets.QLabel(TraceNGNodeConfigPageWidget)
        self.uiCategoryLabel.setObjectName("uiCategoryLabel")
        self.gridLayout.addWidget(self.uiCategoryLabel, 3, 0, 1, 2)
        self.uiCategoryComboBox = QtWidgets.QComboBox(TraceNGNodeConfigPageWidget)
        self.uiCategoryComboBox.setObjectName("uiCategoryComboBox")
        self.gridLayout.addWidget(self.uiCategoryComboBox, 3, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(263, 212, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 2)

        self.retranslateUi(TraceNGNodeConfigPageWidget)
        QtCore.QMetaObject.connectSlotsByName(TraceNGNodeConfigPageWidget)

    def retranslateUi(self, TraceNGNodeConfigPageWidget):
        _translate = QtCore.QCoreApplication.translate
        TraceNGNodeConfigPageWidget.setWindowTitle(_translate("TraceNGNodeConfigPageWidget", "TraceNG node configuration"))
        self.uiNameLabel.setText(_translate("TraceNGNodeConfigPageWidget", "Name:"))
        self.uiDefaultNameFormatLabel.setText(_translate("TraceNGNodeConfigPageWidget", "Default name format:"))
        self.uiSymbolLabel.setText(_translate("TraceNGNodeConfigPageWidget", "Symbol:"))
        self.uiSymbolToolButton.setText(_translate("TraceNGNodeConfigPageWidget", "&Browse..."))
        self.uiCategoryLabel.setText(_translate("TraceNGNodeConfigPageWidget", "Category:"))

