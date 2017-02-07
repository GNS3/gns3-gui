# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/export_debug_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ExportDebugDialog(object):

    def setupUi(self, ExportDebugDialog):
        ExportDebugDialog.setObjectName("ExportDebugDialog")
        ExportDebugDialog.setWindowModality(QtCore.Qt.WindowModal)
        ExportDebugDialog.resize(555, 215)
        ExportDebugDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(ExportDebugDialog)
        self.verticalLayout.setContentsMargins(-1, -1, 12, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(ExportDebugDialog)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.uiCancelButton = QtWidgets.QPushButton(ExportDebugDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiCancelButton.sizePolicy().hasHeightForWidth())
        self.uiCancelButton.setSizePolicy(sizePolicy)
        self.uiCancelButton.setObjectName("uiCancelButton")
        self.horizontalLayout.addWidget(self.uiCancelButton)
        self.uiOkButton = QtWidgets.QDialogButtonBox(ExportDebugDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiOkButton.sizePolicy().hasHeightForWidth())
        self.uiOkButton.setSizePolicy(sizePolicy)
        self.uiOkButton.setOrientation(QtCore.Qt.Horizontal)
        self.uiOkButton.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.uiOkButton.setObjectName("uiOkButton")
        self.horizontalLayout.addWidget(self.uiOkButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label.raise_()

        self.retranslateUi(ExportDebugDialog)
        self.uiCancelButton.clicked.connect(ExportDebugDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExportDebugDialog)

    def retranslateUi(self, ExportDebugDialog):
        _translate = QtCore.QCoreApplication.translate
        ExportDebugDialog.setWindowTitle(_translate("ExportDebugDialog", "Export debug information"))
        self.label.setText(_translate("ExportDebugDialog", "<html><head/><body><p>This will export a debug information file.</p><p><span style=\" font-weight:600;\">Be aware</span> this file can contain <span style=\" font-weight:600;\">private information</span> about your project, your GNS3 settings or your computer (list of running processes, opened ports etc.). You can unzip the file in order to edit its content.</p><p><br/>Thanks a lot for helping GNS3.</p></body></html>"))
        self.uiCancelButton.setText(_translate("ExportDebugDialog", "Cancel"))

from . import resources_rc
