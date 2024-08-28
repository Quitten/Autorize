#!/usr/bin/env python
# -*- coding: utf-8 -*-

from javax.swing import SwingUtilities
from javax.swing import JFileChooser
from javax.swing import JFrame

from table import LogEntry, UpdateTableEDT
from helpers.http import get_cookie_header_from_message, get_authorization_header_from_message, IHttpRequestResponseImplementation

import csv, base64, json, re, sys

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

class SaveRestore():
    def __init__(self, extender):
        self._extender = extender
        self._checkBoxes = [
            "autoScroll",
            "ignore304",
            "prevent304",
            "interceptRequestsfromRepeater",
            "doUnauthorizedRequest",
            "replaceQueryParam",
            "showAuthBypassModified",
            "showAuthPotentiallyEnforcedModified",
            "showAuthEnforcedModified",
            "showAuthBypassUnauthenticated",
            "showAuthPotentiallyEnforcedUnauthenticated",
            "showAuthEnforcedUnauthenticated",
            "showDisabledUnauthenticated"
        ]

    def saveState(self):
        parentFrame = JFrame()
        fileChooser = JFileChooser()
        fileChooser.setDialogTitle("State output file")
        userSelection = fileChooser.showSaveDialog(parentFrame)

        if userSelection == JFileChooser.APPROVE_OPTION:
            exportFile = fileChooser.getSelectedFile()
            with open(exportFile.getAbsolutePath(), 'wb') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)

                # Configuration
                tempRow = ["ReplaceString", base64.b64encode(self._extender.replaceString.getText())]
                csvwriter.writerow(tempRow)

                for EDFilter in self._extender.EDModel.toArray():
                    tempRow = ["EDFilter", base64.b64encode(EDFilter)]
                    csvwriter.writerow(tempRow)

                for EDFilterUnauth in self._extender.EDModelUnauth.toArray():
                    tempRow = ["EDFilterUnauth", base64.b64encode(EDFilterUnauth)]
                    csvwriter.writerow(tempRow)

                for IFFilter in self._extender.IFModel.toArray():
                    tempRow = ["IFFilter", base64.b64encode(IFFilter)]
                    csvwriter.writerow(tempRow)

                for t in ["AndOrType", "AndOrTypeUnauth"]:
                    tempRow = [t, getattr(self._extender, t).getSelectedItem()]
                    csvwriter.writerow(tempRow)

                for key in self._extender.badProgrammerMRModel:
                    d = dict(self._extender.badProgrammerMRModel[key])
                    d["regexMatch"] = d["regexMatch"] is not None
                    tempRow = ["MatchReplace", base64.b64encode(json.dumps(d))]
                    csvwriter.writerow(tempRow)

                d = dict((c, getattr(self._extender, c).isSelected()) for c in self._checkBoxes)
                tempRow = ["CheckBoxes", json.dumps(d)]
                csvwriter.writerow(tempRow)

                isSelected = self._extender.exportPnl.getComponents()[-1].isSelected()
                tempRow = ["RemoveDuplicates", json.dumps(isSelected)]
                csvwriter.writerow(tempRow)

                # Request/response list
                for i in range(0,self._extender._log.size()):
                    tempRequestResponseHost = self._extender._log.get(i)._requestResponse.getHttpService().getHost()
                    tempRequestResponsePort = self._extender._log.get(i)._requestResponse.getHttpService().getPort()
                    tempRequestResponseProtocol = self._extender._log.get(i)._requestResponse.getHttpService().getProtocol()
                    tempRequestResponseRequest = base64.b64encode(self._extender._log.get(i)._requestResponse.getRequest())
                    tempRequestResponseResponse = base64.b64encode(self._extender._log.get(i)._requestResponse.getResponse())

                    tempOriginalRequestResponseHost = self._extender._log.get(i)._originalrequestResponse.getHttpService().getHost()
                    tempOriginalRequestResponsePort = self._extender._log.get(i)._originalrequestResponse.getHttpService().getPort()
                    tempOriginalRequestResponseProtocol = self._extender._log.get(i)._originalrequestResponse.getHttpService().getProtocol()
                    tempOriginalRequestResponseRequest = base64.b64encode(self._extender._log.get(i)._originalrequestResponse.getRequest())
                    tempOriginalRequestResponseResponse = base64.b64encode(self._extender._log.get(i)._originalrequestResponse.getResponse())

                    if self._extender._log.get(i)._unauthorizedRequestResponse is not None:
                        tempUnauthorizedRequestResponseHost = self._extender._log.get(i)._unauthorizedRequestResponse.getHttpService().getHost()
                        tempUnauthorizedRequestResponsePort = self._extender._log.get(i)._unauthorizedRequestResponse.getHttpService().getPort()
                        tempUnauthorizedRequestResponseProtocol = self._extender._log.get(i)._unauthorizedRequestResponse.getHttpService().getProtocol()
                        tempUnauthorizedRequestResponseRequest = base64.b64encode(self._extender._log.get(i)._unauthorizedRequestResponse.getRequest())
                        tempUnauthorizedRequestResponseResponse = base64.b64encode(self._extender._log.get(i)._unauthorizedRequestResponse.getResponse())
                    else:
                        tempUnauthorizedRequestResponseHost = None
                        tempUnauthorizedRequestResponsePort = None
                        tempUnauthorizedRequestResponseProtocol = None
                        tempUnauthorizedRequestResponseRequest = None
                        tempUnauthorizedRequestResponseResponse = None

                    tempEnforcementStatus = self._extender._log.get(i)._enfocementStatus
                    tempEnforcementStatusUnauthorized = self._extender._log.get(i)._enfocementStatusUnauthorized

                    tempRow = [tempRequestResponseHost,tempRequestResponsePort,tempRequestResponseProtocol,tempRequestResponseRequest,tempRequestResponseResponse]
                    tempRow.extend([tempOriginalRequestResponseHost,tempOriginalRequestResponsePort,tempOriginalRequestResponseProtocol,tempOriginalRequestResponseRequest,tempOriginalRequestResponseResponse])
                    tempRow.extend([tempUnauthorizedRequestResponseHost,tempUnauthorizedRequestResponsePort,tempUnauthorizedRequestResponseProtocol,tempUnauthorizedRequestResponseRequest,tempUnauthorizedRequestResponseResponse])
                    tempRow.extend([tempEnforcementStatus,tempEnforcementStatusUnauthorized])

                    csvwriter.writerow(tempRow)

    def restoreState(self):
        parentFrame = JFrame()
        fileChooser = JFileChooser()
        fileChooser.setDialogTitle("State import file")
        userSelection = fileChooser.showDialog(parentFrame, "Restore")
        modelMap = {
            "IFFilter": self._extender.IFModel,
            "EDFilter": self._extender.EDModel,
            "EDFilterUnauth": self._extender.EDModelUnauth
        }

        if userSelection == JFileChooser.APPROVE_OPTION:
            importFile = fileChooser.getSelectedFile()

            with open(importFile.getAbsolutePath(), 'r') as csvfile:

                csvreader = csv.reader(csvfile, delimiter='\t', quotechar='|')

                for row in csvreader:
                    # Configuration
                    if row[0] == "ReplaceString":
                        self._extender.replaceString.setText(base64.b64decode(row[1]))
                        continue

                    if row[0] in modelMap:
                        f = base64.b64decode(row[1])
                        if f not in modelMap[row[0]].toArray():
                            modelMap[row[0]].addElement(f)
                        continue

                    if row[0] in {"AndOrType", "AndOrTypeUnauth"}:
                        getattr(self._extender, row[0]).setSelectedItem(row[1])
                        continue

                    if row[0] == "MatchReplace":
                        d = json.loads(base64.b64decode(row[1]))
                        key = d["type"] + " " + d["match"] + "->" + d["replace"]
                        if key in self._extender.badProgrammerMRModel:
                            continue
                        regexMatch = None
                        if d["regexMatch"]:
                            try:
                                d["regexMatch"] = re.compile(d["match"])
                            except re.error:
                                print("ERROR: Regex to restore is invalid:", d["match"])
                                continue
                        self._extender.badProgrammerMRModel[key] = d
                        self._extender.MRModel.addElement(key)
                        continue

                    if row[0] == "CheckBoxes":
                        d = json.loads(row[1])
                        for k in d:
                            getattr(self._extender, k).setSelected(d[k])
                        continue

                    if row[0] == "RemoveDuplicates":
                        isSelected = json.loads(row[1])
                        try:
                            self._extender.exportPnl.getComponents()[-1].setSelected(isSelected)
                        except TypeError:  # suppress TypeError: None required for void return
                            pass
                        continue

                    # Request/response list
                    tempRequestResponseHost = row[0]
                    tempRequestResponsePort = row[1]
                    tempRequestResponseProtocol = row[2]
                    tempRequestResponseRequest = base64.b64decode(row[3])
                    tempRequestResponseResponse = base64.b64decode(row[4])

                    tempRequestResponseHttpService = self._extender._helpers.buildHttpService(tempRequestResponseHost,int(tempRequestResponsePort),tempRequestResponseProtocol)
                    tempRequestResponse = IHttpRequestResponseImplementation(tempRequestResponseHttpService,tempRequestResponseRequest,tempRequestResponseResponse)

                    tempOriginalRequestResponseHost = row[5]
                    tempOriginalRequestResponsePort = row[6]
                    tempOriginalRequestResponseProtocol = row[7]
                    tempOriginalRequestResponseRequest = base64.b64decode(row[8])
                    tempOriginalRequestResponseResponse = base64.b64decode(row[9])

                    tempOriginalRequestResponseHttpService = self._extender._helpers.buildHttpService(tempOriginalRequestResponseHost,int(tempOriginalRequestResponsePort),tempOriginalRequestResponseProtocol)
                    tempOriginalRequestResponse = IHttpRequestResponseImplementation(tempOriginalRequestResponseHttpService,tempOriginalRequestResponseRequest,tempOriginalRequestResponseResponse)

                    checkAuthentication = True
                    if row[10] != '':
                        tempUnauthorizedRequestResponseHost = row[10]
                        tempUnauthorizedRequestResponsePort = row[11]
                        tempUnauthorizedRequestResponseProtocol = row[12]
                        tempUnauthorizedRequestResponseRequest = base64.b64decode(row[13])
                        tempUnauthorizedRequestResponseResponse = base64.b64decode(row[14])
                        tempUnauthorizedRequestResponseHttpService = self._extender._helpers.buildHttpService(tempUnauthorizedRequestResponseHost,int(tempUnauthorizedRequestResponsePort),tempUnauthorizedRequestResponseProtocol)
                        tempUnauthorizedRequestResponse = IHttpRequestResponseImplementation(tempUnauthorizedRequestResponseHttpService,tempUnauthorizedRequestResponseRequest,tempUnauthorizedRequestResponseResponse)
                    else:
                        checkAuthentication = False
                        tempUnauthorizedRequestResponse = None

                    tempEnforcementStatus = row[15]
                    tempEnforcementStatusUnauthorized = row[16]

                    self._extender._lock.acquire()

                    row = self._extender._log.size()

                    if checkAuthentication:
                        self._extender._log.add(
                            LogEntry(self._extender.currentRequestNumber,
                            self._extender._callbacks.saveBuffersToTempFiles(tempRequestResponse),
                             self._extender._helpers.analyzeRequest(tempRequestResponse).getMethod(),
                              self._extender._helpers.analyzeRequest(tempRequestResponse).getUrl(),
                               self._extender._callbacks.saveBuffersToTempFiles(tempOriginalRequestResponse),
                               tempEnforcementStatus,
                               self._extender._callbacks.saveBuffersToTempFiles(tempUnauthorizedRequestResponse),
                               tempEnforcementStatusUnauthorized))
                    else:
                        self._extender._log.add(
                            LogEntry(self._extender.currentRequestNumber,
                            self._extender._callbacks.saveBuffersToTempFiles(tempRequestResponse),
                            self._extender._helpers.analyzeRequest(tempRequestResponse).getMethod(),
                             self._extender._helpers.analyzeRequest(tempRequestResponse).getUrl(),
                              self._extender._callbacks.saveBuffersToTempFiles(tempOriginalRequestResponse),
                              tempEnforcementStatus,None,tempEnforcementStatusUnauthorized))

                    SwingUtilities.invokeLater(UpdateTableEDT(self._extender,"insert",row,row))
                    self._extender.currentRequestNumber = self._extender.currentRequestNumber + 1
                    self._extender._lock.release()

                lastRow = self._extender._log.size()
                if lastRow > 0:
                    cookiesHeader = get_cookie_header_from_message(self._extender, self._extender._log.get(lastRow - 1)._requestResponse)
                    if cookiesHeader:
                        self._extender.lastCookiesHeader = cookiesHeader
                        self._extender.fetchCookiesHeaderButton.setEnabled(True)
                    authorizationHeader = get_authorization_header_from_message(self._extender, self._extender._log.get(lastRow - 1)._requestResponse)
                    if authorizationHeader:
                        self._extender.lastAuthorizationHeader = authorizationHeader
                        self._extender.fetchAuthorizationHeaderButton.setEnabled(True)
