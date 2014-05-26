# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/jseutterlst/gns3/gns3-gui/gns3/ui/resources_type_dialog.ui'
#
# Created: Tue May 20 17:02:27 2014
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

class Ui_ResourcesTypeDialog(object):
    def setupUi(self, ResourcesTypeDialog):
        ResourcesTypeDialog.setObjectName(_fromUtf8("ResourcesTypeDialog"))
        ResourcesTypeDialog.resize(285, 149)
        self.verticalLayout_2 = QtGui.QVBoxLayout(ResourcesTypeDialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = QtGui.QGroupBox(ResourcesTypeDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.uiLocalRadioButton = QtGui.QRadioButton(self.groupBox)
        self.uiLocalRadioButton.setChecked(True)
        self.uiLocalRadioButton.setObjectName(_fromUtf8("uiLocalRadioButton"))
        self.verticalLayout.addWidget(self.uiLocalRadioButton)
        self.uiCloudRadioButton = QtGui.QRadioButton(self.groupBox)
        self.uiCloudRadioButton.setObjectName(_fromUtf8("uiCloudRadioButton"))
        self.verticalLayout.addWidget(self.uiCloudRadioButton)
        self.verticalLayout_2.addWidget(self.groupBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ResourcesTypeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(ResourcesTypeDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ResourcesTypeDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ResourcesTypeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ResourcesTypeDialog)

    def retranslateUi(self, ResourcesTypeDialog):
        ResourcesTypeDialog.setWindowTitle(_translate("ResourcesTypeDialog", "Dialog", None))
        self.groupBox.setTitle(_translate("ResourcesTypeDialog", "Choose the resource type for this project", None))
        self.uiLocalRadioButton.setText(_translate("ResourcesTypeDialog", "Local", None))
        self.uiCloudRadioButton.setText(_translate("ResourcesTypeDialog", "Cloud", None))

