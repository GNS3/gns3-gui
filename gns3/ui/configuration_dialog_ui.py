# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/configuration_dialog.ui'
#
# Created: Thu Oct  2 15:12:03 2014
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


class Ui_configurationDialog(object):

    def setupUi(self, configurationDialog):
        configurationDialog.setObjectName(_fromUtf8("configurationDialog"))
        configurationDialog.resize(585, 454)
        configurationDialog.setModal(True)
        self.gridlayout = QtGui.QGridLayout(configurationDialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.splitter = QtGui.QSplitter(configurationDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.verticalLayout = QtGui.QWidget(self.splitter)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.vboxlayout = QtGui.QVBoxLayout(self.verticalLayout)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTitleLabel = QtGui.QLabel(self.verticalLayout)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.uiTitleLabel.setFont(font)
        self.uiTitleLabel.setFrameShape(QtGui.QFrame.Box)
        self.uiTitleLabel.setFrameShadow(QtGui.QFrame.Sunken)
        self.uiTitleLabel.setTextFormat(QtCore.Qt.PlainText)
        self.uiTitleLabel.setObjectName(_fromUtf8("uiTitleLabel"))
        self.vboxlayout.addWidget(self.uiTitleLabel)
        self.uiConfigStackedWidget = QtGui.QStackedWidget(self.verticalLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiConfigStackedWidget.sizePolicy().hasHeightForWidth())
        self.uiConfigStackedWidget.setSizePolicy(sizePolicy)
        self.uiConfigStackedWidget.setFrameShape(QtGui.QFrame.Box)
        self.uiConfigStackedWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.uiConfigStackedWidget.setObjectName(_fromUtf8("uiConfigStackedWidget"))
        self.uiEmptyPageWidget = QtGui.QWidget()
        self.uiEmptyPageWidget.setObjectName(_fromUtf8("uiEmptyPageWidget"))
        self.vboxlayout1 = QtGui.QVBoxLayout(self.uiEmptyPageWidget)
        self.vboxlayout1.setSpacing(0)
        self.vboxlayout1.setContentsMargins(0, 4, 0, 0)
        self.vboxlayout1.setObjectName(_fromUtf8("vboxlayout1"))
        self.uiConfigStackedWidget.addWidget(self.uiEmptyPageWidget)
        self.vboxlayout.addWidget(self.uiConfigStackedWidget)
        self.gridlayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.uiButtonBox = QtGui.QDialogButtonBox(configurationDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridlayout.addWidget(self.uiButtonBox, 1, 0, 1, 1)

        self.retranslateUi(configurationDialog)
        self.uiConfigStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(configurationDialog)

    def retranslateUi(self, configurationDialog):
        configurationDialog.setWindowTitle(_translate("configurationDialog", "Configuration", None))
        self.uiTitleLabel.setText(_translate("configurationDialog", "Configuration", None))

from . import resources_rc
