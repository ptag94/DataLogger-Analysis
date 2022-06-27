from PySide6.QtWidgets import *
from PySide6.QtCore import *

from . functions import *
from . subClasses import *

import random as rd

import pyqtgraph as pg


def loadExperiences(self, DP: dict):
    """Add all data in the main DataPack:
        * param : header of the data logger
        * data : data from the data logger
        * plot : param for ploting

    Args:
        DP (dict): main DataPack
    """

    # Get files path from the user
    filesPath: list = QFileDialog.getOpenFileNames()[0]

    # Get experience's name
    expName: str = requiredExpName(self)

    # List of DataLoggers' names
    dataLoggerNames: list = getDataLoggersNames(filesPath)

    # List of Json data and path of the experience
    jsonPath, jsonList = dataLoggerJson(filesPath)

    # New experience key in the main DataPack
    DP[expName] = {}

    # List of the data from both dataLoggers
    expData: DataFrame = loadData(filesPath, jsonPath)

    # Enumerate index/names in dataLoggerNames list
    for index, dataLogger in enumerate(dataLoggerNames):

        # Create new entry in mainDataPack dict : DataLogger
        DP[expName][dataLogger] = {}

        # Create 3 news entries in DataLogger
        DP[expName][dataLogger]['param'] = jsonList[index]
        DP[expName][dataLogger]['data'] = expData[index]
        DP[expName][dataLogger]['plot'] = {}

        # Iterate channels
        for channel in DP[expName][dataLoggerNames[index]]['param'
                                                           ]['Channels configuration']:

            # Channel's name
            name = DP[expName][dataLoggerNames[index]
                               ]['param']['Channels configuration'][channel]['Probe Name']

            # New entry if the channel is plot and the random color used
            DP[expName][dataLoggerNames[index]]['plot'][name] = {}
            DP[expName][dataLoggerNames[index]
                        ]['plot'][name]['checked'] = False
            DP[expName][dataLoggerNames[index]
                        ]['plot'][name]['color'] = (rd.random() * 255, rd.random() * 255, rd.random() * 255)

    # Refresh table
    loadTable(self, DP)


def getDataLoggersNames (filesPath: list) -> list:
    dataLoggersNames: list = []
    for path in filesPath:
        fileName = path.split('/')[-1]
        dataLogger = fileName.split('_')[1][-1]
        dataLoggersNames.append('DataLogger' + dataLogger)

    return dataLoggersNames


def requiredExpName(self) -> str:
    """Asks for the experimentes' name

    Returns:
        str: name of the experience in the table
    """

    name = QInputDialog.getText(
        self,
        'Load experience',
        'Enter experience\'s name : '
    )

    return name[0]


def loadTable(self, DP: dict):
    """Generate the table containing experiences' button and del button

    Args:
        DP (dict): main DataPack
    """

    # Number of loaded experiences
    numberExp: int = len(DP.keys())

    # Set table row count of the number of experiences
    self.tableau.setRowCount(numberExp)

    # Iterate a list from 0 to the count of experiences
    for index in range(numberExp):

        # Set experience name
        self.name = list(DP.keys())[index]

        # Set experience button 
        self.expItem = QWidget()
        self.expButton = RowButton(index, self.name, parent=self.tableau)
        self.expButton.setObjectName('ExpButton')
        self.expButton.setMaximumWidth(self.rowSize)
        self.expButton.setMinimumWidth(self.rowSize)

        self.layoutExpButton = QHBoxLayout()
        self.layoutExpButton.addWidget(self.expButton)
        self.layoutExpButton.setAlignment(Qt.AlignHCenter)
        self.layoutExpButton.setContentsMargins(0, 0, 0, 0)
        self.expItem.setLayout(self.layoutExpButton)

        # Set suppr button
        self.supprItem = QWidget()
        self.supprItem.setObjectName('SupprButtonBackGround')
        self.supprButton = RowButton(index, parent=self.tableau)
        self.supprButton.setMaximumSize(30,30)
        self.supprButton.setObjectName('SupprButton')

        self.layoutSupprButton = QHBoxLayout()
        self.layoutSupprButton.addWidget(self.supprButton)
        self.layoutSupprButton.setAlignment(Qt.AlignHCenter)
        self.layoutSupprButton.setContentsMargins(0, 0, 0, 0)
        self.supprItem.setLayout(self.layoutSupprButton)

        # Set item in table
        self.tableau.setCellWidget(0 + index, 0, self.expItem)
        self.tableau.setCellWidget(0 + index, 1, self.supprItem)

        # Connect button to fuction
        self.supprButton.clicked.connect(self.deleteExperience)
        self.expButton.clicked.connect(self.optionsExp)


def savePlot(self):
    """Save plot
    """

    # Get file path to the saving file
    filePath = QFileDialog.getSaveFileName(
        self, 
        'Save as', 
        filter='Images (*png)'
    )

    # Check if png is entered
    if filePath[0].split("/")[-1][-4:] != '.png':
        fileName = filePath[0] + '.png'
    else:
        fileName = filePath[0]

    # Save the plot
    exporter = pg.exporters.ImageExporter(self.graph.plotItem)
    exporter.export(fileName)
