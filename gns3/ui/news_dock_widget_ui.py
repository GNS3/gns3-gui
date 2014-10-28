# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/news_dock_widget.ui'
#
# Created: Sat Oct 18 15:38:49 2014
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

class Ui_NewsDockWidget(object):
    def setupUi(self, NewsDockWidget):
        NewsDockWidget.setObjectName(_fromUtf8("NewsDockWidget"))
        NewsDockWidget.resize(300, 275)
        NewsDockWidget.setFloating(False)
        NewsDockWidget.setFeatures(QtGui.QDockWidget.DockWidgetFloatable|QtGui.QDockWidget.DockWidgetMovable)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiWebView = QtWebKit.QWebView(self.dockWidgetContents)
        self.uiWebView.setMinimumSize(QtCore.QSize(300, 250))
        self.uiWebView.setMaximumSize(QtCore.QSize(300, 250))
        self.uiWebView.setProperty("url", QtCore.QUrl(None))
        self.uiWebView.setObjectName(_fromUtf8("uiWebView"))
        self.horizontalLayout.addWidget(self.uiWebView)
        NewsDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(NewsDockWidget)
        QtCore.QMetaObject.connectSlotsByName(NewsDockWidget)

    def retranslateUi(self, NewsDockWidget):
        NewsDockWidget.setWindowTitle(_translate("NewsDockWidget", "GNS3 Jungle", None))

from PyQt4 import QtWebKit
