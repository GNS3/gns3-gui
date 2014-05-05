# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/masci/devel/gns3/gns3-gui/gns3/ui/cloud_preferences_page.ui'
#
# Created: Thu Apr 24 16:27:29 2014
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
        self.uiAPIKeyLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiAPIKeyLabel.setObjectName(_fromUtf8("uiAPIKeyLabel"))
        self.gridLayout.addWidget(self.uiAPIKeyLabel, 0, 1, 1, 1)
        self.uiForgetAPIKeyRadioButton = QtGui.QRadioButton(CloudPreferencesPageWidget)
        self.uiForgetAPIKeyRadioButton.setObjectName(_fromUtf8("uiForgetAPIKeyRadioButton"))
        self.gridLayout.addWidget(self.uiForgetAPIKeyRadioButton, 4, 1, 1, 1)
        self.uiUserNameLineEdit = QtGui.QLineEdit(CloudPreferencesPageWidget)
        self.uiUserNameLineEdit.setObjectName(_fromUtf8("uiUserNameLineEdit"))
        self.gridLayout.addWidget(self.uiUserNameLineEdit, 1, 0, 1, 1)
        self.uiCreateAccountLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiCreateAccountLabel.setTextFormat(QtCore.Qt.RichText)
        self.uiCreateAccountLabel.setObjectName(_fromUtf8("uiCreateAccountLabel"))
        self.gridLayout.addWidget(self.uiCreateAccountLabel, 2, 1, 1, 1)
        self.PLACEHOLDER = QtGui.QFrame(CloudPreferencesPageWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PLACEHOLDER.sizePolicy().hasHeightForWidth())
        self.PLACEHOLDER.setSizePolicy(sizePolicy)
        self.PLACEHOLDER.setMinimumSize(QtCore.QSize(0, 25))
        self.PLACEHOLDER.setFrameShape(QtGui.QFrame.StyledPanel)
        self.PLACEHOLDER.setFrameShadow(QtGui.QFrame.Raised)
        self.PLACEHOLDER.setObjectName(_fromUtf8("PLACEHOLDER"))
        self.gridLayout.addWidget(self.PLACEHOLDER, 6, 0, 1, 2)
        self.uiCloudProviderLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiCloudProviderLabel.setObjectName(_fromUtf8("uiCloudProviderLabel"))
        self.gridLayout.addWidget(self.uiCloudProviderLabel, 2, 0, 1, 1)
        self.uiAPIKeyLineEdit = QtGui.QLineEdit(CloudPreferencesPageWidget)
        self.uiAPIKeyLineEdit.setObjectName(_fromUtf8("uiAPIKeyLineEdit"))
        self.gridLayout.addWidget(self.uiAPIKeyLineEdit, 1, 1, 1, 1)
        self.uiRegionComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiRegionComboBox.setObjectName(_fromUtf8("uiRegionComboBox"))
        self.gridLayout.addWidget(self.uiRegionComboBox, 5, 0, 1, 1)
        self.uiCloudProviderComboBox = QtGui.QComboBox(CloudPreferencesPageWidget)
        self.uiCloudProviderComboBox.setObjectName(_fromUtf8("uiCloudProviderComboBox"))
        self.gridLayout.addWidget(self.uiCloudProviderComboBox, 3, 0, 1, 1)
        self.uiRegionLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiRegionLabel.setObjectName(_fromUtf8("uiRegionLabel"))
        self.gridLayout.addWidget(self.uiRegionLabel, 4, 0, 1, 1)
        self.uiRememberAPIKeyRadioButton = QtGui.QRadioButton(CloudPreferencesPageWidget)
        self.uiRememberAPIKeyRadioButton.setObjectName(_fromUtf8("uiRememberAPIKeyRadioButton"))
        self.gridLayout.addWidget(self.uiRememberAPIKeyRadioButton, 3, 1, 1, 1)
        self.uiUserNameLabel = QtGui.QLabel(CloudPreferencesPageWidget)
        self.uiUserNameLabel.setObjectName(_fromUtf8("uiUserNameLabel"))
        self.gridLayout.addWidget(self.uiUserNameLabel, 0, 0, 1, 1)

        self.retranslateUi(CloudPreferencesPageWidget)
        QtCore.QMetaObject.connectSlotsByName(CloudPreferencesPageWidget)

    def retranslateUi(self, CloudPreferencesPageWidget):
        CloudPreferencesPageWidget.setWindowTitle(_translate("CloudPreferencesPageWidget", "Cloud", None))
        self.uiAPIKeyLabel.setText(_translate("CloudPreferencesPageWidget", "API Key", None))
        self.uiForgetAPIKeyRadioButton.setText(_translate("CloudPreferencesPageWidget", "Forget these settings on exit\n"
"(Suggested for public computers)", None))
        self.uiCreateAccountLabel.setText(_translate("CloudPreferencesPageWidget", "No API Key? <a href=\"#\">Create Cloud Account.</a>", None))
        self.uiCloudProviderLabel.setText(_translate("CloudPreferencesPageWidget", "Cloud provider", None))
        self.uiRegionLabel.setText(_translate("CloudPreferencesPageWidget", "Region (optional)", None))
        self.uiRememberAPIKeyRadioButton.setText(_translate("CloudPreferencesPageWidget", "Remeber these settings\n"
"(Suggested for private computers)", None))
        self.uiUserNameLabel.setText(_translate("CloudPreferencesPageWidget", "User Name:", None))

