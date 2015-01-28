# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gns3/ui/import_cloud_project_dialog.ui'
#
# Created: Wed Oct 22 12:45:41 2014
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


class Ui_ImportCloudProjectDialog(object):

    def setupUi(self, ImportCloudProjectDialog):
        ImportCloudProjectDialog.setObjectName(_fromUtf8("ImportCloudProjectDialog"))
        ImportCloudProjectDialog.resize(471, 402)
        self.listWidget = QtGui.QListWidget(ImportCloudProjectDialog)
        self.listWidget.setGeometry(QtCore.QRect(20, 30, 431, 271))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.uiImportProjectAction = QtGui.QPushButton(ImportCloudProjectDialog)
        self.uiImportProjectAction.setGeometry(QtCore.QRect(110, 320, 99, 24))
        self.uiImportProjectAction.setObjectName(_fromUtf8("uiImportProjectAction"))
        self.uiDeleteProjectAction = QtGui.QPushButton(ImportCloudProjectDialog)
        self.uiDeleteProjectAction.setGeometry(QtCore.QRect(260, 320, 99, 24))
        self.uiDeleteProjectAction.setObjectName(_fromUtf8("uiDeleteProjectAction"))
        self.buttonBox = QtGui.QDialogButtonBox(ImportCloudProjectDialog)
        self.buttonBox.setGeometry(QtCore.QRect(300, 360, 160, 25))
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(ImportCloudProjectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ImportCloudProjectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ImportCloudProjectDialog)

    def retranslateUi(self, ImportCloudProjectDialog):
        ImportCloudProjectDialog.setWindowTitle(_translate("ImportCloudProjectDialog", "Dialog", None))
        self.uiImportProjectAction.setText(_translate("ImportCloudProjectDialog", "Import", None))
        self.uiDeleteProjectAction.setText(_translate("ImportCloudProjectDialog", "Delete", None))
