# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/preferences_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(590, 534)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(PreferencesDialog.sizePolicy().hasHeightForWidth())
        PreferencesDialog.setSizePolicy(sizePolicy)
        PreferencesDialog.setModal(True)
        self.gridlayout = QtWidgets.QGridLayout(PreferencesDialog)
        self.gridlayout.setObjectName("gridlayout")
        self.uiButtonBox = QtWidgets.QDialogButtonBox(PreferencesDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.uiButtonBox.setCenterButtons(False)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.gridlayout.addWidget(self.uiButtonBox, 2, 1, 1, 2)
        self.uiTreeWidget = QtWidgets.QTreeWidget(PreferencesDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Expanding)
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
        self.uiTreeWidget.setObjectName("uiTreeWidget")
        self.uiTreeWidget.headerItem().setText(0, "1")
        self.uiTreeWidget.header().setVisible(False)
        self.gridlayout.addWidget(self.uiTreeWidget, 0, 0, 1, 1)
        self.uiLine = QtWidgets.QFrame(PreferencesDialog)
        self.uiLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.uiLine.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.uiLine.setObjectName("uiLine")
        self.gridlayout.addWidget(self.uiLine, 1, 0, 1, 3)
        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.setSpacing(3)
        self.vboxlayout.setObjectName("vboxlayout")
        self.uiTitleLabel = QtWidgets.QLabel(PreferencesDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
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
        self.uiTitleLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.uiTitleLabel.setObjectName("uiTitleLabel")
        self.vboxlayout.addWidget(self.uiTitleLabel)
        self.uiStackedWidget = QtWidgets.QStackedWidget(PreferencesDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.uiStackedWidget.sizePolicy().hasHeightForWidth())
        self.uiStackedWidget.setSizePolicy(sizePolicy)
        self.uiStackedWidget.setObjectName("uiStackedWidget")
        self.uiPageWidget = QtWidgets.QWidget()
        self.uiPageWidget.setObjectName("uiPageWidget")
        self.uiStackedWidget.addWidget(self.uiPageWidget)
        self.vboxlayout.addWidget(self.uiStackedWidget)
        self.gridlayout.addLayout(self.vboxlayout, 0, 2, 1, 1)

        self.retranslateUi(PreferencesDialog)
        self.uiButtonBox.accepted.connect(PreferencesDialog.accept)
        self.uiButtonBox.rejected.connect(PreferencesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)

    def retranslateUi(self, PreferencesDialog):
        _translate = QtCore.QCoreApplication.translate
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Preferences"))

from . import resources_rc
