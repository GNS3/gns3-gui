# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/ui/node_properties_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NodePropertiesDialog(object):
    def setupUi(self, NodePropertiesDialog):
        NodePropertiesDialog.setObjectName("NodePropertiesDialog")
        NodePropertiesDialog.resize(689, 454)
        self.gridlayout = QtWidgets.QGridLayout(NodePropertiesDialog)
        self.gridlayout.setObjectName("gridlayout")
        self.splitter = QtWidgets.QSplitter(NodePropertiesDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiNodesTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiNodesTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiNodesTreeWidget.setSizePolicy(sizePolicy)
        self.uiNodesTreeWidget.setObjectName("uiNodesTreeWidget")
        self.uiNodesTreeWidget.header().setVisible(False)
        self.verticalLayout = QtWidgets.QWidget(self.splitter)
        self.verticalLayout.setObjectName("verticalLayout")
        self.vboxlayout = QtWidgets.QVBoxLayout(self.verticalLayout)
        self.vboxlayout.setContentsMargins(0, 0, 0, 0)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName("vboxlayout")
        self.uiTitleLabel = QtWidgets.QLabel(self.verticalLayout)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.uiTitleLabel.setFont(font)
        self.uiTitleLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.uiTitleLabel.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.uiTitleLabel.setTextFormat(QtCore.Qt.PlainText)
        self.uiTitleLabel.setObjectName("uiTitleLabel")
        self.vboxlayout.addWidget(self.uiTitleLabel)
        self.uiConfigStackedWidget = QtWidgets.QStackedWidget(self.verticalLayout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiConfigStackedWidget.sizePolicy().hasHeightForWidth())
        self.uiConfigStackedWidget.setSizePolicy(sizePolicy)
        self.uiConfigStackedWidget.setFrameShape(QtWidgets.QFrame.Box)
        self.uiConfigStackedWidget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.uiConfigStackedWidget.setObjectName("uiConfigStackedWidget")
        self.uiEmptyPageWidget = QtWidgets.QWidget()
        self.uiEmptyPageWidget.setObjectName("uiEmptyPageWidget")
        self.vboxlayout1 = QtWidgets.QVBoxLayout(self.uiEmptyPageWidget)
        self.vboxlayout1.setContentsMargins(0, 4, 0, 0)
        self.vboxlayout1.setSpacing(0)
        self.vboxlayout1.setObjectName("vboxlayout1")
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem)
        self.textLabel = QtWidgets.QLabel(self.uiEmptyPageWidget)
        self.textLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel.setObjectName("textLabel")
        self.vboxlayout1.addWidget(self.textLabel)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem1)
        self.uiConfigStackedWidget.addWidget(self.uiEmptyPageWidget)
        self.vboxlayout.addWidget(self.uiConfigStackedWidget)
        self.gridlayout.addWidget(self.splitter, 0, 0, 1, 1)
        self.uiButtonBox = QtWidgets.QDialogButtonBox(NodePropertiesDialog)
        self.uiButtonBox.setOrientation(QtCore.Qt.Horizontal)
        self.uiButtonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Help|QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Reset)
        self.uiButtonBox.setObjectName("uiButtonBox")
        self.gridlayout.addWidget(self.uiButtonBox, 1, 0, 1, 1)

        self.retranslateUi(NodePropertiesDialog)
        self.uiConfigStackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(NodePropertiesDialog)

    def retranslateUi(self, NodePropertiesDialog):
        _translate = QtCore.QCoreApplication.translate
        NodePropertiesDialog.setWindowTitle(_translate("NodePropertiesDialog", "Node properties"))
        self.uiNodesTreeWidget.headerItem().setText(0, _translate("NodePropertiesDialog", "Nodes"))
        self.uiTitleLabel.setText(_translate("NodePropertiesDialog", "Node Configuration"))
        self.textLabel.setText(_translate("NodePropertiesDialog", "Please select a node in the list \n"
"to display the configuration page."))

from . import resources_rc
