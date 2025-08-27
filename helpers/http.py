#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from burp import IHttpRequestResponse

try:  
    unicode  
except NameError:  
    unicode = str  

def _split_request_line(req_line):
    try:
        i = req_line.find(' ')
        j = req_line.rfind(' ')
        if i == -1 or j == -1 or j <= i:
            return None, None, None
        return req_line[:i], req_line[i+1:j], req_line[j+1:]
    except Exception:
        return None, None, None

def _update_request_line_params(req_line, pairs):
    try:
        method, path_query, version = _split_request_line(req_line)
        if not path_query:
            return req_line
        qpos = path_query.find('?')
        if qpos == -1:
            path = path_query
            query = ''
            items = []
        else:
            path = path_query[:qpos]
            query = path_query[qpos+1:]
            items = [s for s in query.split('&') if s != '']
        kv = []
        for it in items:
            if '=' in it:
                k, v = it.split('=', 1)
            else:
                k, v = it, ''
            kv.append([k, v])
        used = set()
        for k_new, v_new in pairs:
            if not k_new:
                continue
            if k_new in used:
                kv.append([k_new, v_new])
                continue
            replaced = False
            for entry in kv:
                if entry[0] == k_new:
                    entry[1] = v_new
                    replaced = True
                    used.add(k_new)
                    break
            if not replaced:
                kv.append([k_new, v_new])
                used.add(k_new)

        new_query = '&'.join(['{}={}'.format(k, v) if v != '' else k for k, v in kv])
        new_path_query = path if not new_query else '{}?{}'.format(path, new_query)
        return '{} {} {}'.format(method, new_path_query, version)
    except Exception:
        return req_line

def _parse_query_pairs_from_text(text):
    pairs = []
    try:
        for raw in (text or '').split('\n'):
            line = raw.strip()
            if not line or line.endswith(':'):
                continue
            if '=' not in line:
                continue
            k, v = line.split('=', 1)
            pairs.append((k, v))
    except Exception:
        pass
    return pairs

def _compute_removal_names(text):
    names = set()
    try:
        for raw in (text or '').split('\n'):
            s = raw.strip()
            if s.endswith(':'):
                names.add(s[:-1].strip().lower())
        if not names:
            # whitespace fallback
            for token in (text or '').split():
                if token.endswith(':'):
                    names.add(token[:-1].strip().lower())
    except Exception:
        pass
    return names

def _filter_headers_remove(headers, removal_names):
    if not removal_names:
        return headers
    out = []
    for h in headers:
        try:
            name = h.split(':', 1)[0].strip().lower()
            if name in removal_names:
                continue
        except Exception:
            pass
        out.append(h)
    return out

def _apply_header_replacements(headers, mr_model):
    out = []
    subs_simple = []
    subs_regex = []
    try:
        for _, v in mr_model.items():
            t = v.get('type') if isinstance(v, dict) else None
            if t == 'Headers (simple string):':
                subs_simple.append((v.get('match', ''), v.get('replace', '')))
            elif t == 'Headers (regex):':
                pat = v.get('_compiled')
                if pat is None:
                    raw = v.get('regexMatch', '')
                    try:
                        pat = re.compile(raw)
                    except Exception:
                        pat = None
                    v['_compiled'] = pat
                if pat is not None:
                    subs_regex.append((pat, v.get('replace', '')))
    except Exception:
        pass
    for h in headers:
        try:
            for m, r in subs_simple:
                if m:
                    h = h.replace(m, r)
            for pat, r in subs_regex:
                h = pat.sub(r, h)
        except Exception:
            pass
        out.append(h)
    return out

def _apply_body_replacements(body_bytes, mr_model, helpers):
    try:
        # Prepare rules
        simple = []
        regex = []
        for _, v in mr_model.items():
            t = v.get('type') if isinstance(v, dict) else None
            if t == 'Body (simple string):':
                simple.append((v.get('match', ''), v.get('replace', '')))
            elif t == 'Body (regex):':
                pat = v.get('_compiled_body')
                if pat is None:
                    raw = v.get('regexMatch', '')
                    try:
                        pat = re.compile(raw)
                    except Exception:
                        pat = None
                    v['_compiled_body'] = pat
                if pat is not None:
                    regex.append((pat, v.get('replace', '')))
        if not simple and not regex:
            return body_bytes
        s = helpers.bytesToString(body_bytes)
        for m, r in simple:
            if m:
                s = s.replace(m, r)
        for pat, r in regex:
            s = pat.sub(r, s)
        return helpers.stringToBytes(s)
    except Exception:
        return body_bytes

def isStatusCodesReturned(self, messageInfo, statusCodes):
    try:
        analyzed = self._helpers.analyzeResponse(messageInfo.getResponse())
        status_num = analyzed.getStatusCode()
        first_header = analyzed.getHeaders()[0]
    except Exception:
        status_num = None
        try:
            first_header = self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders()[0]
        except Exception:
            first_header = ""

    def _matches_one(sc):
        s = str(sc)
        if status_num is not None:
            try:
                if int(s) == status_num:
                    return True
            except Exception:
                pass
            if s == str(status_num):
                return True
        return s in first_header

    if isinstance(statusCodes, (list, tuple, set)):
        for sc in statusCodes:
            if _matches_one(sc):
                return True
        return False
    return _matches_one(statusCodes)

def makeRequest(self, messageInfo, message):
    requestURL = self._helpers.analyzeRequest(messageInfo).getUrl()
    return self._callbacks.makeHttpRequest(self._helpers.buildHttpService(str(requestURL.getHost()), int(requestURL.getPort()), requestURL.getProtocol() == "https"), message)

def makeMessage(self, messageInfo, removeOrNot, authorizeOrNot):
    requestInfo = self._helpers.analyzeRequest(messageInfo)
    headers = requestInfo.getHeaders()
    if removeOrNot:
        headers = list(headers)
        query_flag = self.replaceQueryParam.isSelected()
        if query_flag:
            pairs = _parse_query_pairs_from_text(self.replaceString.getText())
            if pairs:
                headers[0] = _update_request_line_params(headers[0], pairs)
        removal_names = _compute_removal_names(self.replaceString.getText())
        headers = _filter_headers_remove(headers, removal_names)

        if authorizeOrNot:
            headers = _apply_header_replacements(headers, self.badProgrammerMRModel)

            if not query_flag:
                replace_string_lines = list(self.replaceString.getText().split("\n"))
                for h in replace_string_lines:
                    if not h:
                        continue
                    if h.strip().endswith(':'):
                        continue
                    headers.append(h)

    msgBody = messageInfo.getRequest()[requestInfo.getBodyOffset():]

    if authorizeOrNot and msgBody is not None:
        msgBody = _apply_body_replacements(msgBody, self.badProgrammerMRModel, self._helpers)
    return self._helpers.buildHttpMessage(headers, msgBody)

def makeMessageWithReplaceText(self, messageInfo, removeOrNot, authorizeOrNot, replaceText, queryOverride=None):
    requestInfo = self._helpers.analyzeRequest(messageInfo)
    headers = requestInfo.getHeaders()
    
    if removeOrNot:
        headers = list(headers)
        query_flag = bool(queryOverride) if queryOverride is not None else self.replaceQueryParam.isSelected()
        if query_flag and replaceText is not None:
            pairs = _parse_query_pairs_from_text(replaceText)
            if pairs:
                headers[0] = _update_request_line_params(headers[0], pairs)

        removal_names = _compute_removal_names(replaceText)
        headers = _filter_headers_remove(headers, removal_names)

        if authorizeOrNot:
            headers = _apply_header_replacements(headers, self.badProgrammerMRModel)

            if not query_flag:
                replaceStringLines = replaceText.split("\n")
                for h in replaceStringLines:
                    if h and not h.strip().endswith(':'):
                        headers.append(h)

    msgBody = messageInfo.getRequest()[requestInfo.getBodyOffset():]

    if authorizeOrNot and msgBody is not None:
        msgBody = _apply_body_replacements(msgBody, self.badProgrammerMRModel, self._helpers)

    built = self._helpers.buildHttpMessage(headers, msgBody)
    return built

def getResponseBody(self, requestResponse):
    analyzedResponse = self._helpers.analyzeResponse(requestResponse.getResponse())
    return self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])

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
