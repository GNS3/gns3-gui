# -*- coding: utf-8 -*-
from PyQt4.QtGui import QWidget

# this widget was promoted on Creator, must use absolute imports
from gns3.ui.cloud_inspector_view_ui import Ui_CloudInspectorView


class CloudInspectorView(QWidget, Ui_CloudInspectorView):
    """

    """
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.setupUi(self)