# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/masci/devel/gns3/gns3-gui/gns3/ui/cloud_preferences_page.ui'
#
# Created: Wed Apr 23 22:46:42 2014
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

class Ui_CloudPreferencesPageWidget(object):
    def setupUi(self, CloudPreferencesPageWidget):
        CloudPreferencesPageWidget.setObjectName(_fromUtf8("CloudPreferencesPageWidget"))
        CloudPreferencesPageWidget.resize(567, 406)
        self.gridLayout = QtGui.QGridLayout(CloudPreferencesPageWidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.uiUserNameLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiUserNameLabel.setObjectName(_fromUtf8("uiUserNameLabel"))
        self.gridLayout.addWidget(self.uiUserNameLabel, 0, 0, 1, 1)
        self.uiAPIKeyLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiAPIKeyLabel.setObjectName(_fromUtf8("uiAPIKeyLabel"))
        self.gridLayout.addWidget(self.uiAPIKeyLabel, 0, 1, 1, 1)
        self.uiAPIKeyLineEdit = QtGui.QLineEdit(CloudPreferencesPageWidget)
        self.uiAPIKeyLineEdit.setObjectName(_fromUtf8("uiAPIKeyLineEdit"))
        self.gridLayout.addWidget(self.uiAPIKeyLineEdit, 1, 1, 1, 1)
        self.uiCreateAccountLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiCreateAccountLabel.setTextFormat(QtCore.Qt.RichText)
        self.uiCreateAccountLabel.setObjectName(_fromUtf8("uiCreateAccountLabel"))
        self.gridLayout.addWidget(self.uiCreateAccountLabel, 2, 1, 1, 1)
        self.uiRememberAPIKeyRadioButton = QtGui.QRadioButton(CloudPreferencesPageWidget)
        self.uiRememberAPIKeyRadioButton.setObjectName(_fromUtf8("uiRememberAPIKeyRadioButton"))
        self.gridLayout.addWidget(self.uiRememberAPIKeyRadioButton, 3, 1, 1, 1)
        self.uiForgetAPIKeyRadioButton = QtGui.QRadioButton(CloudPreferencesPageWidget)
        self.uiForgetAPIKeyRadioButton.setObjectName(_fromUtf8("uiForgetAPIKeyRadioButton"))
        self.gridLayout.addWidget(self.uiForgetAPIKeyRadioButton, 4, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 1)
        self.uiUserNameLineEdit = QtGui.QLineEdit(CloudPreferencesPageWidget)
        self.uiUserNameLineEdit.setObjectName(_fromUtf8("uiUserNameLineEdit"))
        self.gridLayout.addWidget(self.uiUserNameLineEdit, 1, 0, 1, 1)

        self.retranslateUi(CloudPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(CloudPreferencesPageWidget)

    def retranslateUi(self, CloudPreferencesPageWidget):
        CloudPreferencesPageWidget.setWindowTitle(_translate("CloudPreferencesPageWidget", "Cloud", None))
        self.uiUserNameLabel.setText(_translate("CloudPreferencesPageWidget", "User Name:", None))
        self.uiAPIKeyLabel.setText(_translate("CloudPreferencesPageWidget", "API Key", None))
        self.uiCreateAccountLabel.setText(_translate("CloudPreferencesPageWidget", "No API Key? <a href=\"#\">Create Cloud Account.</a>", None))
        self.uiRememberAPIKeyRadioButton.setText(_translate("CloudPreferencesPageWidget", "Remeber these settings\n"
"(Suggested for private computers)", None))
        self.uiForgetAPIKeyRadioButton.setText(_translate("CloudPreferencesPageWidget", "Forget these settings on exit\n"
"(Suggested for public computers)", None))

