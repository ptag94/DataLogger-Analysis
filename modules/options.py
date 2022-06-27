from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from pandas import DataFrame

from . subClasses import *


class OptionsWindow(QWidget):

    # Signal object
    signalData = Signal(object)
    signalAnalyse = Signal(object)
    signalColor = Signal(object)
    signalPsd = Signal(object)

    def __init__(self, index: int, mainDataPack: dict):
        super(OptionsWindow, self).__init__()

        # Add style
        with open('theme/mainStyle.qss', 'r') as file:
            style = file.read()

        self.setStyleSheet(style)

        # Size of the option window
        self.resize(500, 600)

        # Get expName and Dataloggers names
        self.expName: str = list(mainDataPack.keys())[index]
        self.dataLoggers: list = list(mainDataPack[self.expName].keys())

        self.layout = QVBoxLayout()

        for indexDL, names in enumerate(self.dataLoggers):

            # Layout and table for each dataLogger
            self.tableauDataLogger = QTableWidget(1, 5)
            self.tableauDataLogger.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tableauDataLogger.verticalHeader().setVisible(False)
            self.tableauDataLogger.horizontalHeader().setVisible(False)
            self.tableauDataLogger.setVerticalScrollBarPolicy(
                Qt.ScrollBarAlwaysOn
            )
            self.tableauDataLogger.setObjectName('OptionsTable')

            # GroupBox
            groupBoxData = QGroupBox('DataLogger ' + names[-1])
            self.layoutGB = QVBoxLayout()
            self.layoutGB.addWidget(self.tableauDataLogger)
            groupBoxData.setLayout(self.layoutGB)

            self.layout.addWidget(groupBoxData)

        # self.layout.addWidget(self.tableauDataLogger1)
        # self.layout.addWidget(self.tableauDataLogger2)
        # self.layout.addWidget(groupBoxData2)

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
        dataLogger: list = list(mainDataPack[self.expName].keys())

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
            groupbox = self.layout.itemAt(index).widget()
            layoutGB = groupbox.layout()
            table = layoutGB.itemAt(0).widget()

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
                analyseButton.setObjectName('optionsButton')

                self.layoutAnalyseButton = QHBoxLayout()
                self.layoutAnalyseButton.addWidget(analyseButton)
                self.layoutAnalyseButton.setAlignment(Qt.AlignHCenter)
                self.layoutAnalyseButton.setContentsMargins(0, 0, 0, 0)
                analyseItem.setLayout(self.layoutAnalyseButton)

                # psd button
                psdItem = QWidget()
                psdButton = RowButton(
                    self.index,
                    name='PSD',
                    channelName=names,
                    dataLogger=dataLoggerName,
                    parent=table
                )
                psdButton.setObjectName('optionsButton')

                self.layoutPsdButton = QHBoxLayout()
                self.layoutPsdButton.addWidget(psdButton)
                self.layoutPsdButton.setAlignment(Qt.AlignHCenter)
                self.layoutPsdButton.setContentsMargins(0, 0, 0, 0)
                psdItem.setLayout(self.layoutPsdButton)

                # Options color for the ploted channel
                channelOptions = QWidget()
                optionButton = RowButton(
                    self.index,
                    dataLogger=dataLoggerName, 
                    name='Couleur',
                    channelName=names, 
                    parent=table
                )
                optionButton.setObjectName('optionsButton')

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
                table.setCellWidget(row, 3, psdItem)
                table.setCellWidget(row, 4, graphItem)

                # Connect the signal
                graphCheckBox.clicked.connect(self.sendSignal)
                analyseButton.clicked.connect(self.sendAnalyse)
                optionButton.clicked.connect(self.sendColor)
                psdButton.clicked.connect(self.sendPsd)

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

    def sendPsd(self):
        """Signal send to MainWindow"""

        button = self.sender()

        self.signalPsd.emit(
            [
                self.expName,
                button.channelName,
                button.dataLogger

            ]
        )
