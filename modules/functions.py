import json
from pandas import DataFrame, read_csv, Series, concat
from PySide6.QtWidgets import *


def dataLoggerJson(filesPath: list):
    """Generate json files of the data loggers

    Args:
        filesPath (list): files path of data

    Returns:
        list: list of json files and json filePath
    """

    # Name for json files
    indexName: int = 1

    # List json files path
    jsonPath: list = []

    # List containing the two json
    jsonList: list = []

    for filePath in filesPath:

        # Load the file and stock in a list
        file = open(filePath, 'r')
        data = file.readlines()
        file.close()

        # Stock header in a list
        header: list = []
        index: int = 0
        while data[index][0] == '#':
            header.append(data[index][2:])
            index += 1

        # Global dict of the file which contains Infos and channel
        # Configuration
        dataDict: dict = {}

        # List that stocks each channel configuration index
        configIndex: list = [
            index for index, string in enumerate(header) 
            if 'Configuration' in string
        ]

        # Store infos in a dict
        infos: dict = {}
        for index, integer in enumerate(header[:configIndex[0]]):

            # Cut the line to fit in a dict
            splitedItem: list = header[index].split(':', 1)

            # Exception in lines without ":"
            try:
                # Suppr spaces
                correctedItem = correctItem(splitedItem)

                # Add new entry in the infos dict
                infos[correctedItem[0]] = correctedItem[1]

            except IndexError:
                # Split line at the " at "
                splitedItem: list = header[index].split(' at ', 1)

                # Suppr spaces
                correctedItem = correctItem(splitedItem)

                # Add new entry in the infos dict
                infos[correctedItem[0]] = correctedItem[1]
        
        # Add Acquisition started time
        splitedItem: list = header[-1].split(' at : ')
        infos[splitedItem[0]] = splitedItem[1][:-1]

        # First channel configuration index
        channelConf = header[configIndex[0]:-1]

        # Dict contains all channels configuration
        configDict = {}

        # Dict contains the configuration of one dict
        channelDict = {}

        # Read all the configuration lines 
        for string in channelConf:

            # Add dict entries when hit "Configuration of channel XXXX"
            if 'Configuration' in string:

                # Case for the first channel
                if len(channelDict.keys()) == 0:
                    name = string[-8:-4]

                else:
                    # Add channel configuration in dict
                    configDict[name] = channelDict

                    # Reset the channel configuration
                    channelDict = {}

                    # Change name of the current channel
                    name = string[-8:-4]
            
            else:
                # Split item to create a dict readeable entrie
                splitedItem: list = string.split(':', 1)

                # Suppr spaces
                correctedItem = correctItem(splitedItem)

                # Add a configuration line of the channel
                channelDict[correctedItem[0][5:]] = correctedName(correctedItem[1])
        
        # Add the last channel configuration
        configDict[name] = channelDict

        # Add the infos and channels configuration dicts 
        dataDict['infos'] = infos
        dataDict['Channels configuration'] = configDict

        # Layout for saving in json
        jsonData = json.dumps(dataDict, indent=10)

        # Save in json
        # file = open("data/json/DataLogger" + str(indexName) + ".json", 'w')
        jsonName: str = "data/json/DataLogger" + str(indexName) + ".json"
        jsonPath.append(jsonName)
        with open(jsonName, 'w') as f:
            f.write(jsonData)

        # Add dict to the returned dict
        jsonList.append(dataDict)

        # Add 1 to name the dataLogger 2
        indexName += 1

    return jsonPath, jsonList


def correctItem(items: str) -> list:
    """Delete unnecessary spaces in text 

    Args:
        items (str): item from json

    Returns:
        str: corrected item
    """

    # List containing corrected item
    correctedItem = []

    # Iterate items
    for i in items:
        try:
            correctedItem.append(" ".join(i.split()))
        except TypeError:
            correctedItem.append(i)

    return correctedItem


def correctedName(item: str) -> str:
    """delete information in name

    Args:
        item (str): names 

    Returns:
        str: corrected name
    """

    try:
        return item.split()[0]
    except TypeError:
        return item

def loadData (filesPath: list, jsonsPath: list) -> list:
    """Load headers and data of dataLoggers

    Args:
        filesPath (list): files path for the data
        jsonsPath (list): jsons files path

    Returns:
        list: contains a dict for each dataLogger
    """

    # Number of dataLoggers
    # dataLogger: list = [0,1]
    lenDataLogger: int = len(filesPath)

    # List of dataLoggers' data
    dataList: list = []

    # Iterate dataLogger's index
    for index in range(lenDataLogger):

        # Get file and json path
        filePath: str = filesPath[index]
        jsonPath: str = jsonsPath[index]

        # Load dataLogger's json
        with open(jsonPath, 'r') as f:
            settings = json.load(f)

        # list of names for the pandas DataFrame
        colNames = []

        # Iterate channel and add column name
        for channel in settings['Channels configuration'].keys():
            colNames.append(settings['Channels configuration']
                        [channel]['Probe Name'] + '(s)')
            colNames.append(settings['Channels configuration']
                        [channel]['Probe Name'] + '(ohm)')
            colNames.append(settings['Channels configuration']
                        [channel]['Probe Name'] + '(°C)')

        # Load dataLoggers' data
        data = read_csv(
            filePath,
            comment="#",
            sep="\t",
            header=None
        )

        # Set columns names
        data.columns = colNames

        # Add data in the final list
        dataList.append(data)

    return dataList

def enableTimedData (self):
    """Enable the timed data in the graph
    """

    # Change timedData bool
    if self.timedData:
        self.timedData = False
    else:
        self.timedData = True
    
    # Refresh plot
    self.plot()

def timeSeconds(dateTime):
    """Convert DateTime to seconds"""
    hours = dateTime.hour
    minutes = dateTime.minute
    second = dateTime.second
    microsecond = dateTime.microsecond

    converted = hours * 3600 + minutes * 60 + second + microsecond * 1e-6

    return converted


def saveCsv(self):

    # Get file path to the saving file
    filePath = QFileDialog.getSaveFileName(
        self,
        'Save as',
        filter='File (*csv)'
        )

    # Check if png is entered
    if filePath[0].split("/")[-1][-4:] != '.csv':
        fileName = filePath[0] + '.csv'
    else:
        fileName = filePath[0]

    saveData = DataFrame()

    for expName in self.mainDataPack.keys():
        for dataLogger in self.mainDataPack[expName]:
            for channel in self.mainDataPack[expName][dataLogger]['param'
                                                                    ]['Channels configuration'].keys():

                # Get channel's name
                name = self.mainDataPack[expName][dataLogger]['param'
                                                                ]['Channels configuration'][channel]['Probe Name']

                # Check if ploted
                if self.mainDataPack[expName][dataLogger]['plot'][name
                                                                    ]['checked'] == True:
                    data = self.mainDataPack[expName][dataLogger]['data'][name + '(s)']
                    series = Series(data, name=name + '(s)')

                    saveData = concat([saveData, series], axis=1)

                    data = self.mainDataPack[expName][dataLogger]['data'][name +
                                                                          '(°C)']
                    series = Series(data, name=name + '(°C)')

                    saveData = concat([saveData, series], axis=1)

    saveData.to_csv(fileName)

