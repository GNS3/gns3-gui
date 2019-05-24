# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/grossmj/PycharmProjects/gns3-gui/gns3/modules/traceng/ui/traceng_node_preferences_page.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TraceNGNodePageWidget(object):
    def setupUi(self, TraceNGNodePageWidget):
        TraceNGNodePageWidget.setObjectName("TraceNGNodePageWidget")
        TraceNGNodePageWidget.resize(546, 455)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(TraceNGNodePageWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(TraceNGNodePageWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.uiTraceNGTreeWidget = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiTraceNGTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiTraceNGTreeWidget.setSizePolicy(sizePolicy)
        self.uiTraceNGTreeWidget.setMaximumSize(QtCore.QSize(160, 16777215))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.uiTraceNGTreeWidget.setFont(font)
        self.uiTraceNGTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.uiTraceNGTreeWidget.setIconSize(QtCore.QSize(32, 32))
        self.uiTraceNGTreeWidget.setRootIsDecorated(False)
        self.uiTraceNGTreeWidget.setObjectName("uiTraceNGTreeWidget")
        self.uiTraceNGTreeWidget.headerItem().setText(0, "1")
        self.uiTraceNGTreeWidget.header().setVisible(False)
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTraceNGInfoTreeWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.uiTraceNGInfoTreeWidget.sizePolicy().hasHeightForWidth())
        self.uiTraceNGInfoTreeWidget.setSizePolicy(sizePolicy)
        self.uiTraceNGInfoTreeWidget.setIndentation(10)
        self.uiTraceNGInfoTreeWidget.setAllColumnsShowFocus(True)
        self.uiTraceNGInfoTreeWidget.setObjectName("uiTraceNGInfoTreeWidget")
        self.uiTraceNGInfoTreeWidget.header().setVisible(False)
        self.verticalLayout.addWidget(self.uiTraceNGInfoTreeWidget)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.uiNewTraceNGPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiNewTraceNGPushButton.setObjectName("uiNewTraceNGPushButton")
        self.horizontalLayout_5.addWidget(self.uiNewTraceNGPushButton)
        self.uiEditTraceNGPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiEditTraceNGPushButton.setEnabled(False)
        self.uiEditTraceNGPushButton.setObjectName("uiEditTraceNGPushButton")
        self.horizontalLayout_5.addWidget(self.uiEditTraceNGPushButton)
        self.uiDeleteTraceNGPushButton = QtWidgets.QPushButton(self.layoutWidget)
        self.uiDeleteTraceNGPushButton.setEnabled(False)
        self.uiDeleteTraceNGPushButton.setObjectName("uiDeleteTraceNGPushButton")
        self.horizontalLayout_5.addWidget(self.uiDeleteTraceNGPushButton)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(TraceNGNodePageWidget)
        QtCore.QMetaObject.connectSlotsByName(TraceNGNodePageWidget)
        TraceNGNodePageWidget.setTabOrder(self.uiNewTraceNGPushButton, self.uiDeleteTraceNGPushButton)

    def retranslateUi(self, TraceNGNodePageWidget):
        _translate = QtCore.QCoreApplication.translate
        TraceNGNodePageWidget.setWindowTitle(_translate("TraceNGNodePageWidget", "TraceNG nodes"))
        TraceNGNodePageWidget.setAccessibleName(_translate("TraceNGNodePageWidget", "TraceNG node templates"))
        self.uiTraceNGInfoTreeWidget.headerItem().setText(0, _translate("TraceNGNodePageWidget", "1"))
        self.uiTraceNGInfoTreeWidget.headerItem().setText(1, _translate("TraceNGNodePageWidget", "2"))
        self.uiNewTraceNGPushButton.setText(_translate("TraceNGNodePageWidget", "&New"))
        self.uiEditTraceNGPushButton.setText(_translate("TraceNGNodePageWidget", "&Edit"))
        self.uiDeleteTraceNGPushButton.setText(_translate("TraceNGNodePageWidget", "&Delete"))

