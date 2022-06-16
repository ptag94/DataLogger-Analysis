from PySide6.QtWidgets import *
from PySide6.QtCore import *

from pandas import DataFrame

from . subClasses import *


class OptionsWindow(QWidget):

    # Signal object
    signalData = Signal(object)
    signalAnalyse = Signal(object)
    signalColor = Signal(object)

    def __init__(self, index: int, mainDataPack: dict):
        super(OptionsWindow, self).__init__()

        # Size of the option window
        self.resize(500, 600)

        # Layout and table for each dataLogger
        self.layout = QVBoxLayout()
        self.tableauDataLogger1 = QTableWidget(1, 4)
        self.tableauDataLogger1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableauDataLogger1.verticalHeader().setVisible(False)
        self.tableauDataLogger1.horizontalHeader().setVisible(False)
        self.tableauDataLogger1.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOn
        )
        self.tableauDataLogger1.setObjectName('OptionsTable')

        self.tableauDataLogger2 = QTableWidget(1, 4)
        self.tableauDataLogger2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableauDataLogger2.verticalHeader().setVisible(False)
        self.tableauDataLogger2.horizontalHeader().setVisible(False)
        self.tableauDataLogger2.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOn
        )
        self.tableauDataLogger2.setObjectName('OptionsTable')

        self.layout.addWidget(self.tableauDataLogger1)
        self.layout.addWidget(self.tableauDataLogger2)

        self.setLayout(self.layout)

        # Refresh table
        self.setupTable(index, mainDataPack)

    def setupTable(self, index: int, mainDataPack: dict):
        """Load the table containing each channel

        Args:
            index (int): experience index
            mainDataPack (dict): main Data Pack
        """

        # Get index and experience name
        self.index = index
        self.expName = list(mainDataPack.keys())[index]

        # DataLoggers' names
        dataLogger: list = ['DataLogger1', 'DataLogger2']

        # Iterate index and name in list of dataLoggers' names
        for index, dataLoggerName in enumerate(dataLogger):

            # Dict containing all channels configurations
            nameDict: dict = mainDataPack[self.expName][dataLoggerName
                                                        ]['param']['Channels configuration']

            # Data of a datalogger
            data: DataFrame = mainDataPack[self.expName][dataLoggerName
                                                         ]['data']

            # List of non over loads channels
            nonOverloadChannels: list = [
                nameDict[var]['Probe Name'] for var in nameDict.keys()
                if data[nameDict[var]['Probe Name'] + '(°C)'][0] != 1e+10
            ]

            # Table objet containing channels
            table = self.layout.itemAt(index).widget()

            # Set the row count of the table
            table.setRowCount(len(nonOverloadChannels))

            # Initialize at row number 0
            row = 0

            # Iterate each non over load channels
            for names in nonOverloadChannels:

                # Create table item

                nameItem = QWidget()
                name = QLabel(names)

                self.layoutName = QHBoxLayout()
                self.layoutName.addWidget(name)
                self.layoutName.setAlignment(Qt.AlignHCenter)
                self.layoutName.setContentsMargins(0, 0, 0, 0)
                nameItem.setLayout(self.layoutName)

                # Analyse button
                analyseItem = QWidget()
                analyseButton = RowButton(
                    self.index,
                    name='Analyse', 
                    channelName=names, 
                    dataLogger=dataLoggerName,
                    parent=table
                )

                self.layoutAnalyseButton = QHBoxLayout()
                self.layoutAnalyseButton.addWidget(analyseButton)
                self.layoutAnalyseButton.setAlignment(Qt.AlignHCenter)
                self.layoutAnalyseButton.setContentsMargins(0, 0, 0, 0)
                analyseItem.setLayout(self.layoutAnalyseButton)

                # Options color for the ploted channel
                channelOptions = QWidget()
                optionButton = RowButton(
                    self.index,
                    dataLogger=dataLoggerName, 
                    name='Couleur',
                    channelName=names, 
                    parent=table
                )

                self.layoutOptionButton = QHBoxLayout()
                self.layoutOptionButton.addWidget(optionButton)
                self.layoutOptionButton.setAlignment(Qt.AlignHCenter)
                self.layoutOptionButton.setContentsMargins(0, 0, 0, 0)
                channelOptions.setLayout(self.layoutOptionButton)

                # Check box for plot channel
                graphItem = QWidget()
                graphCheckBox = RowCheckBox(names, dataLogger=dataLoggerName)

                # When refresh set the check box checked if it was already checked
                state = mainDataPack[self.expName][dataLoggerName]['plot'][names]['checked']
                if state:
                    graphCheckBox.setCheckState(Qt.CheckState.Checked)

                layoutCheckBox = QHBoxLayout()
                layoutCheckBox.addWidget(graphCheckBox)
                layoutCheckBox.setAlignment(Qt.AlignHCenter)
                layoutCheckBox.setContentsMargins(0, 0, 0, 0)
                graphItem.setLayout(layoutCheckBox)

                # Set items in table
                table.setCellWidget(row, 0, nameItem)
                table.setCellWidget(row, 1, channelOptions)
                table.setCellWidget(row, 2, analyseItem)
                table.setCellWidget(row, 3, graphItem)

                # Connect the signal
                graphCheckBox.clicked.connect(self.sendSignal)
                analyseButton.clicked.connect(self.sendAnalyse)
                optionButton.clicked.connect(self.sendColor)

                # Increase row index
                row += 1

    def sendSignal(self):
        """Signal send to MainWindow"""

        # Retrieve sender object
        checkButton = self.sender()

        # Send Data
        self.signalData.emit(
            [
                self,
                self.index,
                self.expName,
                checkButton.dataLogger,
                checkButton.name
            ]
        )

    def sendAnalyse(self):
        """Signal send to MainWindow"""

        # Retrieve sender object
        analyseButton = self.sender()

        # Send Data
        self.signalAnalyse.emit(
            [
                self.expName,
                analyseButton.channelName,
                analyseButton.dataLogger
            ]
        )

    def sendColor(self):
        """Signal send to MainWindow"""

        colorButton = self.sender()

        self.signalColor.emit(
            [
                self.expName,
                colorButton.channelName,
                colorButton.dataLogger
                
            ]
        )
