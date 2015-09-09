# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/noplay/code/gns3/gns3-gui/gns3/ui/appliance_window.ui'
#
# Created by: PyQt5 UI code generator 5.5
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ApplianceWindow(object):
    def setupUi(self, ApplianceWindow):
        ApplianceWindow.setObjectName("ApplianceWindow")
        ApplianceWindow.setWindowModality(QtCore.Qt.WindowModal)
        self.horizontalLayout = QtWidgets.QHBoxLayout(ApplianceWindow)
        self.horizontalLayout.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiWebView = QtWebKitWidgets.QWebView(ApplianceWindow)
        self.uiWebView.setUrl(QtCore.QUrl("about:blank"))
        self.uiWebView.setObjectName("uiWebView")
        self.horizontalLayout.addWidget(self.uiWebView)

        self.retranslateUi(ApplianceWindow)
        QtCore.QMetaObject.connectSlotsByName(ApplianceWindow)

    def retranslateUi(self, ApplianceWindow):
        _translate = QtCore.QCoreApplication.translate
        ApplianceWindow.setWindowTitle(_translate("ApplianceWindow", "Form"))

from PyQt5 import QtWebKitWidgets
