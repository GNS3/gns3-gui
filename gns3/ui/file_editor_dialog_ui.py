# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/file_editor_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FileEditorDialog(object):
    def setupUi(self, FileEditorDialog):
        FileEditorDialog.setObjectName("FileEditorDialog")
        FileEditorDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        FileEditorDialog.resize(768, 677)
        FileEditorDialog.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(FileEditorDialog)
        self.verticalLayout.setContentsMargins(-1, -1, 12, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiFileTextEdit = QtWidgets.QTextEdit(FileEditorDialog)
        self.uiFileTextEdit.setObjectName("uiFileTextEdit")
        self.verticalLayout.addWidget(self.uiFileTextEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiRefreshButton = QtWidgets.QPushButton(FileEditorDialog)
        self.uiRefreshButton.setObjectName("uiRefreshButton")
        self.horizontalLayout.addWidget(self.uiRefreshButton)
        self.uiOkButton = QtWidgets.QDialogButtonBox(FileEditorDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiOkButton.sizePolicy().hasHeightForWidth())
        self.uiOkButton.setSizePolicy(sizePolicy)
        self.uiOkButton.setOrientation(QtCore.Qt.Horizontal)
        self.uiOkButton.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.uiOkButton.setObjectName("uiOkButton")
        self.horizontalLayout.addWidget(self.uiOkButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(FileEditorDialog)
        self.uiOkButton.accepted.connect(FileEditorDialog.accept)
        self.uiOkButton.rejected.connect(FileEditorDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FileEditorDialog)

    def retranslateUi(self, FileEditorDialog):
        _translate = QtCore.QCoreApplication.translate
        FileEditorDialog.setWindowTitle(_translate("FileEditorDialog", "File editor"))
        self.uiFileTextEdit.setHtml(_translate("FileEditorDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.SF NS Text\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.uiRefreshButton.setText(_translate("FileEditorDialog", "Refresh"))

from . import resources_rc
