# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/preferences_dialog.ui'
#
# Created: Sat Feb 28 15:58:23 2015
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

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName(_fromUtf8("PreferencesDialog"))
        PreferencesDialog.resize(590, 534)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(PreferencesDialog.sizePolicy().hasHeightForWidth())
        PreferencesDialog.setSizePolicy(sizePolicy)
        PreferencesDialog.setModal(True)
        self.gridlayout = QtGui.QGridLayout(PreferencesDialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.uiButtonBox = QtGui.QDialogButtonBox(PreferencesDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setCenterButtons(False)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridlayout.addWidget(self.uiButtonBox, 2, 1, 1, 2)
        self.uiTreeWidget = QtGui.QTreeWidget(PreferencesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiTreeWidget.setSizePolicy(sizePolicy)
        self.uiTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiTreeWidget.setFont(font)
        self.uiTreeWidget.setIndentation(10)
        self.uiTreeWidget.setObjectName(_fromUtf8("uiTreeWidget"))
        self.uiTreeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.uiTreeWidget.header().setVisible(False)
        self.gridlayout.addWidget(self.uiTreeWidget, 0, 0, 1, 1)
        self.uiLine = QtGui.QFrame(PreferencesDialog)
        self.uiLine.setFrameShape(QtGui.QFrame.HLine)
        self.uiLine.setFrameShadow(QtGui.QFrame.Sunken)
        self.uiLine.setObjectName(_fromUtf8("uiLine"))
        self.gridlayout.addWidget(self.uiLine, 1, 0, 1, 3)
        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setSpacing(3)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTitleLabel = QtGui.QLabel(PreferencesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiTitleLabel.sizePolicy().hasHeightForWidth())
        self.uiTitleLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setUnderline(False)
        font.setWeight(75)
        self.uiTitleLabel.setFont(font)
        self.uiTitleLabel.setFrameShape(QtGui.QFrame.Box)
        self.uiTitleLabel.setObjectName(_fromUtf8("uiTitleLabel"))
        self.vboxlayout.addWidget(self.uiTitleLabel)
        self.uiStackedWidget = QtGui.QStackedWidget(PreferencesDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.uiStackedWidget.sizePolicy().hasHeightForWidth())
        self.uiStackedWidget.setSizePolicy(sizePolicy)
        self.uiStackedWidget.setObjectName(_fromUtf8("uiStackedWidget"))
        self.uiPageWidget = QtGui.QWidget()
        self.uiPageWidget.setObjectName(_fromUtf8("uiPageWidget"))
        self.uiStackedWidget.addWidget(self.uiPageWidget)
        self.vboxlayout.addWidget(self.uiStackedWidget)
        self.gridlayout.addLayout(self.vboxlayout, 0, 2, 1, 1)

        self.retranslateUi(PreferencesDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PreferencesDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PreferencesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Preferences", None))

from . import resources_rc
