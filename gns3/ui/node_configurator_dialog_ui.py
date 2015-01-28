# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/node_configurator_dialog.ui'
#
# Created: Sun Aug 17 18:05:14 2014
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


class Ui_NodeConfiguratorDialog(object):

    def setupUi(self, NodeConfiguratorDialog):
        NodeConfiguratorDialog.setObjectName(_fromUtf8("NodeConfiguratorDialog"))
        NodeConfiguratorDialog.resize(689, 454)
        self.gridlayout = QtGui.QGridLayout(NodeConfiguratorDialog)
        self.gridlayout.setObjectName(_fromUtf8("gridlayout"))
        self.splitter = QtGui.QSplitter(NodeConfiguratorDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.uiNodesTreeWidget = QtGui.QTreeWidget(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiNodesTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiNodesTreeWidget.setSizePolicy(sizePolicy)
        self.uiNodesTreeWidget.setObjectName(_fromUtf8("uiNodesTreeWidget"))
        self.uiNodesTreeWidget.header().setVisible(False)
        self.verticalLayout = QtGui.QWidget(self.splitter)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.vboxlayout = QtGui.QVBoxLayout(self.verticalLayout)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setObjectName(_fromUtf8("vboxlayout"))
        self.uiTitleLabel = QtGui.QLabel(self.verticalLayout)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.uiTitleLabel.setFont(font)
        self.uiTitleLabel.setFrameShape(QtGui.QFrame.Box)
        self.uiTitleLabel.setFrameShadow(QtGui.QFrame.Sunken)
        self.uiTitleLabel.setTextFormat(QtCore.Qt.PlainText)
        self.uiTitleLabel.setObjectName(_fromUtf8("uiTitleLabel"))
        self.vboxlayout.addWidget(self.uiTitleLabel)
        self.uiConfigStackedWidget = QtGui.QStackedWidget(self.verticalLayout)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiConfigStackedWidget.sizePolicy().hasHeightForWidth())
        self.uiConfigStackedWidget.setSizePolicy(sizePolicy)
        self.uiConfigStackedWidget.setFrameShape(QtGui.QFrame.Box)
        self.uiConfigStackedWidget.setFrameShadow(QtGui.QFrame.Sunken)
        self.uiConfigStackedWidget.setObjectName(_fromUtf8("uiConfigStackedWidget"))
        self.uiEmptyPageWidget = QtGui.QWidget()
        self.uiEmptyPageWidget.setObjectName(_fromUtf8("uiEmptyPageWidget"))
        self.vboxlayout1 = QtGui.QVBoxLayout(self.uiEmptyPageWidget)
        self.vboxlayout1.setSpacing(0)
        self.vboxlayout1.setContentsMargins(0, 4, 0, 0)
        self.vboxlayout1.setObjectName(_fromUtf8("vboxlayout1"))
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem)
        self.textLabel = QtGui.QLabel(self.uiEmptyPageWidget)
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel.setObjectName(_fromUtf8("textLabel"))
        self.vboxlayout1.addWidget(self.textLabel)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem1)
        self.uiConfigStackedWidget.addWidget(self.uiEmptyPageWidget)
        self.vboxlayout.addWidget(self.uiConfigStackedWidget)
        self.gridlayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.uiButtonBox = QtGui.QDialogButtonBox(NodeConfiguratorDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Reset)
        self.uiButtonBox.setObjectName(_fromUtf8("uiButtonBox"))
        self.gridlayout.addWidget(self.uiButtonBox, 1, 0, 1, 1)

        self.retranslateUi(NodeConfiguratorDialog)
        self.uiConfigStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(NodeConfiguratorDialog)

    def retranslateUi(self, NodeConfiguratorDialog):
        NodeConfiguratorDialog.setWindowTitle(_translate("NodeConfiguratorDialog", "Node configurator", None))
        self.uiNodesTreeWidget.headerItem().setText(0, _translate("NodeConfiguratorDialog", "Nodes", None))
        self.uiTitleLabel.setText(_translate("NodeConfiguratorDialog", "Node Configuration", None))
        self.textLabel.setText(_translate("NodeConfiguratorDialog", "Please select a node in the list \n"
                                          "to display the configuration page.", None))

from . import resources_rc
