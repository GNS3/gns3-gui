# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/new_project_dialog.ui'
#
# Created: Tue Mar  3 11:41:04 2015
#      by: PyQt4 UI code generator 4.11.3
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


class Ui_NewProjectDialog(object):

    def setupUi(self, NewProjectDialog):
        NewProjectDialog.setObjectName(_fromUtf8("NewProjectDialog"))
        NewProjectDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        NewProjectDialog.resize(491, 177)
        NewProjectDialog.setModal(True)
        self.gridLayout_2 = QtGui.QGridLayout(NewProjectDialog)
        self.gridLayout_2.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.uiProjectGroupBox = QtGui.QGroupBox(NewProjectDialog)
        self.uiProjectGroupBox.setObjectName(_fromUtf8("uiProjectGroupBox"))
        self.gridLayout = QtGui.QGridLayout(self.uiProjectGroupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiNameLabel = QtGui.QLabel(self.uiProjectGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiNameLabel.sizePolicy().hasHeightForWidth())
        self.uiNameLabel.setSizePolicy(sizePolicy)
        self.uiNameLabel.setObjectName(_fromUtf8("uiNameLabel"))
        self.gridLayout.addWidget(self.uiNameLabel, 0, 0, 1, 1)
        self.uiNameLineEdit = QtGui.QLineEdit(self.uiProjectGroupBox)
        self.uiNameLineEdit.setObjectName(_fromUtf8("uiNameLineEdit"))
        self.gridLayout.addWidget(self.uiNameLineEdit, 0, 1, 1, 4)
        self.uiLocationLabel = QtGui.QLabel(self.uiProjectGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiLocationLabel.sizePolicy().hasHeightForWidth())
        self.uiLocationLabel.setSizePolicy(sizePolicy)
        self.uiLocationLabel.setObjectName(_fromUtf8("uiLocationLabel"))
        self.gridLayout.addWidget(self.uiLocationLabel, 1, 0, 1, 1)
        self.uiLocationLineEdit = QtGui.QLineEdit(self.uiProjectGroupBox)
        self.uiLocationLineEdit.setObjectName(_fromUtf8("uiLocationLineEdit"))
        self.gridLayout.addWidget(self.uiLocationLineEdit, 1, 1, 1, 3)
        self.uiLocationBrowserToolButton = QtGui.QToolButton(self.uiProjectGroupBox)
        self.uiLocationBrowserToolButton.setObjectName(_fromUtf8("uiLocationBrowserToolButton"))
        self.gridLayout.addWidget(self.uiLocationBrowserToolButton, 1, 4, 1, 1)
        self.uiTypeLabel = QtGui.QLabel(self.uiProjectGroupBox)
        self.uiTypeLabel.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiTypeLabel.sizePolicy().hasHeightForWidth())
        self.uiTypeLabel.setSizePolicy(sizePolicy)
        self.uiTypeLabel.setObjectName(_fromUtf8("uiTypeLabel"))
        self.gridLayout.addWidget(self.uiTypeLabel, 2, 0, 1, 1)
        self.uiLocalRadioButton = QtGui.QRadioButton(self.uiProjectGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiLocalRadioButton.sizePolicy().hasHeightForWidth())
        self.uiLocalRadioButton.setSizePolicy(sizePolicy)
        self.uiLocalRadioButton.setChecked(True)
        self.uiLocalRadioButton.setObjectName(_fromUtf8("uiLocalRadioButton"))
        self.gridLayout.addWidget(self.uiLocalRadioButton, 2, 1, 1, 1)
        self.uiCloudRadioButton = QtGui.QRadioButton(self.uiProjectGroupBox)
        self.uiCloudRadioButton.setEnabled(False)
        self.uiCloudRadioButton.setObjectName(_fromUtf8("uiCloudRadioButton"))
        self.gridLayout.addWidget(self.uiCloudRadioButton, 2, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(201, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 3, 1, 2)
        self.gridLayout_2.addWidget(self.uiProjectGroupBox, 0, 0, 1, 3)
        self.uiOpenProjectPushButton = QtGui.QPushButton(NewProjectDialog)
        self.uiOpenProjectPushButton.setObjectName(_fromUtf8("uiOpenProjectPushButton"))
        self.gridLayout_2.addWidget(self.uiOpenProjectPushButton, 1, 0, 1, 1)
        self.uiRecentProjectsPushButton = QtGui.QPushButton(NewProjectDialog)
        self.uiRecentProjectsPushButton.setObjectName(_fromUtf8("uiRecentProjectsPushButton"))
        self.gridLayout_2.addWidget(self.uiRecentProjectsPushButton, 1, 1, 1, 1)
        self.uiButtonBox = QtGui.QDialogButtonBox(NewProjectDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridLayout_2.addWidget(self.uiButtonBox, 1, 2, 1, 1)

        self.retranslateUi(NewProjectDialog)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewProjectDialog.accept)
        QtCore.QObject.connect(self.uiButtonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewProjectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewProjectDialog)

    def retranslateUi(self, NewProjectDialog):
        NewProjectDialog.setWindowTitle(_translate("NewProjectDialog", "New project", None))
        self.uiProjectGroupBox.setTitle(_translate("NewProjectDialog", "Project", None))
        self.uiNameLabel.setText(_translate("NewProjectDialog", "Name:", None))
        self.uiLocationLabel.setText(_translate("NewProjectDialog", "Location:", None))
        self.uiLocationBrowserToolButton.setText(_translate("NewProjectDialog", "Browse...", None))
        self.uiTypeLabel.setText(_translate("NewProjectDialog", "Type:", None))
        self.uiLocalRadioButton.setText(_translate("NewProjectDialog", "Local", None))
        self.uiCloudRadioButton.setText(_translate("NewProjectDialog", "Cloud", None))
        self.uiOpenProjectPushButton.setText(_translate("NewProjectDialog", "&Open a project", None))
        self.uiRecentProjectsPushButton.setText(_translate("NewProjectDialog", "&Recent projects...", None))
