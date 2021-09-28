#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import re
from burp import IHttpRequestResponse

def isStatusCodesReturned(self, messageInfo, statusCodes):
    firstHeader = self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders()[0]
    if type(statusCodes) == list:
        for statusCode in statusCodes:
            if statusCode in firstHeader:
                return True
    elif type(statusCodes) == str or type(statusCodes) == unicode:
        # single status code
        if statusCodes in firstHeader:
                return True
    return False

def makeRequest(self, messageInfo, message):
    requestURL = self._helpers.analyzeRequest(messageInfo).getUrl()
    return self._callbacks.makeHttpRequest(self._helpers.buildHttpService(str(requestURL.getHost()), int(requestURL.getPort()), requestURL.getProtocol() == "https"), message)

def makeMessage(self, messageInfo, removeOrNot, authorizeOrNot):
    requestInfo = self._helpers.analyzeRequest(messageInfo)
    headers = requestInfo.getHeaders()
    if removeOrNot:
        headers = list(headers)
        # flag for query
        queryFlag = self.replaceQueryParam.isSelected()
        if queryFlag:
            param = self.replaceString.getText().split("=")
            paramKey = param[0]
            paramValue = param[1]
            # ([\?&])test=.*?(?=[\s&])
            pattern = r"([\?&]){}=.*?(?=[\s&])".format(paramKey)
            patchedHeader = re.sub(pattern, r"\1{}={}".format(paramKey, paramValue), headers[0], count=1, flags=re.DOTALL)
            headers[0] = patchedHeader
        else:
            removeHeaders = self.replaceString.getText()

            # Headers must be entered line by line i.e. each header in a new
            # line
            removeHeaders = [header for header in removeHeaders.split() if header.endswith(':')]
            
            for header in headers[:]:
                for removeHeader in removeHeaders:
                    if header.startswith(removeHeader):
                        headers.remove(header)

        if authorizeOrNot:
            # simple string replace
            for k, v in self.badProgrammerMRModel.items():
                if(v["type"] == "Headers (simple string):") :
                    headers = map(lambda h: h.replace(v["match"], v["replace"]), headers)
                if(v["type"] == "Headers (regex):") :
                    headers = map(lambda h: re.sub(v["regexMatch"], v["replace"], h), headers)
                    
            if not queryFlag:
                # fix missing carriage return on *NIX systems
                replaceStringLines = self.replaceString.getText().split("\n")
                
                for h in replaceStringLines:
                    headers.append(h)
            
    msgBody = messageInfo.getRequest()[requestInfo.getBodyOffset():]

    # apply the match/replace settings to the body of the request
    if authorizeOrNot and msgBody is not None:
        msgBody = self._helpers.bytesToString(msgBody)
        # simple string replace
        for k, v in self.badProgrammerMRModel.items():
            if(v["type"] == "Body (simple string):") :
                msgBody = msgBody.replace(v["match"], v["replace"])
            if(v["type"] == "Body (regex):") :
                msgBody = re.sub(v["regexMatch"], v["replace"],msgBody)
        msgBody = self._helpers.stringToBytes(msgBody)
    return self._helpers.buildHttpMessage(headers, msgBody)

def getResponseHeaders(self, requestResponse):
    analyzedResponse = self._helpers.analyzeResponse(requestResponse.getResponse())
    return self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])

def getResponseBody(self, requestResponse):
    analyzedResponse = self._helpers.analyzeResponse(requestResponse.getResponse())
    self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])

def getResponseContentLength(self, response):
    return len(response) - self._helpers.analyzeResponse(response).getBodyOffset()

def get_cookie_header_from_message(self, messageInfo):
    headers = list(self._helpers.analyzeRequest(messageInfo.getRequest()).getHeaders())
    for header in headers:
        if header.strip().lower().startswith("cookie:"):
            return header
    return None

def get_authorization_header_from_message(self, messageInfo):
    headers = list(self._helpers.analyzeRequest(messageInfo.getRequest()).getHeaders())
    for header in headers:
        if header.strip().lower().startswith("authorization:"):
            return header
    return None

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
