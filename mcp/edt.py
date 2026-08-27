#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Concurrency helpers for the MCP layer.
#
# Two categories of Autorize state, each with exactly one access rule:
#   1. _log / LogEntry / IHttpRequestResponse data  -> snapshot_log() (brief lock)
#   2. any Swing-backed state (JCheckBox/JTextArea/DefaultListModel/JTabbedPane,
#      userTab.*, EDModel, MRModel, IFModel, ...)   -> run_on_edt()
#
# MCP handler threads are never the EDT, so run_on_edt() always dispatches via
# invokeAndWait. Never call run_on_edt() while holding extender._lock.

from javax.swing import SwingUtilities
from java.lang import Runnable


class _EDTCall(Runnable):
    def __init__(self, fn):
        self.fn = fn
        self.result = None
        self.exception = None

    def run(self):
        try:
            self.result = self.fn()
        except Exception as e:
            self.exception = e


def run_on_edt(fn):
    """Run fn() synchronously on the Swing EDT and return its result.

    Required for any read or write of Swing-backed Autorize state.
    """
    if SwingUtilities.isEventDispatchThread():
        return fn()
    call = _EDTCall(fn)
    SwingUtilities.invokeAndWait(call)
    if call.exception is not None:
        raise call.exception
    return call.result


def snapshot_log(extender):
    """Take a quick, lock-protected snapshot of LogEntry references.

    Mirrors the lock discipline in authorization.checkAuthorizationAllUsers and
    gui.configuration_tab.ClearTableRunnable. No slow work is done under the lock;
    callers format/serialize the returned entries outside of it.
    """
    extender._lock.acquire()
    try:
        return list(extender._log.toArray())
    finally:
        extender._lock.release()
