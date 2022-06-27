from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import pyqtgraph as pg
import datetime
import pytz

class RowButton (QPushButton):

    def __init__(
        self, 
        index: int, 
        name: str = '', 
        channelName: str='',
        dataLogger: str='',
        *args, 
        **kwargs
    ):
        super(RowButton, self).__init__(*args, **kwargs)

        # Row index of the button in table
        self.channelName = channelName
        self.dataLogger = dataLogger
        self.rowIndex = index
        self.setText(name)


class RowCheckBox(QCheckBox):

    def __init__(self, name: str, dataLogger=''):
        super(RowCheckBox, self).__init__()

        self.name = name
        self.dataLogger = dataLogger


class MyDialog(QDialog):
    def __init__(self,  title: str, message: str, expNames: list, parent=None):
        super(MyDialog, self).__init__(parent=parent)

        self.selectedExp = None

        form = QFormLayout(self)
        form.addRow(QLabel(message))
        self.setWindowTitle(title)

        for index, name in enumerate(expNames):
            expNameButton = RowButton(index, name=name)
            expNameButton.clicked.connect(self.getExpIndex)
            form.addRow(expNameButton)

    def getExpIndex(self):
        button = self.sender()

        self.selectedExp = button.rowIndex

        super().accept()

    def selectedRef(self):
        return self.selectedExp


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text='Time', units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return [datetime.datetime.fromtimestamp(value, pytz.timezone("UTC")).strftime("%H:%M") for value in values]
