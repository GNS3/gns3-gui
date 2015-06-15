# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/getting_started_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GettingStartedDialog(object):
    def setupUi(self, GettingStartedDialog):
        GettingStartedDialog.setObjectName("GettingStartedDialog")
        GettingStartedDialog.resize(778, 593)
        GettingStartedDialog.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(GettingStartedDialog)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.gridLayout.setObjectName("gridLayout")
        self.uiWebView = QtWebKitWidgets.QWebView(GettingStartedDialog)
        self.uiWebView.setMinimumSize(QtCore.QSize(760, 540))
        self.uiWebView.setMaximumSize(QtCore.QSize(760, 540))
        self.uiWebView.setProperty("url", QtCore.QUrl("about:blank"))
        self.uiWebView.setObjectName("uiWebView")
        self.gridLayout.addWidget(self.uiWebView, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiCheckBox = QtWidgets.QCheckBox(GettingStartedDialog)
        self.uiCheckBox.setChecked(True)
        self.uiCheckBox.setObjectName("uiCheckBox")
        self.horizontalLayout.addWidget(self.uiCheckBox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(GettingStartedDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(GettingStartedDialog)
        self.buttonBox.accepted.connect(GettingStartedDialog.accept)
        self.buttonBox.rejected.connect(GettingStartedDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GettingStartedDialog)

    def retranslateUi(self, GettingStartedDialog):
        _translate = QtCore.QCoreApplication.translate
        GettingStartedDialog.setWindowTitle(_translate("GettingStartedDialog", "Getting started"))
        self.uiCheckBox.setText(_translate("GettingStartedDialog", "Don\'t show this again"))

from PyQt5 import QtWebKitWidgets
