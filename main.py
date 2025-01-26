from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys, os, json, re

class LogViewerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(LogViewerWindow, self).__init__()

        uic.loadUi("main.ui",self)
        # self.setFixedSize(self.size())
        
        self.infoDict = {}
        self.fileName = ""
        
       
        self.mainTable  = self.findChild(QTableWidget, "mainTable")
        self.loadBtn    = self.findChild(QPushButton, "loadBtn")
        self.titleLabel = self.findChild(QLabel, "titleLabel")

        self.loadBtn.clicked.connect(self.loadFile)
        
        # Take & relinquish control, engines start, engines off
        self.showTC = self.findChild(QAction, "actionTake_Control")
        self.showRC = self.findChild(QAction, "actionRelinquish")
        self.showES = self.findChild(QAction, "actionEngine_startup")
        self.showEO = self.findChild(QAction, "actionEngine_shutdown")
        
        # Shot, hit, kill, BDA, ai abort, pilot dead
        self.showShot = self.findChild(QAction, "actionShot")
        self.showHit = self.findChild(QAction, "actionHit")
        self.showKill = self.findChild(QAction, "actionKill")
        self.showBDA = self.findChild(QAction, "actionBDA")
        self.showAIA = self.findChild(QAction, "actionAI_Abort_Mission")
        self.showPD = self.findChild(QAction, "actionPilot_dead")
        
        # eject, crash, discard chair
        self.showPDC = self.findChild(QAction, "actionPilot_discard_chair")
        self.showEJT = self.findChild(QAction, "actionEject")
        self.showCRH = self.findChild(QAction, "actionCrash")
        
        # Takeoff and Landing
        self.showTO = self.findChild(QAction, "actionTakeoff")
        self.showLD = self.findChild(QAction, "actionLand")
        
        self.showSCR = self.findChild(QAction, "actionScore")
        
        # Refresh / other settings
        self.findChild(QAction, "actionRefresh").triggered.connect(self.refreshTable)
        self.findChild(QAction, "actionSave").triggered.connect(self.save)
        
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
            self.reopenLast,
        ]
        
        try:
            loadData = json.load(open("settings.json"))
            
            for i,value in enumerate(loadData["filters"]):
                self.saveLoadList[i].setChecked(value)
            
            try:
                if loadData["reopen"]:
                    self._loadFile(loadData["file"])
            except (FileNotFoundError, KeyError):
                pass
        
        except FileNotFoundError:
            pass
    
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
            "ai abort mission":self.showAIA.isChecked(),
            "relinquished":self.showRC.isChecked(),
            
            "engine startup":self.showES.isChecked(),
            "engine shutdown":self.showEO.isChecked(),
            
            "crash":self.showCRH.isChecked(),
            "pilot dead":self.showPD.isChecked(),
            "pilot discard chair":self.showPDC.isChecked(),
            "eject":self.showEJT.isChecked(),
            
            "score":self.showSCR.isChecked()
        }
        
        for event in eventsList:
            currentEvent = eventsList[event]
            
            if self.allMyEvents.isChecked():
                if currentEvent.get("initiatorPilotName", False) != self.playerCallsign:
                    continue
                    # this event wasn't from our player
            else:
                if self.onlyMyEvents.isChecked() and currentEvent.get("initiatorPilotName",False) != self.playerCallsign:
                    continue
                    # continue if this event isn't ours or we filter it out
                
                if not showEventsDictionary.get(currentEvent["type"], 1):
                    continue
            
            rowIndex = self.mainTable.rowCount()
            self.mainTable.setRowCount(rowIndex+1)

            rowData = [int(event), currentEvent["t"], currentEvent["type"]]
            
            try:
                rowData.append(f"{currentEvent["initiator_unit_type"]} - ({currentEvent["initiatorPilotName"]})")
            except KeyError:
                rowData.append("")
            
            try:
                rowData.append(f"{currentEvent["target_unit_type"]} - ({currentEvent["targetPilotName"]})")
            except KeyError:
                rowData.append("")
            
            try:
                rowData.append(currentEvent["weapon"])
            except KeyError:
                rowData.append("")
                
            for i in range(len(rowData)):
                self.mainTable.setItem(rowIndex, i, QTableWidgetItem())
                self.mainTable.item(rowIndex, i).setData(Qt.DisplayRole, rowData[i])
    
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
    window.show()
    sys.exit(app.exec())