# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'news_dock_widget.ui'
#
# Created: Wed May  6 14:31:53 2015
#      by: PyQt5 UI code generator 5.4
#
# WARNING! All changes made in this file will be lost!

import gns3.qt
from gns3.qt import QtCore, QtGui, QtWidgets


class Ui_NewsDockWidget:

    def setupUi(self, NewsDockWidget):
        NewsDockWidget.setObjectName("NewsDockWidget")
        NewsDockWidget.resize(203, 225)
        NewsDockWidget.setFloating(False)
        NewsDockWidget.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetMovable)
        NewsDockWidget.setAllowedAreas(QtCore.Qt.AllDockWidgetAreas)
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout.setContentsMargins(1, 0, 2, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.uiWebView = QtWebKitWidgets.QWebView(self.dockWidgetContents)
        self.uiWebView.setMinimumSize(QtCore.QSize(200, 200))
        self.uiWebView.setMaximumSize(QtCore.QSize(200, 200))
        self.uiWebView.setProperty("url", QtCore.QUrl(None))
        self.uiWebView.setObjectName("uiWebView")
        self.horizontalLayout.addWidget(self.uiWebView)
        NewsDockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(NewsDockWidget)
        QtCore.QMetaObject.connectSlotsByName(NewsDockWidget)

    def retranslateUi(self, NewsDockWidget):
        _translate = gns3.qt.translate
        NewsDockWidget.setWindowTitle(_translate("NewsDockWidget", "Jungle Newsfeed"))

import gns3.qt
from gns3.qt import QtWebKitWidgets
