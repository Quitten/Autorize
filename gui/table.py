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
from java.awt.event import MouseAdapter
from java.awt.event import ItemListener
from javax.swing.table import AbstractTableModel
from javax.swing.event import ListSelectionListener

from helpers.filters import expand, collapse

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
        base_columns = 6
        user_count = len(self._extender.userTab.user_tabs) if hasattr(self._extender, 'userTab') and self._extender.userTab else 0
        return base_columns + (user_count * 2)

    def getColumnName(self, columnIndex):
        base_columns = ['ID', 'Method', 'URL', 'Orig. Len', 'Unauth.len', 'Unauth. Status']

        if columnIndex < len(base_columns):
            return base_columns[columnIndex]
        
        try:
            if hasattr(self._extender, 'userTab') and self._extender.userTab:
                user_index = (columnIndex - len(base_columns)) // 2
                col_type = (columnIndex - len(base_columns)) % 2

                user_ids = sorted(self._extender.userTab.user_tabs.keys())

                if user_index < len(user_ids):
                    user_id = user_ids[user_index]
                    user_name = self._extender.userTab.user_tabs[user_id]['user_name']
                    
                    col_names = [
                        "{} Modif. Len".format(user_name), 
                        "{} Authz. Status".format(user_name)
                    ]

                    return col_names[col_type]

            return ""
        
        except (IndexError, KeyError):
            return ""

    def getColumnClass(self, columnIndex):
        base_classes = [Integer, String, String, Integer, Integer, String]
        
        if columnIndex < len(base_classes):
            return base_classes[columnIndex]
        
        try:
            col_type = (columnIndex - len(base_classes)) % 2
            user_col_classes = [Integer, String]
            return user_col_classes[col_type]
        
        except IndexError:
            return ""

    def getValueAt(self, rowIndex, columnIndex):
        logEntry = self._extender._log.get(rowIndex)
        
        if columnIndex == 0: # ID
            return logEntry._id
        if columnIndex == 1: # METHOD
            return logEntry._method
        if columnIndex == 2: # URL
            return logEntry._url.toString()
        if columnIndex == 3: # Original Request Length
            response = logEntry._originalrequestResponse.getResponse()
            return len(logEntry._originalrequestResponse.getResponse()) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
        if columnIndex == 4: # Unauthorized Request Length
            if logEntry._unauthorizedRequestResponse is not None:
                response = logEntry._unauthorizedRequestResponse.getResponse()
                return len(logEntry._unauthorizedRequestResponse.getResponse()) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
            else:
                return 0
        if columnIndex == 5:
            return logEntry._enfocementStatusUnauthorized

        # User columns
        if hasattr(self._extender, 'userTab') and self._extender.userTab and columnIndex >= 6:
            user_index = (columnIndex - 6) // 2
            col_type = (columnIndex - 6) % 2

            user_ids = sorted(self._extender.userTab.user_tabs.keys())
            if user_index < len(user_ids):
                user_id = user_ids[user_index]
                user_name = self._extender.userTab.user_tabs[user_id]['user_name']
                
                user_data = logEntry.get_user_enforcement(user_id)
                if user_data:
                    if col_type == 0:  # Modified Length
                        if user_data['requestResponse'] and user_data['requestResponse'].getResponse():
                            response = user_data['requestResponse'].getResponse()
                            return len(response) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
                        return 0
                    elif col_type == 1:  # Authorization Status
                        return user_data['enforcementStatus']
                        
        return ""

class TableSelectionListener(ListSelectionListener):
    """Class Responsible for the multi-row deletion"""
    def __init__(self, extender):
        self._extender = extender

    def valueChanged(self, e):
        rows = [i for i in self._table.getSelectedRows()]
        self._extender.tableModel.removeRows(rows)

class Table(JTable):
    def __init__(self, extender):
        self._extender = extender
        self._extender.tableModel = TableModel(extender)
        self.setModel(self._extender.tableModel)
        self.addMouseListener(Mouseclick(self._extender))
        self.setRowSelectionAllowed(True)

        # Enables multi-row selection
        self.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
        self.updateColumnWidths()

    def updateColumnWidths(self):
         if self.getColumnCount() > 0:
            self.getColumnModel().getColumn(0).setPreferredWidth(50)
            self.getColumnModel().getColumn(1).setPreferredWidth(80)
            self.getColumnModel().getColumn(2).setPreferredWidth(300)
            self.getColumnModel().getColumn(3).setPreferredWidth(80)
            self.getColumnModel().getColumn(4).setPreferredWidth(80)
            self.getColumnModel().getColumn(5).setPreferredWidth(120)
            
            if hasattr(self._extender, 'userTab'):
                user_count = len(self._extender.userTab.user_tabs)
                if user_count > 0:
                    col_width = 100
                    
                    for i in range(6, self.getColumnCount()):
                        self.getColumnModel().getColumn(i).setPreferredWidth(col_width)

    def prepareRenderer(self, renderer, row, col):
        comp = JTable.prepareRenderer(self, renderer, row, col)
        value = self._extender.tableModel.getValueAt(self._extender.logTable.convertRowIndexToModel(row), col)

        if col >= 5:
            if value == self._extender.BYPASSSED_STR:
                comp.setBackground(Color(255, 153, 153))
                comp.setForeground(Color.BLACK)
            elif value == self._extender.IS_ENFORCED_STR:
                comp.setBackground(Color(255, 204, 153))
                comp.setForeground(Color.BLACK)
            elif value == self._extender.ENFORCED_STR:
                comp.setBackground(Color(204, 255, 153))
                comp.setForeground(Color.BLACK)
            elif value == "Disabled":
                comp.setBackground(Color(211, 211, 211))
                comp.setForeground(Color.BLACK)
            else:
                comp.setForeground(Color.BLACK)
                comp.setBackground(Color.WHITE)
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
        
        current_user_name = "Original"
        current_request_response = logEntry._originalrequestResponse
        
        if col >= 6 and hasattr(self._extender, 'userTab') and self._extender.userTab:
            user_index = (col - 6) // 2
            user_ids = sorted(self._extender.userTab.user_tabs.keys())
            if user_index < len(user_ids):
                user_id = user_ids[user_index]
                user_name = self._extender.userTab.user_tabs[user_id]['user_name']
                user_data = logEntry.get_user_enforcement(user_id)
                if user_data and user_data['requestResponse']:
                    current_user_name = user_name
                    current_request_response = user_data['requestResponse']
        
        if col >= 4 and col < 6:  # Unauthenticated columns
            current_request_response = logEntry._unauthorizedRequestResponse
   
            current_user_name = "Unauthenticated"

        self._extender._requestViewer.setMessage(current_request_response.getRequest(), True)
        self._extender._responseViewer.setMessage(current_request_response.getResponse(), False)
        self._extender._originalrequestViewer.setMessage(logEntry._originalrequestResponse.getRequest(), True)
        self._extender._originalresponseViewer.setMessage(logEntry._originalrequestResponse.getResponse(), False)

        if logEntry._unauthorizedRequestResponse is not None:
            self._extender._unauthorizedrequestViewer.setMessage(logEntry._unauthorizedRequestResponse.getRequest(), True)
            self._extender._unauthorizedresponseViewer.setMessage(logEntry._unauthorizedRequestResponse.getResponse(), False)
        else:
            self._extender._unauthorizedrequestViewer.setMessage("Request disabled", True)
            self._extender._unauthorizedresponseViewer.setMessage("Response disabled", False)

        self._extender._currentlyDisplayedItem = logEntry

        self.updateTabTitles(current_user_name)

        if col == 2:  # URL column
            collapse(self._extender, self._extender.modified_requests_tabs)
            collapse(self._extender, self._extender.unauthenticated_requests_tabs)
            expand(self._extender, self._extender.original_requests_tabs)
        elif col >= 6:  # User columns
            collapse(self._extender, self._extender.original_requests_tabs)
            collapse(self._extender, self._extender.unauthenticated_requests_tabs)
            expand(self._extender, self._extender.modified_requests_tabs)
        elif col == 4 or col == 5:  # Unauth Status
            collapse(self._extender, self._extender.original_requests_tabs)
            collapse(self._extender, self._extender.modified_requests_tabs)
            expand(self._extender, self._extender.unauthenticated_requests_tabs)

        JTable.changeSelection(self, row, col, toggle, extend)
        return
    
    def updateTabTitles(self, user_name):
        if hasattr(self._extender, 'modified_requests_tabs'):
            self._extender.modified_requests_tabs.setTitleAt(0, "{} Modified Request".format(user_name))
            self._extender.modified_requests_tabs.setTitleAt(1, "{} Modified Response".format(user_name))

class LogEntry:
    def __init__(self, id, method, url, originalrequestResponse, unauthorizedRequestResponse=None, enforcementStatusUnauthorized="Disabled"):
        self._id = id
        self._method = method
        self._url = url
        self._originalrequestResponse = originalrequestResponse
        self._unauthorizedRequestResponse = unauthorizedRequestResponse
        self._enfocementStatusUnauthorized = enforcementStatusUnauthorized
        
        self._userEnforcements = {}
        
    def add_user_enforcement(self, user_id, requestResponse, enforcementStatus):
        self._userEnforcements[user_id] = {
            'requestResponse': requestResponse,
            'enforcementStatus': enforcementStatus
        }
    
    def get_user_enforcement(self, user_id):
        return self._userEnforcements.get(user_id, None)
    
    def get_all_users(self):
        return list(self._userEnforcements.keys())
    
    def has_user_data(self, user_id):
        return user_id in self._userEnforcements

class Mouseclick(MouseAdapter):
    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        if evt.button == 3:
            self._extender.menu.show(evt.getComponent(), evt.getX(), evt.getY())

class TableRowFilter(RowFilter):
    def __init__(self, extender):
        self._extender = extender

    def include(self, entry):
        modif_status = entry.getValue(7) if entry.getValueCount() > 7 else ""
        unauth_status = entry.getValue(5) if entry.getValueCount() > 5 else ""
        
        if (self._extender.showAuthBypassModified.isSelected() and self._extender.BYPASSSED_STR == modif_status) or \
           (self._extender.showAuthPotentiallyEnforcedModified.isSelected() and self._extender.IS_ENFORCED_STR == modif_status) or \
           (self._extender.showAuthEnforcedModified.isSelected() and self._extender.ENFORCED_STR == modif_status) or \
           (self._extender.showAuthBypassUnauthenticated.isSelected() and self._extender.BYPASSSED_STR == unauth_status) or \
           (self._extender.showAuthPotentiallyEnforcedUnauthenticated.isSelected() and self._extender.IS_ENFORCED_STR == unauth_status) or \
           (self._extender.showAuthEnforcedUnauthenticated.isSelected() and self._extender.ENFORCED_STR == unauth_status) or \
           (self._extender.showDisabledUnauthenticated.isSelected() and "Disabled" == unauth_status):
            return True
        
        return False

class UpdateTableEDT(Runnable):
    def __init__(self,extender,action,firstRow,lastRow):
        self._extender=extender
        self._action=action
        self._firstRow=firstRow
        self._lastRow=lastRow

    def run(self):
        if self._action == "insert":
            self._extender.tableModel.fireTableRowsInserted(self._firstRow, self._lastRow)
        elif self._action == "update":
            self._extender.tableModel.fireTableRowsUpdated(self._firstRow, self._lastRow)
        elif self._action == "delete":
            self._extender.tableModel.fireTableRowsDeleted(self._firstRow, self._lastRow)
        else:
            print("Invalid action in UpdateTableEDT")

