# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/getting_started_dialog.ui'
#
# Created: Thu Oct 16 19:58:05 2014
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


class Ui_GettingStartedDialog(object):

    def setupUi(self, GettingStartedDialog):
        GettingStartedDialog.setObjectName(_fromUtf8("GettingStartedDialog"))
        GettingStartedDialog.resize(778, 593)
        GettingStartedDialog.setModal(True)
        self.gridLayout = QtGui.QGridLayout(GettingStartedDialog)
        self.gridLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiWebView = QtWebKit.QWebView(GettingStartedDialog)
        self.uiWebView.setMinimumSize(QtCore.QSize(760, 540))
        self.uiWebView.setMaximumSize(QtCore.QSize(760, 540))
        self.uiWebView.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.uiWebView.setObjectName(_fromUtf8("uiWebView"))
        self.gridLayout.addWidget(self.uiWebView, 0, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiCheckBox = QtGui.QCheckBox(GettingStartedDialog)
        self.uiCheckBox.setChecked(True)
        self.uiCheckBox.setObjectName(_fromUtf8("uiCheckBox"))
        self.horizontalLayout.addWidget(self.uiCheckBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(GettingStartedDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(GettingStartedDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), GettingStartedDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), GettingStartedDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GettingStartedDialog)

    def retranslateUi(self, GettingStartedDialog):
        GettingStartedDialog.setWindowTitle(_translate("GettingStartedDialog", "Getting started", None))
        self.uiCheckBox.setText(_translate("GettingStartedDialog", "Don\'t show this again", None))

from PyQt4 import QtWebKit
