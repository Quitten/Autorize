#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from java.awt import Color
from java.lang import String
from java.lang import Integer
from java.lang import Runnable
from javax.swing import JTable
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing import RowFilter
from javax.swing import JCheckBox
from javax.swing import GroupLayout
from javax.swing import ListSelectionModel
from javax.swing import JTabbedPane
from java.awt.event import MouseAdapter
from java.awt.event import ContainerAdapter
from java.awt.event import ItemListener
from javax.swing.table import AbstractTableModel

from helpers.filters import expand, collapse
from burp import IMessageEditorController

class TableFilter():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """
        init show tab
        """

        filterLModified = JLabel("Modified:")
        filterLModified.setBounds(10, 10, 100, 30)

        filterLUnauthenticated = JLabel("Unauthenticated:")
        filterLUnauthenticated.setBounds(250, 10, 100, 30)

        self._extender.showAuthBypassModified = JCheckBox(self._extender.BYPASSSED_STR)
        self._extender.showAuthBypassModified.setBounds(10, 35, 200, 30)
        self._extender.showAuthBypassModified.setSelected(True)
        self._extender.showAuthBypassModified.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthPotentiallyEnforcedModified = JCheckBox("Is enforced???")
        self._extender.showAuthPotentiallyEnforcedModified.setBounds(10, 60, 200, 30)
        self._extender.showAuthPotentiallyEnforcedModified.setSelected(True)
        self._extender.showAuthPotentiallyEnforcedModified.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthEnforcedModified = JCheckBox(self._extender.ENFORCED_STR)
        self._extender.showAuthEnforcedModified.setBounds(10, 85, 200, 30)
        self._extender.showAuthEnforcedModified.setSelected(True)
        self._extender.showAuthEnforcedModified.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthBypassUnauthenticated = JCheckBox(self._extender.BYPASSSED_STR)
        self._extender.showAuthBypassUnauthenticated.setBounds(250, 35, 200, 30)
        self._extender.showAuthBypassUnauthenticated.setSelected(True)
        self._extender.showAuthBypassUnauthenticated.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthPotentiallyEnforcedUnauthenticated = JCheckBox("Is enforced???")
        self._extender.showAuthPotentiallyEnforcedUnauthenticated.setBounds(250, 60, 200, 30)
        self._extender.showAuthPotentiallyEnforcedUnauthenticated.setSelected(True)
        self._extender.showAuthPotentiallyEnforcedUnauthenticated.addItemListener(TabTableFilter(self._extender))

        self._extender.showAuthEnforcedUnauthenticated = JCheckBox(self._extender.ENFORCED_STR)
        self._extender.showAuthEnforcedUnauthenticated.setBounds(250, 85, 200, 30)
        self._extender.showAuthEnforcedUnauthenticated.setSelected(True)
        self._extender.showAuthEnforcedUnauthenticated.addItemListener(TabTableFilter(self._extender))

        self._extender.showDisabledUnauthenticated = JCheckBox("Disabled")
        self._extender.showDisabledUnauthenticated.setBounds(250, 110, 200, 30)
        self._extender.showDisabledUnauthenticated.setSelected(True)
        self._extender.showDisabledUnauthenticated.addItemListener(TabTableFilter(self._extender))        

        self._extender.filterPnl = JPanel()
        layout = GroupLayout(self._extender.filterPnl)
        self._extender.filterPnl.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        layout.setHorizontalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup()
                .addComponent(
                    filterLModified,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.showAuthBypassModified,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.showAuthPotentiallyEnforcedModified,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.showAuthEnforcedModified,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(
                    filterLUnauthenticated,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.showAuthBypassUnauthenticated,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.showAuthPotentiallyEnforcedUnauthenticated,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.showAuthEnforcedUnauthenticated,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.showDisabledUnauthenticated,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
        )
        
        
        layout.setVerticalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                    filterLModified,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    filterLUnauthenticated,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addGroup(layout.createSequentialGroup()
                    .addComponent(
                        self._extender.showAuthBypassModified,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.showAuthPotentiallyEnforcedModified,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.showAuthEnforcedModified,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
                .addGroup(layout.createSequentialGroup()
                    .addComponent(
                        self._extender.showAuthBypassUnauthenticated,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.showAuthPotentiallyEnforcedUnauthenticated,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.showAuthEnforcedUnauthenticated,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.showDisabledUnauthenticated,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
            )
        )

class TabTableFilter(ItemListener):
    def __init__(self, extender):
        self._extender = extender

    def itemStateChanged(self, e):
        self._extender.tableSorter.sort()

class TableModel(AbstractTableModel):
    def __init__(self, extender):
        self._extender = extender

    def removeRows(self, rows):
        rows.sort(reverse=True)
        for row in rows:
            self._extender._log.pop(row)
        self.fireTableDataChanged()

    def getRowCount(self):
        try:
            return self._extender._log.size()
        except:
            return 0

    def getColumnCount(self):
        return 8

    def getColumnName(self, columnIndex):
        data = ['ID','Method', 'URL', 'Orig. Len', 'Modif. Len', "Unauth. Len",
                "Authz. Status", "Unauth. Status"]
        try:
            return data[columnIndex]
        except IndexError:
            return ""

    def getColumnClass(self, columnIndex):
        data = [Integer, String, String, Integer, Integer, Integer, String, String]
        try:
            return data[columnIndex]
        except IndexError:
            return ""

    def getValueAt(self, rowIndex, columnIndex):
        logEntry = self._extender._log.get(rowIndex)
        if columnIndex == 0:
            return logEntry._id
        if columnIndex == 1:
            return logEntry._method
        if columnIndex == 2:
            return logEntry._url.toString()
        if columnIndex == 3:
            response = logEntry._originalrequestResponse.getResponse()
            return len(logEntry._originalrequestResponse.getResponse()) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
        if columnIndex == 4:
            response = logEntry._requestResponse.getResponse()
            return len(logEntry._requestResponse.getResponse()) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
        if columnIndex == 5:
            if logEntry._unauthorizedRequestResponse is not None:
                response = logEntry._unauthorizedRequestResponse.getResponse()
                return len(logEntry._unauthorizedRequestResponse.getResponse()) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
            else:
                return 0
        if columnIndex == 6:
            return logEntry._enfocementStatus   
        if columnIndex == 7:
            return logEntry._enfocementStatusUnauthorized        
        return ""

class Table(JTable):
    def __init__(self, extender):
        self._extender = extender
        self._extender.tableModel = TableModel(extender)
        self.setModel(self._extender.tableModel)
        self.addMouseListener(Mouseclick(self._extender))
        self.getColumnModel().getColumn(0).setPreferredWidth(450)
        self.setRowSelectionAllowed(True)
        self.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)

    def prepareRenderer(self, renderer, row, col):
        comp = JTable.prepareRenderer(self, renderer, row, col)
        value = self._extender.tableModel.getValueAt(self._extender.logTable.convertRowIndexToModel(row), col)
        if col == 6 or col == 7:
            if value == self._extender.BYPASSSED_STR:
                comp.setBackground(Color(255, 153, 153))
                comp.setForeground(Color.BLACK)
            elif value == self._extender.IS_ENFORCED_STR:
                comp.setBackground(Color(255, 204, 153))
                comp.setForeground(Color.BLACK)
            elif value == self._extender.ENFORCED_STR:
                comp.setBackground(Color(204, 255, 153))
                comp.setForeground(Color.BLACK)
        else:
            comp.setForeground(Color.BLACK)
            comp.setBackground(Color.WHITE)

        selectedRows = self._extender.logTable.getSelectedRows()
        if row in selectedRows:
            comp.setBackground(Color(201, 215, 255))
            comp.setForeground(Color.BLACK)

        return comp
    
    def changeSelection(self, row, col, toggle, extend):
        logEntry = self._extender._log.get(self._extender.logTable.convertRowIndexToModel(row))
        try:
            self._extender._contextRequestResponse = None
        except Exception:
            pass

        try:
            tabs = self._extender.modified_requests_tabs
            while tabs.getTabCount() > 0:
                tabs.removeTabAt(0)

            modified_list = getattr(logEntry, '_modified_list', []) or []
            impressions = getattr(logEntry, '_modified_impressions', []) or []
            titles = getattr(logEntry, '_modified_rule_titles', []) or []

            if len(modified_list) > 0:
                tab_rr_map = []
                def _attach_popup_deep(comp, rr):
                    try:
                        try:
                            comp.putClientProperty("autorize-rr", rr)
                        except Exception:
                            pass
                        try:
                            comp.addMouseListener(ShiftEditorPopupListener(self._extender))
                        except Exception:
                            pass
                        try:
                            if hasattr(comp, 'getComponentCount') and hasattr(comp, 'getComponent'):
                                try:
                                    count = comp.getComponentCount()
                                except Exception:
                                    count = 0
                                for ci in range(0, count):
                                    try:
                                        child = comp.getComponent(ci)
                                        _attach_popup_deep(child, rr)
                                    except Exception:
                                        pass
                        except Exception:
                            pass
                    except Exception:
                        pass

                def _attach_container_listener_deep(comp, rr):
                    try:
                        class PopupPropagator(ContainerAdapter):
                            def __init__(self, rr_local):
                                self._rr_local = rr_local
                            def componentAdded(self, e):
                                try:
                                    child = e.getChild()
                                except Exception:
                                    child = None
                                if child is not None:
                                    try:
                                        _attach_popup_deep(child, self._rr_local)
                                    except Exception:
                                        pass
                                    try:
                                        _attach_container_listener_deep(child, self._rr_local)
                                    except Exception:
                                        pass
                        
                        if hasattr(comp, 'addContainerListener'):
                            try:
                                comp.addContainerListener(PopupPropagator(rr))
                            except Exception:
                                pass
                        
                        if hasattr(comp, 'getComponentCount') and hasattr(comp, 'getComponent'):
                            try:
                                cnt = comp.getComponentCount()
                            except Exception:
                                cnt = 0
                            for ci in range(0, cnt):
                                try:
                                    ch = comp.getComponent(ci)
                                    _attach_container_listener_deep(ch, rr)
                                except Exception:
                                    pass
                    except Exception:
                        pass
                for i, rr in enumerate(modified_list):
                    rule_name = titles[i] if i < len(titles) and titles[i] else "Rule {}".format(i+1)
                    impression = impressions[i] if i < len(impressions) else ""
                    
                    try:
                        controller = StaticMessageEditorController(rr)
                    except Exception:
                        controller = None
                    req_editor = self._extender._callbacks.createMessageEditor(controller, True)
                    res_editor = self._extender._callbacks.createMessageEditor(controller, True)
                    try:
                        req_editor.setMessage(rr.getRequest(), True)
                        res_editor.setMessage(rr.getResponse(), False)
                    except Exception:
                        pass
                    
                    req_comp = req_editor.getComponent()
                    res_comp = res_editor.getComponent()
                    _attach_popup_deep(req_comp, rr)
                    _attach_popup_deep(res_comp, rr)
                    _attach_container_listener_deep(req_comp, rr)
                    _attach_container_listener_deep(res_comp, rr)
                    tabs.addTab("M{} {} Req".format(i+1, rule_name), req_comp)
                    tabs.setToolTipTextAt(tabs.getTabCount()-1, "Modified {} Request".format(rule_name))
                    tab_rr_map.append(rr)
                    
                    try:
                        ridx = tabs.getTabCount()-1
                        if impression == self._extender.BYPASSSED_STR:
                            tabs.setBackgroundAt(ridx, Color(255, 153, 153))
                        elif impression == self._extender.IS_ENFORCED_STR:
                            tabs.setBackgroundAt(ridx, Color(255, 204, 153))
                        elif impression == self._extender.ENFORCED_STR:
                            tabs.setBackgroundAt(ridx, Color(204, 255, 153))
                    except Exception:
                        pass
                    tabs.addTab("M{} {} Res".format(i+1, rule_name), res_comp)
                    tabs.setToolTipTextAt(tabs.getTabCount()-1, "{} [{}]".format(rule_name, impression))
                    tab_rr_map.append(rr)
                    
                    try:
                        idx = tabs.getTabCount()-1
                        if impression == self._extender.BYPASSSED_STR:
                            tabs.setBackgroundAt(idx, Color(255, 153, 153))
                        elif impression == self._extender.IS_ENFORCED_STR:
                            tabs.setBackgroundAt(idx, Color(255, 204, 153))
                        elif impression == self._extender.ENFORCED_STR:
                            tabs.setBackgroundAt(idx, Color(204, 255, 153))
                    except Exception:
                        pass
                try:
                    tabs.putClientProperty("autorize-tab-rr-map", tab_rr_map)
                    tabs.putClientProperty("autorize-last-index", 0)
                except Exception:
                    pass
            else:
                self._extender._requestViewer.setMessage(logEntry._requestResponse.getRequest(), True)
                self._extender._responseViewer.setMessage(logEntry._requestResponse.getResponse(), False)
                tabs.addTab("Modified Request", self._extender._requestViewer.getComponent())
                tabs.addTab("Modified Response", self._extender._responseViewer.getComponent())

            tabs.addTab("Expand", None)
            tabs.setSelectedIndex(0)
        except Exception:
            self._extender._requestViewer.setMessage(logEntry._requestResponse.getRequest(), True)
            self._extender._responseViewer.setMessage(logEntry._requestResponse.getResponse(), False)

        self._extender._originalrequestViewer.setMessage(logEntry._originalrequestResponse.getRequest(), True)
        self._extender._originalresponseViewer.setMessage(logEntry._originalrequestResponse.getResponse(), False)

        if logEntry._unauthorizedRequestResponse is not None:
            self._extender._unauthorizedrequestViewer.setMessage(logEntry._unauthorizedRequestResponse.getRequest(), True)
            self._extender._unauthorizedresponseViewer.setMessage(logEntry._unauthorizedRequestResponse.getResponse(), False)
        else:
            self._extender._unauthorizedrequestViewer.setMessage("Request disabled", True)
            self._extender._unauthorizedresponseViewer.setMessage("Response disabled", False)

        self._extender._currentlyDisplayedItem = logEntry

        if col == 3:
            collapse(self._extender, self._extender.modified_requests_tabs)
            collapse(self._extender, self._extender.unauthenticated_requests_tabs)
            expand(self._extender, self._extender.original_requests_tabs)
        elif col == 4 or col == 6:
            collapse(self._extender, self._extender.original_requests_tabs)
            collapse(self._extender, self._extender.unauthenticated_requests_tabs)
            expand(self._extender, self._extender.modified_requests_tabs)
        elif col == 5 or col == 7:
            collapse(self._extender, self._extender.original_requests_tabs)
            collapse(self._extender, self._extender.modified_requests_tabs)
            expand(self._extender, self._extender.unauthenticated_requests_tabs)
        else:
            collapse(self._extender, self._extender.original_requests_tabs)
            collapse(self._extender, self._extender.modified_requests_tabs)
            collapse(self._extender, self._extender.unauthenticated_requests_tabs)

        JTable.changeSelection(self, row, col, toggle, extend)
        return

class StaticMessageEditorController(IMessageEditorController):
    def __init__(self, rr):
        self._rr = rr

    def getHttpService(self):
        try:
            return self._rr.getHttpService()
        except Exception:
            return None

    def getRequest(self):
        try:
            return self._rr.getRequest()
        except Exception:
            return None

    def getResponse(self):
        try:
            return self._rr.getResponse()
        except Exception:
            return None

class LogEntry:
    def __init__(self, id, requestResponse, method, url, originalrequestResponse, enforcementStatus, unauthorizedRequestResponse, enforcementStatusUnauthorized):
        self._id = id
        self._requestResponse = requestResponse
        self._originalrequestResponse = originalrequestResponse
        self._method = method
        self._url = url
        self._enfocementStatus =  enforcementStatus
        self._unauthorizedRequestResponse = unauthorizedRequestResponse
        self._enfocementStatusUnauthorized =  enforcementStatusUnauthorized
        self._modified_list = []
        self._modified_impressions = []
        self._modified_rule_titles = []
        return

class Mouseclick(MouseAdapter):
    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        if evt.button == 3:
            self._extender.menu.show(evt.getComponent(), evt.getX(), evt.getY())

class ShiftEditorPopupListener(MouseAdapter):
    def __init__(self, extender):
        self._extender = extender
    def _maybe_show(self, evt):
        try:
            if not evt.isShiftDown():
                return
        except Exception:
            return
        try:
            comp = evt.getComponent()
            self._extender.menu.show(comp, evt.getX(), evt.getY())
        except Exception:
            pass
    def mousePressed(self, evt):
        if getattr(evt, 'button', None) == 3:
            self._maybe_show(evt)
    def mouseReleased(self, evt):
        if hasattr(evt, 'isPopupTrigger') and evt.isPopupTrigger():
            self._maybe_show(evt)

class TableRowFilter(RowFilter):
    def __init__(self, extender):
        self._extender = extender

    def include(self, entry):
        if self._extender.showAuthBypassModified.isSelected() and self._extender.BYPASSSED_STR == entry.getValue(6):
            return True
        elif self._extender.showAuthPotentiallyEnforcedModified.isSelected() and self._extender.IS_ENFORCED_STR == entry.getValue(6):
            return True
        elif self._extender.showAuthEnforcedModified.isSelected() and self._extender.ENFORCED_STR == entry.getValue(6):
            return True
        elif self._extender.showAuthBypassUnauthenticated.isSelected() and self._extender.BYPASSSED_STR == entry.getValue(7):
            return True
        elif self._extender.showAuthPotentiallyEnforcedUnauthenticated.isSelected() and self._extender.IS_ENFORCED_STR == entry.getValue(7):
            return True
        elif self._extender.showAuthEnforcedUnauthenticated.isSelected() and self._extender.ENFORCED_STR == entry.getValue(7):
            return True
        elif self._extender.showDisabledUnauthenticated.isSelected() and "Disabled" == entry.getValue(7):
            return True
        else:
            return False

class UpdateTableEDT(Runnable):
    def __init__(self,extender,action,firstRow,lastRow):
        self._extender=extender
        self._action=action
        self._firstRow=firstRow
        self._lastRow=lastRow

    def run(self):
        try:
            if self._action == "insert":
                self._extender.tableModel.fireTableRowsInserted(self._firstRow, self._lastRow)
            elif self._action == "update":
                self._extender.tableModel.fireTableRowsUpdated(self._firstRow, self._lastRow)
            elif self._action == "delete":
                self._extender.tableModel.fireTableRowsDeleted(self._firstRow, self._lastRow)
            else:
                pass
        except Exception as ex:
            print("Table EDT error:", ex)


