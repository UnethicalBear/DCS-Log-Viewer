import datetime
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys, os, json, re

class LogViewerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(LogViewerWindow, self).__init__()

        uic.loadUi("main.ui",self)
        
        self.infoDict = {}
        self.fileName = ""
       
        # self.mainTable  = self.findChild(QTableWidget, "mainTable")
        self.loadBtn    = self.findChild(QPushButton, "loadBtn")
        self.titleLabel = self.findChild(QLabel, "titleLabel")

        self.loadBtn.clicked.connect(self.loadFile)
        
        # Take & relinquish control, engines start, engines off
        self.showTC = self.findChild(QAction, "actionTake_Control")
        self.showUC = self.findChild(QAction, "actionUnder_control")
        self.showRC = self.findChild(QAction, "actionRelinquish")
        self.showES = self.findChild(QAction, "actionEngine_startup")
        self.showEO = self.findChild(QAction, "actionEngine_shutdown")
        
        # Shot, hit, kill, BDA, ai abort, pilot dead
        self.showShot       = self.findChild(QAction, "actionShot")
        self.showHit        = self.findChild(QAction, "actionHit")
        self.showKill       = self.findChild(QAction, "actionKill")
        self.showBDA        = self.findChild(QAction, "actionBDA")
        self.showAIA        = self.findChild(QAction, "actionAI_Abort_Mission")
        self.showPD         = self.findChild(QAction, "actionPilot_dead")
        self.showShotStart  = self.findChild(QAction, "actionStart_shooting")
        self.showShotEnd    = self.findChild(QAction, "actionEnd_shooting")
        
        # eject, crash, discard chair
        self.showPDC = self.findChild(QAction, "actionPilot_discard_chair")
        self.showEJT = self.findChild(QAction, "actionEject")
        self.showCRH = self.findChild(QAction, "actionCrash")
        
        # Takeoff and Landing
        self.showTO = self.findChild(QAction, "actionTakeoff")
        self.showLD = self.findChild(QAction, "actionLand")
        
        self.showSCR = self.findChild(QAction, "actionScore")
        self.showStart = self.findChild(QAction, "actionMission_start")
        self.showEnd = self.findChild(QAction, "actionMission_End")
        
        # Refresh / other settings
        self.findChild(QAction, "actionRefresh").triggered.connect(self.refreshTable)
        self.findChild(QAction, "actionSave").triggered.connect(self.save)
        self.findChild(QAction, "actionShow_all").triggered.connect(self.showAll)
        self.findChild(QAction, "actionShow_none").triggered.connect(self.showNone)
        
        self.showUnknown = self.findChild(QAction, "actionShowUnknown")
        
        self.reopenLast   = self.findChild(QAction, "actionReopen")
         
        self.allMyEvents  = self.findChild(QAction, "actionAll_my_events")
        self.onlyMyEvents = self.findChild(QAction, "actionOnly_my_events")
        
        self.saveLoadList = [
            self.showTC,
            self.showRC,
            self.showES,
            self.showEO,
            self.showShot,
            self.showHit,
            self.showKill,
            self.showBDA,
            self.showAIA,
            self.showPD,
            self.showPDC,
            self.showEJT,
            self.showCRH,
            self.showTO,
            self.showLD,
            self.showSCR,
            self.allMyEvents,
            self.onlyMyEvents,
            self.showStart,
            self.showEnd,
            self.showStart,
            self.showUC,
            self.showEnd,
            self.showEO,
            self.showES,
            self.showPD,
            self.showEJT,
            self.showPDC,
            self.showSCR,
            self.showShotStart,
            self.showShotEnd,
            self.showUnknown    
        ]
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        # Create a QTableWidget
        self.mainTable = QTableWidget(0, 5)  # 0 rows, 5 columns
        self.mainTable.setHorizontalHeaderLabels(["Event ID", "Timestamp", "Event Type", "Unit", "Target", "Weapon"])
        # self.mainTable.setSortingEnabled(True)
        self.mainTable.setEditTriggers(QAbstractItemView.NoEditTriggers)    
        # Add the table to the layout
        layout.addWidget(self.titleLabel)
        layout.addWidget(self.loadBtn)
        layout.addWidget(self.mainTable)
        
        central_widget.setLayout(layout)
       
        try:
            loadData = json.load(open("settings.json"))
            for i,value in enumerate(loadData["filters"]):
                self.saveLoadList[i].setChecked(value)
            try:
                self.reopenLast.setChecked(loadData.get("reopen", 1))
                if loadData["reopen"]:
                    self._loadFile(loadData["file"])
            except (FileNotFoundError, KeyError):
                pass
        except FileNotFoundError:
            pass
    
    def showAll(self):
        for x in self.saveLoadList:
            if x.objectName() not in ["actionAll_my_events","actionOnly_my_events"]:
                x.setChecked(1)
    
    def showNone(self):
        for x in self.saveLoadList:
            if x.objectName() not in ["actionAll_my_events","actionOnly_my_events"]:
                x.setChecked(0)
    
    def loadFile(self):
        # Funky windows thing we put here because otherwise it breaks
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        defaultDirectory = os.path.expanduser("~") + "\\Saved Games\\DCS\\Missions\\"
        fileName, _ = QFileDialog.getOpenFileName(self,"Select log import...",defaultDirectory,"Log Files (*.log);;All Files (*)", options=options)
        if fileName:
            self._loadFile(fileName)
            
    def _loadFile(self, fileName):
        self.fileName = fileName
        
        self.setWindowTitle(f"DCS Log Viewer - {fileName}")
        
        with open(fileName, "r") as f:
            fileString = f.read()
        
        # fileString=fileString.replace("\n", "") # get rid of newlines
        pattern = r'\[(\d+)\]'  # Matches [number] where number is one or more digits
        
        fileString = re.sub(pattern, r'"\1"', fileString)
        fileString = fileString.replace("[", "")            
        fileString = fileString.replace("]", "")
        fileString = fileString.replace("=", ":")
        fileString = re.sub(",\s*}", "\n}", fileString)
        fileString = fileString[fileString.find("{"):]

        self.infoDict = dict(json.loads(fileString))
        # json.dump(self.infoDict, open("tmp.json","w"), indent=4)

        self.populateTable(self.infoDict)
    
    def refreshTable(self):
        if len(self.infoDict):
            self.populateTable(self.infoDict)
    
    def populateTable(self, jsonDict:dict):
        showUnknownEvents = self.showUnknown.isChecked()
        self.playerCallsign = jsonDict["callsign"]
        
        self.mainTable.clear()
        self.mainTable.setRowCount(0)
        self.mainTable.setHorizontalHeaderLabels(["Event ID", "Timestamp", "Event Type", "Unit", "Target", "Weapon"])
        
        eventsList = jsonDict["events"]
        
        showEventsDictionary = {
            "took control":self.showTC.isChecked(),
            "takeoff":self.showTO.isChecked(),
            "land":self.showLD.isChecked(),
            
            "shot":self.showShot.isChecked(),
            "kill":self.showKill.isChecked(),
            "hit":self.showHit.isChecked(),
            "bda":self.showBDA.isChecked(),
            "start shooting":self.showShotStart.isChecked(),
            "end shooting":self.showShotEnd.isChecked(),
            
            "ai abort mission":self.showAIA.isChecked(),
            "relinquished":self.showRC.isChecked(),
            
            "engine startup":self.showES.isChecked(),
            "engine shutdown":self.showEO.isChecked(),
            
            "crash":self.showCRH.isChecked(),
            "pilot dead":self.showPD.isChecked(),
            "pilot discard chair":self.showPDC.isChecked(),
            "eject":self.showEJT.isChecked(),
            "score":self.showSCR.isChecked(),
            "mission start":self.showStart.isChecked(),
            "mission end":self.showEnd.isChecked(),
            "under control":self.showUC.isChecked(),
            
        }
        initialTime = 0
        
        try:
            initialTime = float(eventsList["1"]["ta"])
        except (KeyError, IndexError, ValueError, TypeError):
            pass # use intialtime = 0 as we couldn't get the inital time
        
        rowIndex = 0
        for event in eventsList:
            currentEvent = eventsList[event]
            
            if currentEvent["type"] == "pilot landing":
                continue
            
            if self.allMyEvents.isChecked():
                if currentEvent.get("initiatorPilotName", False) != self.playerCallsign:
                    continue
                    # this event wasn't from our player
            else:
                if self.onlyMyEvents.isChecked() and currentEvent.get("initiatorPilotName",False) != self.playerCallsign:
                    continue
                    # continue if this event isn't ours or we filter it out
                
                if not showEventsDictionary.get(currentEvent["type"], showUnknownEvents):
                    continue
            
            self.mainTable.setRowCount(self.mainTable.rowCount()+1)
            rowIndex = self.mainTable.rowCount()-1

            rowData = [currentEvent.get("event_id",""), 0, currentEvent["type"]]
            rowData[1] = datetime.datetime.fromtimestamp(float(currentEvent["t"]) + initialTime).strftime('%H:%M:%S')
            
            try:
                pilotStr = f"{currentEvent["initiator_unit_type"]} - ({currentEvent["initiatorPilotName"]})"
                if pilotStr.strip() == " - ()":
                    rowData.append("")
                else:
                    rowData.append(pilotStr)
            except KeyError:
                rowData.append("")
            
            try:
                if currentEvent["type"] == "land":
                    rowData.append(currentEvent["place"])
                else:
                    targetStr = f"{currentEvent["target_unit_type"]} - ({currentEvent["targetPilotName"]})"
                    if targetStr.strip() == " - ()":
                        rowData.append("")
                    else:
                        rowData.append(targetStr)
            except KeyError:
                rowData.append("")

            try:
                rowData.append(currentEvent["weapon"])
            except KeyError:
                rowData.append("")
                
            for i in range(len(rowData)):
                print(rowData)
                self.mainTable.setItem(rowIndex, i, QTableWidgetItem(str(rowData[i])))
                # self.mainTable.itemAt(rowIndex, i).setData(Qt.DisplayRole, rowData[i])

        self.mainTable.resizeColumnsToContents()  
        
    def save(self):
        settings = {
            "file":self.fileName,
            "filters":[x.isChecked() for x in self.saveLoadList],
            "reopen":self.reopenLast.isChecked()
        }
        json.dump(settings, open("settings.json", "w"), indent=4)
        
if __name__ == "__main__":                      
    app = QtWidgets.QApplication(sys.argv)
    window = LogViewerWindow()
    window.showMaximized()
    sys.exit(app.exec())