
from javax.swing import JLabel
from javax.swing import JComboBox
from javax.swing import JLabel
from javax.swing import JButton
from javax.swing import JPanel
from javax.swing import JFrame
from java.awt import Font
from javax.swing import JFileChooser
from java.io import File
import csv, base64, sys
from table import LogEntry, UpdateTableEDT
from javax.swing import SwingUtilities
from burp import IHttpRequestResponse

# This code is necessary to maximize the csv field limit for the save and
# restore functionality
maxInt = sys.maxsize
decrement = True
while decrement:
    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

# Save state
def saveState(self):

    parentFrame = JFrame()
    fileChooser = JFileChooser()
    fileChooser.setDialogTitle("State output file")
    userSelection = fileChooser.showSaveDialog(parentFrame)
    
    if userSelection == JFileChooser.APPROVE_OPTION:
        exportFile = fileChooser.getSelectedFile()
        with open(exportFile.getAbsolutePath(), 'wb') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for i in range(0,self._log.size()):
                tempRequestResponseHost = self._log.get(i)._requestResponse.getHttpService().getHost()
                tempRequestResponsePort = self._log.get(i)._requestResponse.getHttpService().getPort()
                tempRequestResponseProtocol = self._log.get(i)._requestResponse.getHttpService().getProtocol()
                tempRequestResponseRequest = base64.b64encode(self._log.get(i)._requestResponse.getRequest())
                tempRequestResponseResponse = base64.b64encode(self._log.get(i)._requestResponse.getResponse())

                tempOriginalRequestResponseHost = self._log.get(i)._originalrequestResponse.getHttpService().getHost()
                tempOriginalRequestResponsePort = self._log.get(i)._originalrequestResponse.getHttpService().getPort()
                tempOriginalRequestResponseProtocol = self._log.get(i)._originalrequestResponse.getHttpService().getProtocol()
                tempOriginalRequestResponseRequest = base64.b64encode(self._log.get(i)._originalrequestResponse.getRequest())
                tempOriginalRequestResponseResponse   = base64.b64encode(self._log.get(i)._originalrequestResponse.getResponse())

                if self._log.get(i)._unauthorizedRequestResponse is not None:
                    tempUnauthorizedRequestResponseHost = self._log.get(i)._unauthorizedRequestResponse.getHttpService().getHost()
                    tempUnauthorizedRequestResponsePort = self._log.get(i)._unauthorizedRequestResponse.getHttpService().getPort()
                    tempUnauthorizedRequestResponseProtocol = self._log.get(i)._unauthorizedRequestResponse.getHttpService().getProtocol()
                    tempUnauthorizedRequestResponseRequest = base64.b64encode(self._log.get(i)._unauthorizedRequestResponse.getRequest())
                    tempUnauthorizedRequestResponseResponse = base64.b64encode(self._log.get(i)._unauthorizedRequestResponse.getResponse())
                else:
                    tempUnauthorizedRequestResponseHost = None
                    tempUnauthorizedRequestResponsePort = None
                    tempUnauthorizedRequestResponseProtocol = None
                    tempUnauthorizedRequestResponseRequest = None
                    tempUnauthorizedRequestResponseResponse = None

                tempEnforcementStatus = self._log.get(i)._enfocementStatus
                tempEnforcementStatusUnauthorized  = self._log.get(i)._enfocementStatusUnauthorized           

                tempRow = [tempRequestResponseHost,tempRequestResponsePort,tempRequestResponseProtocol,tempRequestResponseRequest,tempRequestResponseResponse]
                tempRow.extend([tempOriginalRequestResponseHost,tempOriginalRequestResponsePort,tempOriginalRequestResponseProtocol,tempOriginalRequestResponseRequest,tempOriginalRequestResponseResponse])
                tempRow.extend([tempUnauthorizedRequestResponseHost,tempUnauthorizedRequestResponsePort,tempUnauthorizedRequestResponseProtocol,tempUnauthorizedRequestResponseRequest,tempUnauthorizedRequestResponseResponse])
                tempRow.extend([tempEnforcementStatus,tempEnforcementStatusUnauthorized])

                csvwriter.writerow(tempRow)

# Restore state
def restoreState(self):
    parentFrame = JFrame()
    fileChooser = JFileChooser()
    fileChooser.setDialogTitle("State import file")
    userSelection = fileChooser.showDialog(parentFrame,"Restore")
    
    if userSelection == JFileChooser.APPROVE_OPTION:
        importFile = fileChooser.getSelectedFile()

        with open(importFile.getAbsolutePath(), 'r') as csvfile:

            csvreader = csv.reader(csvfile, delimiter='\t', quotechar='|')

            for row in csvreader:

                tempRequestResponseHost = row[0]
                tempRequestResponsePort = row[1]
                tempRequestResponseProtocol = row[2]
                tempRequestResponseRequest = base64.b64decode(row[3])
                tempRequestResponseResponse = base64.b64decode(row[4])

                tempRequestResponseHttpService = self._helpers.buildHttpService(tempRequestResponseHost,int(tempRequestResponsePort),tempRequestResponseProtocol)
                tempRequestResponse = IHttpRequestResponseImplementation(tempRequestResponseHttpService,tempRequestResponseRequest,tempRequestResponseResponse)

                tempOriginalRequestResponseHost = row[5]
                tempOriginalRequestResponsePort = row[6]
                tempOriginalRequestResponseProtocol = row[7]
                tempOriginalRequestResponseRequest = base64.b64decode(row[8])
                tempOriginalRequestResponseResponse   = base64.b64decode(row[9])

                tempOriginalRequestResponseHttpService = self._helpers.buildHttpService(tempOriginalRequestResponseHost,int(tempOriginalRequestResponsePort),tempOriginalRequestResponseProtocol)
                tempOriginalRequestResponse = IHttpRequestResponseImplementation(tempOriginalRequestResponseHttpService,tempOriginalRequestResponseRequest,tempOriginalRequestResponseResponse)
                
                checkAuthentication = True
                if row[10] != '':
                    tempUnauthorizedRequestResponseHost = row[10]
                    tempUnauthorizedRequestResponsePort = row[11]
                    tempUnauthorizedRequestResponseProtocol = row[12]
                    tempUnauthorizedRequestResponseRequest = base64.b64decode(row[13])
                    tempUnauthorizedRequestResponseResponse = base64.b64decode(row[14])
                    tempUnauthorizedRequestResponseHttpService = self._helpers.buildHttpService(tempUnauthorizedRequestResponseHost,int(tempUnauthorizedRequestResponsePort),tempUnauthorizedRequestResponseProtocol)
                    tempUnauthorizedRequestResponse = IHttpRequestResponseImplementation(tempUnauthorizedRequestResponseHttpService,tempUnauthorizedRequestResponseRequest,tempUnauthorizedRequestResponseResponse)
                else:
                    checkAuthentication = False
                    tempUnauthorizedRequestResponse = None                      

                tempEnforcementStatus = row[15]
                tempEnforcementStatusUnauthorized  = row[16]

                self._lock.acquire()
    
                row = self._log.size()

                if checkAuthentication:
                    self._log.add(LogEntry(self.currentRequestNumber,self._callbacks.saveBuffersToTempFiles(tempRequestResponse), self._helpers.analyzeRequest(tempRequestResponse).getMethod(), self._helpers.analyzeRequest(tempRequestResponse).getUrl(), self._callbacks.saveBuffersToTempFiles(tempOriginalRequestResponse),tempEnforcementStatus,self._callbacks.saveBuffersToTempFiles(tempUnauthorizedRequestResponse),tempEnforcementStatusUnauthorized))
                else:
                    self._log.add(LogEntry(self.currentRequestNumber,self._callbacks.saveBuffersToTempFiles(tempRequestResponse), self._helpers.analyzeRequest(tempRequestResponse).getMethod(), self._helpers.analyzeRequest(tempRequestResponse).getUrl(), self._callbacks.saveBuffersToTempFiles(tempOriginalRequestResponse),tempEnforcementStatus,None,tempEnforcementStatusUnauthorized))

                SwingUtilities.invokeLater(UpdateTableEDT(self,"insert",row,row))
                self.currentRequestNumber = self.currentRequestNumber + 1
                self._lock.release()

            lastRow = self._log.size()
            if lastRow > 0:
                cookies = self.getCookieFromMessage(self._log.get(lastRow - 1)._requestResponse)
                if cookies:
                    self.lastCookies = cookies
                    self.fetchButton.setEnabled(True)

class IHttpRequestResponseImplementation(IHttpRequestResponse):

    def __init__(self, service, req, res):
        
        self._httpService = service
        self._request = req
        self._response = res
        self._comment = None
        self._highlight = None

    def getComment(self):
        return self._comment

    def getHighlight(self):
        return self._highlight

    def getHttpService(self):
        return self._httpService

    def getRequest(self):
        return self._request

    def getResponse(self):
        return self._response

    def setComment(self,c):
        self._comment = c

    def setHighlight(self,h):
        self._highlight = h

    def setHttpService(self,service):
        self._httpService = service

    def setRequest(self,req):
        self._request = req

    def setResponse(self,res):
        self._response = res
