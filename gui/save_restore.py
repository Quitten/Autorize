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
            "showBypassed",
            "showIsEnforced", 
            "showEnforced"
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
                user_configs = []

                for user_id, user_data in self._extender.userTab.user_tabs.items():
                    user_config = {
                        'user_id': user_id,
                        'user_name': user_data['user_name'],
                        'headers_text': user_data['headers_instance'].replaceString.getText(),
                        'ed_filters': list(user_data['ed_instance'].EDModel.toArray()),
                        'ed_type': user_data['ed_instance'].EDType.getSelectedIndex(),
                        'ed_text': user_data['ed_instance'].EDText.getText(),
                        'andor_type': user_data['ed_instance'].AndOrType.getSelectedIndex(),
                        'mr_rules': dict(user_data['mr_instance'].badProgrammerMRModel)
                    }

                    user_configs.append(user_config)

                    tempRow = ["UserConfigs", base64.b64encode(json.dumps(user_configs))]
                    csvwriter.writerow(tempRow)

                if hasattr(self._extender, 'EDModelUnauth'):
                    for EDFilterUnauth in self._extender.EDModelUnauth.toArray():
                        tempRow = ["EDFilterUnauth", base64.b64encode(EDFilterUnauth)]
                        csvwriter.writerow(tempRow)

                if hasattr(self._extender, 'IFModel'):
                    for IFFilter in self._extender.IFModel.toArray():
                        tempRow = ["IFFilter", base64.b64encode(IFFilter)]
                        csvwriter.writerow(tempRow)

                d = dict((c, getattr(self._extender, c).isSelected()) for c in self._checkBoxes)

                tempRow = ["CheckBoxes", json.dumps(d)]
                csvwriter.writerow(tempRow)

                # Request/response list
                for i in range(0, self._extender._log.size()):
                    logEntry = self._extender._log.get(i)
                    
                    tempOriginalRequestResponseHost = logEntry._originalrequestResponse.getHttpService().getHost()
                    tempOriginalRequestResponsePort = logEntry._originalrequestResponse.getHttpService().getPort()
                    tempOriginalRequestResponseProtocol = logEntry._originalrequestResponse.getHttpService().getProtocol()
                    tempOriginalRequestResponseRequest = base64.b64encode(logEntry._originalrequestResponse.getRequest())
                    tempOriginalRequestResponseResponse = base64.b64encode(logEntry._originalrequestResponse.getResponse())

                    if logEntry._unauthorizedRequestResponse is not None:
                        tempUnauthorizedRequestResponseHost = logEntry._unauthorizedRequestResponse.getHttpService().getHost()
                        tempUnauthorizedRequestResponsePort = logEntry._unauthorizedRequestResponse.getHttpService().getPort()
                        tempUnauthorizedRequestResponseProtocol = logEntry._unauthorizedRequestResponse.getHttpService().getProtocol()
                        tempUnauthorizedRequestResponseRequest = base64.b64encode(logEntry._unauthorizedRequestResponse.getRequest())
                        tempUnauthorizedRequestResponseResponse = base64.b64encode(logEntry._unauthorizedRequestResponse.getResponse())
                    else:
                        tempUnauthorizedRequestResponseHost = None
                        tempUnauthorizedRequestResponsePort = None
                        tempUnauthorizedRequestResponseProtocol = None
                        tempUnauthorizedRequestResponseRequest = None
                        tempUnauthorizedRequestResponseResponse = None

                    tempEnforcementStatusUnauthorized = logEntry._enfocementStatusUnauthorized

                    user_data_json = {}
                    
                    for user_id in logEntry.get_all_users():
                        user_enforcement = logEntry.get_user_enforcement(user_id)
                        if user_enforcement and user_enforcement['requestResponse']:
                            user_data_json[str(user_id)] = {
                                'host': user_enforcement['requestResponse'].getHttpService().getHost(),
                                'port': user_enforcement['requestResponse'].getHttpService().getPort(),
                                'protocol': user_enforcement['requestResponse'].getHttpService().getProtocol(),
                                'request': base64.b64encode(user_enforcement['requestResponse'].getRequest()),
                                'response': base64.b64encode(user_enforcement['requestResponse'].getResponse()),
                                'status': user_enforcement['enforcementStatus']
                            }

                    tempRow = [
                        tempOriginalRequestResponseHost, tempOriginalRequestResponsePort, tempOriginalRequestResponseProtocol,
                        tempOriginalRequestResponseRequest, tempOriginalRequestResponseResponse,
                        tempUnauthorizedRequestResponseHost, tempUnauthorizedRequestResponsePort, tempUnauthorizedRequestResponseProtocol,
                        tempUnauthorizedRequestResponseRequest, tempUnauthorizedRequestResponseResponse,
                        tempEnforcementStatusUnauthorized,
                        base64.b64encode(json.dumps(user_data_json))
                    ]

                    csvwriter.writerow(tempRow)

    def restoreState(self):
        parentFrame = JFrame()
        fileChooser = JFileChooser()
        fileChooser.setDialogTitle("State import file")
        userSelection = fileChooser.showDialog(parentFrame, "Restore")

        if userSelection == JFileChooser.APPROVE_OPTION:
            importFile = fileChooser.getSelectedFile()
            
            self._extender._log.clear()
            self._extender.tableModel.fireTableDataChanged()
            
            if hasattr(self._extender, 'EDModelUnauth'):
                self._extender.EDModelUnauth.clear()
            if hasattr(self._extender, 'IFModel'):
                self._extender.IFModel.clear()

            with open(importFile.getAbsolutePath(), 'r') as csvfile:

                csvreader = csv.reader(csvfile, delimiter='\t', quotechar='|')

                user_configs = None

                for row in csvreader:
                    # Configuration
                    if row[0] == "ReplaceString":
                        # Legacy: global ReplaceString no longer used (now per-user)
                        continue

                    if row[0] == "UserConfigs":
                        user_configs = json.loads(base64.b64decode(row[1]))

                        # Restore user configurations
                        if hasattr(self._extender, 'userTab') and self._extender.userTab:
                            self._extender.userTab.reset_user()

                            for i, config in enumerate(user_configs):
                                if i == 0:
                                    user_data = list(self._extender.userTab.user_tabs.values())[0]
                                else:
                                    self._extender.userTab.add_user()
                                    user_data = list(self._extender.userTab.user_tabs.values())[-1]
                                
                                if 'headers_text' in config:
                                    user_data['headers_instance'].replaceString.setText(config['headers_text'])

                                user_data['ed_instance'].EDModel.clear()
                                for filter in config['ed_filters']:
                                    user_data['ed_instance'].EDModel.addElement(filter)
                                
                                user_data['ed_instance'].EDType.setSelectedIndex(config['ed_type'])
                                user_data['ed_instance'].EDText.setText(config['ed_text'])
                                user_data['ed_instance'].AndOrType.setSelectedIndex(config['andor_type'])
                                
                                user_data['mr_instance'].badProgrammerMRModel.clear()
                                user_data['mr_instance'].MRModel.clear()
                                for key, value in config['mr_rules'].items():
                                    user_data['mr_instance'].badProgrammerMRModel[key] = value
                                    user_data['mr_instance'].MRModel.addElement(key)
                        continue

                    if row[0] == "EDFilterUnauth":
                        if hasattr(self._extender, 'EDModelUnauth'):
                            self._extender.EDModelUnauth.addElement(base64.b64decode(row[1]))
                        continue

                    if row[0] == "IFFilter":
                        if hasattr(self._extender, 'IFModel'):
                            self._extender.IFModel.addElement(base64.b64decode(row[1]))
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

                    if len(row) >= 12:
                        tempOriginalRequestResponseHost = row[0]
                        tempOriginalRequestResponsePort = row[1]
                        tempOriginalRequestResponseProtocol = row[2]
                        tempOriginalRequestResponseRequest = base64.b64decode(row[3])
                        tempOriginalRequestResponseResponse = base64.b64decode(row[4])

                        tempOriginalRequestResponseHttpService = self._extender._helpers.buildHttpService(
                            tempOriginalRequestResponseHost, int(tempOriginalRequestResponsePort), tempOriginalRequestResponseProtocol)
                        tempOriginalRequestResponse = IHttpRequestResponseImplementation(
                            tempOriginalRequestResponseHttpService, tempOriginalRequestResponseRequest, tempOriginalRequestResponseResponse)

                        checkAuthentication = True
                        if row[5] != '':
                            tempUnauthorizedRequestResponseHost = row[5]
                            tempUnauthorizedRequestResponsePort = row[6]
                            tempUnauthorizedRequestResponseProtocol = row[7]
                            tempUnauthorizedRequestResponseRequest = base64.b64decode(row[8])
                            tempUnauthorizedRequestResponseResponse = base64.b64decode(row[9])
                            tempUnauthorizedRequestResponseHttpService = self._extender._helpers.buildHttpService(
                                tempUnauthorizedRequestResponseHost, int(tempUnauthorizedRequestResponsePort), tempUnauthorizedRequestResponseProtocol)
                            tempUnauthorizedRequestResponse = IHttpRequestResponseImplementation(
                                tempUnauthorizedRequestResponseHttpService, tempUnauthorizedRequestResponseRequest, tempUnauthorizedRequestResponseResponse)
                        else:
                            checkAuthentication = False
                            tempUnauthorizedRequestResponse = None

                        tempEnforcementStatusUnauthorized = row[10]

                        method = self._extender._helpers.analyzeRequest(tempOriginalRequestResponse).getMethod()
                        original_url = self._extender._helpers.analyzeRequest(tempOriginalRequestResponse).getUrl()

                        logEntry = LogEntry(self._extender.currentRequestNumber, method, original_url,
                                        self._extender._callbacks.saveBuffersToTempFiles(tempOriginalRequestResponse),
                                        self._extender._callbacks.saveBuffersToTempFiles(tempUnauthorizedRequestResponse) if checkAuthentication else None,
                                        tempEnforcementStatusUnauthorized)

                        if len(row) > 11 and row[11]:
                            user_data_json = json.loads(base64.b64decode(row[11]))
                            for user_id_str, user_data in user_data_json.items():
                                user_id = int(user_id_str)
                                userHttpService = self._extender._helpers.buildHttpService(
                                    user_data['host'], int(user_data['port']), user_data['protocol'])
                                userRequestResponse = IHttpRequestResponseImplementation(
                                    userHttpService, base64.b64decode(user_data['request']), base64.b64decode(user_data['response']))
                                savedUserRequestResponse = self._extender._callbacks.saveBuffersToTempFiles(userRequestResponse)
                                logEntry.add_user_enforcement(user_id, savedUserRequestResponse, user_data['status'])

                        self._extender._log.add(logEntry)
                        self._extender.currentRequestNumber = self._extender.currentRequestNumber + 1

                    self._extender.tableModel.fireTableDataChanged()