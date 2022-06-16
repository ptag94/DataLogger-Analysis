from modules import *

import pandas as pd

import numpy as np

class MainWindow (QMainWindow):

    def __init__(self):
        super().__init__()

        # Add style
        with open('theme/style.qss', 'r') as file:
            style = file.read()
        
        self.setStyleSheet(style)

        # Dict containing multiple experiences datas
        self.mainDataPack: dict = {}

        # State if time based data in plot
        self.timedData: bool = False

        # Name and size of the main window
        self.setWindowTitle('Plot Analysis')
        size = [1200, 700]
        self.resize(size[0], size[1])

        # Load experience button
        self.loadButton = QPushButton('Load')
        self.loadButton.setObjectName('MainUiButton')
        self.loadButton.clicked.connect(
            lambda: loadExperiences(self, self.mainDataPack)
        )

        # Save plot in png
        self.savePlot = QPushButton('Save')
        self.savePlot.clicked.connect(lambda: savePlot(self))
        self.savePlot.setObjectName('MainUiButton')

        # Plot Widget
        self.graph = pg.PlotWidget()
        self.graph.setBackground('w')
        self.graph.setLabel('left', 'Temperature')
        self.graph.setLabel('bottom', 'Time')
        self.graph.addLegend()
        self.graph.setMinimumWidth(size[0]*0.7)
        self.graph.setStyleSheet('\
            border: 3px solid gray;\
            border-radius: 6px;\
            margin-bottom: 10px\
        ')

        # Table with all loaded data
        self.tableau = QTableWidget(1, 2)
        self.tableau.setMinimumWidth(size[0]*0.3)
        self.rowSize = size[0]*0.3 * 0.49
        self.tableau.setColumnWidth(0, self.rowSize)
        self.tableau.setColumnWidth(1, self.rowSize)
        self.tableau.verticalHeader().setVisible(False)
        self.tableau.verticalHeader().setDefaultSectionSize(70)
        self.tableau.horizontalHeader().setVisible(False)
        self.tableau.setObjectName('MainTableExp')

        # Switch between timed based data and absolute time
        self.timedButton = QPushButton('Timed Data')
        self.timedButton.clicked.connect(
            lambda: enableTimedData(self)
        )
        self.timedButton.setObjectName('MainUiButton')

        # Base layout of the app
        self.baseLayout = QHBoxLayout()
        self.leftLayout = QVBoxLayout()

        # Add widgets to the left layout
        self.leftLayout.addWidget(self.loadButton)
        self.leftLayout.addWidget(self.savePlot)
        self.leftLayout.addWidget(self.tableau)
        self.leftLayout.addWidget(self.timedButton)

        # Add widget to the main layout
        self.baseLayout.addLayout(self.leftLayout)
        self.baseLayout.addWidget(self.graph)

        # Set the main widget
        self.widget = QWidget()
        self.widget.setLayout(self.baseLayout)
        self.setCentralWidget(self.widget)

    def deleteExperience(self):
        """Delete experience from the main DataPack when clicking on the 
        delete button.
        """

        # Get signal sender's objet
        button = self.sender()

        # Get the experience index from table
        expIndex = button.rowIndex

        # Get the name of the experience
        name = list(self.mainDataPack.keys())[expIndex]

        # Pop the experience from the main dataPack
        self.mainDataPack.pop(name)

        # Reload Option and plot widgets
        loadTable(self, self.mainDataPack)
        self.plot()

    def optionsExp(self):
        """Show the option window for a experience.
        """

        # Get signal sender's objet
        button = self.sender()

        # Get the experience index from table
        expIndex = button.rowIndex

        # Show option window
        self.optionsExpWindow = OptionsWindow(expIndex, self.mainDataPack)
        self.optionsExpWindow.show()

        # Connect the OptionsWindow's signal to a function changePlotStatus
        self.optionsExpWindow.signalData.connect(self.changePlotStatus)
        self.optionsExpWindow.signalAnalyse.connect(self.analyse)
        self.optionsExpWindow.signalColor.connect(self.changeColor)

    def changeColor(self, sendedData: list):
        """Change the color plot of a given channel

        Args:
            sendedData (list): Data sended by OptionWindow (Experience's name, Channel's name, DataLogger)
        """

        # Get names for dict's inputs
        expName: str = sendedData[0]
        channelName: str = sendedData[1]
        dataLogger: str = sendedData[2]

        # Pick color
        color = QColorDialog.getColor()

        # Set the color 
        self.mainDataPack[expName][dataLogger]['plot'][channelName]['color'] = color

        # Refresh plot widget
        self.plot()

    def analyse(self, sendedData: list):
        """Subtract to a given channel's data, a fited reference.

        Args:
            sendedData (list): Data sended by OptionWindow (Experience's name, Channel's name, DataLogger)
        """

        # Get names for dict's inputs
        expName = sendedData[0]
        channelName = sendedData[1]
        dataLogger = sendedData[2]
        
        # Select the reference for analyse
        selectedFile = MyDialog(
            'Window', 
            'Select reference', 
            self.mainDataPack.keys()
        )
        if selectedFile.exec() == QDialog.Accepted:
            referenceIndex = selectedFile.selectedRef()
            refName: str = list(self.mainDataPack.keys())[referenceIndex]
        
        # Reset graph
        self.graph.clear() 

        # Time based axis
        bottomAxis = TimeAxisItem(orientation='bottom')
        self.graph.setAxisItems(
            axisItems={'bottom': bottomAxis}
        )

        # Get reference fit
        # Offset base on acquisition start
        refOffset = self.mainDataPack[refName][dataLogger]['param'
                                                    ]['infos']['Acquisition started']

        # Convert in seconds
        refOffsetSecond = timeSeconds(
            pd.to_datetime(refOffset)
        )

        # Timed based abscisse
        refAbscisse = self.mainDataPack[refName][dataLogger
                                          ]['data'][channelName + '(s)'] + refOffsetSecond
        refOrdonne = self.mainDataPack[refName][dataLogger]['data'][channelName +
                                                                 '(°C)']
        
        # Fit reference
        varRefFit = np.polyfit(refAbscisse, refOrdonne, 6)
        polFitRef = np.poly1d(varRefFit)

        # Analysed curve
        # Offset base on acquisition start
        offset = self.mainDataPack[expName][dataLogger]['param'
                                                           ]['infos']['Acquisition started']

        # Convert in seconds
        offsetSecond = timeSeconds(
            pd.to_datetime(offset)
        )

        # Timed based abscisse
        abscisse = self.mainDataPack[expName][dataLogger
                                                 ]['data'][channelName + '(s)'] + offsetSecond
        ordonne = self.mainDataPack[expName][dataLogger]['data'][channelName +
                                                                    '(°C)']

        # Subtract fited ref and first value to start at 0
        analysedOrdonne = ordonne - polFitRef(abscisse)
        analysedOrdonne -= analysedOrdonne[0]

        # Plot
        self.graph.plot(abscisse, analysedOrdonne, pen=pg.mkPen(color='green'))

        

    def changePlotStatus(self, sendedData):
        """Change the plot status of a channel.

        Args:
            sendedData (list): 
                * Option Window object
                * Table experience's index
                * experience's name
                * DataLogger's Name
                * Channel's name
        """

        # Get plot state
        plotState = self.mainDataPack[sendedData[2]][
            sendedData[3]]['plot'][sendedData[4]]['checked']

        # Change the plot state
        if plotState == False:
            self.mainDataPack[sendedData[2]][sendedData[3]
                                             ]['plot'][sendedData[4]]['checked'] = True

        else:
            self.mainDataPack[sendedData[2]][sendedData[3]
                                             ]['plot'][sendedData[4]]['checked'] = False

        # Refresh option table and plot widget
        sendedData[0].setupTable(sendedData[1], self.mainDataPack)
        self.plot()

    def plot(self):

        # Clear graph widget
        self.graph.clear()

        # Iterate experience in main DataPack
        for exp in self.mainDataPack.keys():

            # Iterate Datalogger
            for dataLogger in self.mainDataPack[exp].keys():

                # Iterate channels
                for channel in self.mainDataPack[exp][dataLogger]['param'
                                                                  ]['Channels configuration'].keys():

                    # Get channel's name
                    name = self.mainDataPack[exp][dataLogger]['param'
                                                              ]['Channels configuration'][channel]['Probe Name']

                    # Check if needs to be plot
                    if self.mainDataPack[exp][dataLogger]['plot'][name
                                                                  ]['checked'] == True:

                        # Check if needs to be timed ploted
                        if self.timedData:

                            # Offset base on acquisition start
                            offset = self.mainDataPack[exp][dataLogger]['param'
                                                                        ]['infos']['Acquisition started']
                            
                            # Convert in seconds
                            # offsetSecond = pd.to_datetime(offset).timestamp()
                            offsetSecond = timeSeconds(
                                pd.to_datetime(offset)
                            )

                            # Timed based abscisse
                            abscisse = self.mainDataPack[exp][dataLogger
                                                              ]['data'][name + '(s)'] + offsetSecond

                            # Timed based axis
                            bottomAxis = TimeAxisItem(orientation='bottom')
                            self.graph.setAxisItems(
                                axisItems={'bottom': bottomAxis}
                            )
                        else:
                            # None timed based abscisse
                            abscisse = self.mainDataPack[exp][dataLogger
                                                              ]['data'][name + '(s)']

                            # None timed based axis
                            bottomAxis = pg.AxisItem('bottom')
                            bottomAxis.setLabel('Time')
                            bottomAxis.setTickSpacing(3600, 3600)
                            self.graph.setAxisItems(
                                axisItems={'bottom': bottomAxis}
                            )

                        # Get data
                        ordonne = self.mainDataPack[exp][dataLogger]['data'
                                                                     ][name + '(°C)']

                        # Get the ploted color
                        color = self.mainDataPack[exp][dataLogger]['plot'
                                                                   ][name]['color']

                        # Plot the item
                        self.graph.plot(
                            abscisse,
                            ordonne,
                            pen=pg.mkPen(color=color),
                            name=exp + '/' + name,
                            width=20
                        )


# Main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
