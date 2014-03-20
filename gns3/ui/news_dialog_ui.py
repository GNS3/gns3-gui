# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/workspace/git/gns3-gui/gns3/ui/news_dialog.ui'
#
# Created: Wed Mar 19 16:26:12 2014
#      by: PyQt4 UI code generator 4.10
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

class Ui_NewsDialog(object):
    def setupUi(self, NewsDialog):
        NewsDialog.setObjectName(_fromUtf8("NewsDialog"))
        NewsDialog.resize(424, 466)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(NewsDialog.sizePolicy().hasHeightForWidth())
        NewsDialog.setSizePolicy(sizePolicy)
        self.uiWebView = QtWebKit.QWebView(NewsDialog)
        self.uiWebView.setGeometry(QtCore.QRect(12, 12, 400, 400))
        self.uiWebView.setMinimumSize(QtCore.QSize(400, 400))
        self.uiWebView.setMaximumSize(QtCore.QSize(400, 400))
        self.uiWebView.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.uiWebView.setObjectName(_fromUtf8("uiWebView"))
        self.layoutWidget = QtGui.QWidget(NewsDialog)
        self.layoutWidget.setGeometry(QtCore.QRect(12, 420, 401, 32))
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.uiWhyThisAdLabel = QtGui.QLabel(self.layoutWidget)
        self.uiWhyThisAdLabel.setOpenExternalLinks(True)
        self.uiWhyThisAdLabel.setObjectName(_fromUtf8("uiWhyThisAdLabel"))
        self.horizontalLayout.addWidget(self.uiWhyThisAdLabel)
        spacerItem = QtGui.QSpacerItem(58, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(self.layoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout.addWidget(self.buttonBox)

        self.retranslateUi(NewsDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), NewsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), NewsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(NewsDialog)

    def retranslateUi(self, NewsDialog):
        NewsDialog.setWindowTitle(_translate("NewsDialog", "GNS3 News", None))
        self.uiWhyThisAdLabel.setText(_translate("NewsDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body>\n"
"<p> <a href=\"http://www.gns3.net/why-this-ad/\">Why this?</a></p></body></html>", None))

from PyQt4 import QtWebKit
