import sys
sys.path.append("..")

from helpers.http import getCookieFromMessage, isStatusCodesReturned, makeMessage, makeRequest, getResponseContentLength, IHttpRequestResponseImplementation
from gui.table import LogEntry, UpdateTableEDT
from javax.swing import SwingUtilities
from java.net import URL
import re

def handle_message(self, toolFlag, messageIsRequest, messageInfo):
    for i in range(0, self.IFList.getModel().getSize()):
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore spider requests":
            if (toolFlag == self._callbacks.TOOL_SPIDER):
                return
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore proxy requests":
            if (toolFlag == self._callbacks.TOOL_PROXY):
                return
        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore target requests":
            if (toolFlag == self._callbacks.TOOL_TARGET):
                return
    
    cookies = getCookieFromMessage(self, messageInfo)
    if cookies:
        self.lastCookies = cookies
        self.fetchButton.setEnabled(True)

    if self.intercept == 1 and (toolFlag == self._callbacks.TOOL_PROXY or (toolFlag == self._callbacks.TOOL_REPEATER and self.interceptRequestsfromRepeater.isSelected())):
        if self.prevent304.isSelected():
            if messageIsRequest:
                requestHeaders = list(self._helpers.analyzeRequest(messageInfo).getHeaders())
                newHeaders = list()
                found = 0
                for header in requestHeaders:
                    if not "If-None-Match:" in header and not "If-Modified-Since:" in header:
                        newHeaders.append(header)
                        found = 1
                if found == 1:
                    requestInfo = self._helpers.analyzeRequest(messageInfo)
                    bodyBytes = messageInfo.getRequest()[requestInfo.getBodyOffset():]
                    bodyStr = self._helpers.bytesToString(bodyBytes)
                    messageInfo.setRequest(self._helpers.buildHttpMessage(newHeaders, bodyStr))
        if not messageIsRequest:
            # Requests with the same headers of the Autorize headers are
            # not intercepted
            if not self.replaceString.getText() in self._helpers.analyzeRequest(messageInfo).getHeaders():
                if self.ignore304.isSelected():
                    if isStatusCodesReturned(self, messageInfo, ["304", "204"]):
                        return

                if self.IFList.getModel().getSize() == 0:
                    checkAuthorization(self, messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),
                                            self.doUnauthorizedRequest.isSelected())
                else:
                    urlString = str(self._helpers.analyzeRequest(messageInfo).getUrl())
                    do_the_check = 1
                    for i in range(0, self.IFList.getModel().getSize()):
                        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Scope items only":
                            currentURL = URL(urlString)
                            if not self._callbacks.isInScope(currentURL):
                                do_the_check = 0

                        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Contains (simple string)":
                            if self.IFList.getModel().getElementAt(i)[30:] not in urlString:
                                do_the_check = 0

                        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Contains (regex)":
                            regex_string = self.IFList.getModel().getElementAt(i)[22:]
                            if re.search(regex_string, urlString, re.IGNORECASE) is None:
                                do_the_check = 0

                        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Not Contains (simple string)":
                            if self.IFList.getModel().getElementAt(i)[34:] in urlString:
                                do_the_check = 0

                        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Not Contains (regex)":
                            regex_string = self.IFList.getModel().getElementAt(i)[26:]
                            if not re.search(regex_string, urlString, re.IGNORECASE) is None:
                                do_the_check = 0

                        if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Not Contains (regex)":
                            regex_string = self.IFList.getModel().getElementAt(i)[26:]
                            if not re.search(regex_string, urlString, re.IGNORECASE) is None:
                                do_the_check = 0

                        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Only HTTP methods (newline separated)":
                            filterMethods = self.IFList.getModel().getElementAt(i)[39:].split("\n")
                            filterMethods = [x.lower() for x in filterMethods]
                            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
                            if reqMethod.lower() not in filterMethods:
                                do_the_check = 0

                        if self.IFList.getModel().getElementAt(i).split(":")[0] == "Ignore HTTP methods (newline separated)":
                            filterMethods = self.IFList.getModel().getElementAt(i)[41:].split("\n")
                            filterMethods = [x.lower() for x in filterMethods]
                            reqMethod = str(self._helpers.analyzeRequest(messageInfo).getMethod())
                            if reqMethod.lower() in filterMethods:
                                do_the_check = 0
                        
                        
                    if do_the_check:
                        checkAuthorization(self, messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())

def sendRequestToAutorizeWork(self,messageInfo):
    if messageInfo.getResponse() is None:
        message = makeMessage(self, messageInfo,False,False)
        requestResponse = makeRequest(self, messageInfo, message)
        checkAuthorization(self, requestResponse,self._helpers.analyzeResponse(requestResponse.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())
    else:
        request = messageInfo.getRequest()
        response = messageInfo.getResponse()
        httpService = messageInfo.getHttpService()
        newHttpRequestResponse = IHttpRequestResponseImplementation(httpService,request,response)
        newHttpRequestResponsePersisted = self._callbacks.saveBuffersToTempFiles(newHttpRequestResponse)
        checkAuthorization(self, newHttpRequestResponsePersisted,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())

def checkBypass(self,oldStatusCode,newStatusCode,oldContentLen,newContentLen,filters,requestResponse,andOrEnforcement):
    response = requestResponse.getResponse()
    analyzedResponse = self._helpers.analyzeResponse(response)
    impression = ""

    if oldStatusCode == newStatusCode:
        if oldContentLen == newContentLen:
            impression = self.BYPASSSED_STR
        
        if len(filters) > 0:

            if andOrEnforcement == "And":
                andEnforcementCheck = True
                auth_enforced = 1
            else:
                andEnforcementCheck = False
                auth_enforced = 0

            for filter in filters:
                if str(filter).startswith("Status code equals: "):
                    statusCode = filter[20:]
                    if andEnforcementCheck:
                        if auth_enforced == 1 and not isStatusCodesReturned(self, requestResponse, statusCode):
                            auth_enforced = 0
                    else:
                        if auth_enforced == 0 and isStatusCodesReturned(self, requestResponse, statusCode):
                            auth_enforced = 1

                if str(filter).startswith("Headers (simple string): "):
                    if andEnforcementCheck:
                        if auth_enforced == 1 and not filter[25:] in self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()]):
                            auth_enforced = 0
                    else:
                        if auth_enforced == 0 and filter[25:] in self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()]):
                            auth_enforced = 1

                if str(filter).startswith("Headers (regex): "):
                    regex_string = filter[17:]
                    p = re.compile(regex_string, re.IGNORECASE)                        
                    if andEnforcementCheck:
                        if auth_enforced == 1 and not p.search(self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])):
                            auth_enforced = 0
                    else:
                        if auth_enforced == 0 and p.search(self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])):
                            auth_enforced = 1

                if str(filter).startswith("Body (simple string): "):
                    if andEnforcementCheck:
                        if auth_enforced == 1 and not filter[22:] in self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():]):
                            auth_enforced = 0
                    else:
                        if auth_enforced == 0 and filter[22:] in self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():]):
                            auth_enforced = 1

                if str(filter).startswith("Body (regex): "):
                    regex_string = filter[14:]
                    p = re.compile(regex_string, re.IGNORECASE)
                    if andEnforcementCheck:
                        if auth_enforced == 1 and not p.search(self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])):
                            auth_enforced = 0
                    else:
                        if auth_enforced == 0 and p.search(self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])):
                            auth_enforced = 1

                if str(filter).startswith("Full response (simple string): "):
                    if andEnforcementCheck:
                        if auth_enforced == 1 and not filter[31:] in self._helpers.bytesToString(requestResponse.getResponse()):
                            auth_enforced = 0
                    else:
                        if auth_enforced == 0 and filter[31:] in self._helpers.bytesToString(requestResponse.getResponse()):
                            auth_enforced = 1

                if str(filter).startswith("Full response (regex): "):
                    regex_string = filter[23:]
                    p = re.compile(regex_string, re.IGNORECASE)
                    if andEnforcementCheck:
                        if auth_enforced == 1 and not p.search(self._helpers.bytesToString(requestResponse.getResponse())):
                            auth_enforced = 0
                    else:
                        if auth_enforced == 0 and p.search(self._helpers.bytesToString(requestResponse.getResponse())):
                            auth_enforced = 1

                if str(filter).startswith("Full response length: "):
                    if andEnforcementCheck:
                        if auth_enforced == 1 and not str(len(response)) == filter[22:].strip():
                            auth_enforced = 0
                    else:
                        if auth_enforced == 0 and str(len(response)) == filter[22:].strip():
                            auth_enforced = 1

        else:
            # If no enforcement detectors are set and the HTTP response is the same, the impression is yellow
            auth_enforced = 0

        if auth_enforced:
            impression = self.ENFORCED_STR
        else:
            impression = self.IS_ENFORCED_STR
                        
    else:
        impression = self.ENFORCED_STR

    return impression

def checkAuthorization(self, messageInfo, originalHeaders, checkUnauthorized):
    oldResponse = messageInfo.getResponse()
    message = makeMessage(self, messageInfo, True, True)
    requestResponse = makeRequest(self, messageInfo, message)
    newResponse = requestResponse.getResponse()
    analyzedResponse = self._helpers.analyzeResponse(newResponse)
    
    oldStatusCode = originalHeaders[0]
    newStatusCode = analyzedResponse.getHeaders()[0]
    oldContentLen = getResponseContentLength(self, oldResponse)
    newContentLen = getResponseContentLength(self, newResponse)

    # Check unauthorized request
    if checkUnauthorized:
        messageUnauthorized = makeMessage(self, messageInfo, True, False)
        requestResponseUnauthorized = makeRequest(self, messageInfo, messageUnauthorized)
        unauthorizedResponse = requestResponseUnauthorized.getResponse()
        analyzedResponseUnauthorized = self._helpers.analyzeResponse(unauthorizedResponse)  
        statusCodeUnauthorized = analyzedResponseUnauthorized.getHeaders()[0]
        contentLenUnauthorized = getResponseContentLength(self, unauthorizedResponse)

    EDFilters = self.EDModel.toArray()

    impression = checkBypass(self, oldStatusCode,newStatusCode,oldContentLen,newContentLen,EDFilters,requestResponse,self.AndOrType.getSelectedItem())

    if checkUnauthorized:
        EDFiltersUnauth = self.EDModelUnauth.toArray()
        impressionUnauthorized = checkBypass(self, oldStatusCode,statusCodeUnauthorized,oldContentLen,contentLenUnauthorized,EDFiltersUnauth,requestResponseUnauthorized,self.AndOrTypeUnauth.getSelectedItem())

    self._lock.acquire()
    
    row = self._log.size()
    method = self._helpers.analyzeRequest(messageInfo.getRequest()).getMethod()
    
    if checkUnauthorized:
        self._log.add(LogEntry(self.currentRequestNumber,self._callbacks.saveBuffersToTempFiles(requestResponse), method, self._helpers.analyzeRequest(requestResponse).getUrl(),messageInfo,impression,self._callbacks.saveBuffersToTempFiles(requestResponseUnauthorized),impressionUnauthorized)) # same requests not include again.
    else:
        self._log.add(LogEntry(self.currentRequestNumber,self._callbacks.saveBuffersToTempFiles(requestResponse), method, self._helpers.analyzeRequest(requestResponse).getUrl(),messageInfo,impression,None,"Disabled")) # same requests not include again.
    
    SwingUtilities.invokeLater(UpdateTableEDT(self,"insert",row,row))
    self.currentRequestNumber = self.currentRequestNumber + 1
    self._lock.release()
    
