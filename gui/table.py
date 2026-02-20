#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from java.awt import Color
from java.lang import String
from java.lang import Integer
from java.lang import Runnable
from javax.swing import JTable
from javax.swing import JPanel
from javax.swing import RowFilter
from javax.swing import JCheckBox
from javax.swing import ListSelectionModel
from java.awt.event import MouseAdapter
from java.awt.event import ItemListener
from java.awt import FlowLayout
from javax.swing.table import AbstractTableModel
from javax.swing.event import ListSelectionListener

from helpers.filters import expand, collapse, rebuildViewerPanel

class TableFilter():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """
        init show tab
        """
        self._extender.filterPnl = JPanel(FlowLayout(FlowLayout.LEFT))

        self._extender.showBypassed = JCheckBox(self._extender.BYPASSSED_STR)
        self._extender.showBypassed.setSelected(True)
        self._extender.showBypassed.addItemListener(TabTableFilter(self._extender))

        self._extender.showIsEnforced = JCheckBox("Is enforced???")
        self._extender.showIsEnforced.setSelected(True)
        self._extender.showIsEnforced.addItemListener(TabTableFilter(self._extender))

        self._extender.showEnforced = JCheckBox(self._extender.ENFORCED_STR)
        self._extender.showEnforced.setSelected(True)
        self._extender.showEnforced.addItemListener(TabTableFilter(self._extender))

        self._extender.filterPnl.add(self._extender.showBypassed)
        self._extender.filterPnl.add(self._extender.showIsEnforced)
        self._extender.filterPnl.add(self._extender.showEnforced)

class TabTableFilter(ItemListener):
    def __init__(self, extender):
        self._extender = extender

    def itemStateChanged(self, e):
        if hasattr(self._extender, 'tableSorter'):
            self._extender.tableSorter.sort()

        if hasattr(self._extender, 'logTable'):
            self._extender.logTable.repaint()

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

    def _get_visible_columns(self):
        """Return list of data column indices that are visible (based on viewer_visibility)."""
        visible = []
        visibility = getattr(self._extender, 'viewer_visibility', {})
        if visibility.get('original', True):
            visible.append(3)  # Orig. Len
        if visibility.get('unauthenticated', True):
            visible.extend([4, 5])  # Unauth.len, Unauth. Status
        if hasattr(self._extender, 'userTab') and self._extender.userTab:
            for i, user_id in enumerate(sorted(self._extender.userTab.user_tabs.keys())):
                key = 'user_{}'.format(user_id)
                if visibility.get(key, True):
                    visible.extend([6 + i * 2, 6 + i * 2 + 1])  # User Len, User Status
        return [0, 1, 2] + visible  # ID, Method, URL always visible

    def getDataColumnIndex(self, viewColumnIndex):
        """Map view column index to data column index."""
        visible = self._get_visible_columns()
        if 0 <= viewColumnIndex < len(visible):
            return visible[viewColumnIndex]
        return -1

    def getViewColumnIndex(self, dataColumnIndex):
        """Map data column index to view column index, or -1 if hidden."""
        visible = self._get_visible_columns()
        if dataColumnIndex in visible:
            return visible.index(dataColumnIndex)
        return -1

    def getColumnCount(self):
        return len(self._get_visible_columns())

    def getColumnName(self, columnIndex):
        dataCol = self.getDataColumnIndex(columnIndex)
        if dataCol < 0:
            return ""
        base_columns = ['ID', 'Method', 'URL', 'Orig. Len', 'Unauth.len', 'Unauth. Status']
        if dataCol < len(base_columns):
            return base_columns[dataCol]
        try:
            if hasattr(self._extender, 'userTab') and self._extender.userTab:
                user_index = (dataCol - len(base_columns)) // 2
                col_type = (dataCol - len(base_columns)) % 2
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
        dataCol = self.getDataColumnIndex(columnIndex)
        if dataCol < 0:
            return ""
        base_classes = [Integer, String, String, Integer, Integer, String]
        if dataCol < len(base_classes):
            return base_classes[dataCol]
        col_type = (dataCol - len(base_classes)) % 2
        user_col_classes = [Integer, String]
        return user_col_classes[col_type]

    def _getValueAtDataColumn(self, rowIndex, dataCol):
        """Get value at (rowIndex, dataCol) using data column index."""
        logEntry = self._extender._log.get(rowIndex)
        if dataCol == 0:
            return logEntry._id
        if dataCol == 1:
            return logEntry._method
        if dataCol == 2:
            return logEntry._url.toString()
        if dataCol == 3:
            response = logEntry._originalrequestResponse.getResponse()
            return len(logEntry._originalrequestResponse.getResponse()) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
        if dataCol == 4:
            if logEntry._unauthorizedRequestResponse is not None:
                response = logEntry._unauthorizedRequestResponse.getResponse()
                return len(logEntry._unauthorizedRequestResponse.getResponse()) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
            return 0
        if dataCol == 5:
            return logEntry._enfocementStatusUnauthorized
        if hasattr(self._extender, 'userTab') and self._extender.userTab and dataCol >= 6:
            user_index = (dataCol - 6) // 2
            col_type = (dataCol - 6) % 2
            user_ids = sorted(self._extender.userTab.user_tabs.keys())
            if user_index < len(user_ids):
                user_id = user_ids[user_index]
                user_data = logEntry.get_user_enforcement(user_id)
                if user_data:
                    if col_type == 0:
                        if user_data['requestResponse'] and user_data['requestResponse'].getResponse():
                            response = user_data['requestResponse'].getResponse()
                            return len(response) - self._extender._helpers.analyzeResponse(response).getBodyOffset()
                        return 0
                    elif col_type == 1:
                        return user_data['enforcementStatus']
        return ""

    def getValueAt(self, rowIndex, columnIndex):
        dataCol = self.getDataColumnIndex(columnIndex)
        if dataCol < 0:
            return ""
        return self._getValueAtDataColumn(rowIndex, dataCol)
    
class ColorConstants:
    BLACK = Color.BLACK
    WHITE = Color.WHITE
    BYPASSED_BG = Color(255, 153, 153)    # Light red
    IS_ENFORCED_BG = Color(255, 204, 153) # Light orange
    ENFORCED_BG = Color(204, 255, 153)    # Light green
    DISABLED_BG = Color(211, 211, 211)    # Light gray
    SELECTED_BG = Color(201, 215, 255) 

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
            column_model = self.getColumnModel()
            widths_by_data_col = [50, 80, 300, 80, 80, 120]
            for view_idx in range(self.getColumnCount()):
                data_col = self._extender.tableModel.getDataColumnIndex(view_idx)
                width = widths_by_data_col[data_col] if data_col < len(widths_by_data_col) else 100
                column_model.getColumn(view_idx).setPreferredWidth(width)

    def prepareRenderer(self, renderer, row, col):
        comp = JTable.prepareRenderer(self, renderer, row, col)
        data_col = self._extender.tableModel.getDataColumnIndex(col)
        model_row = self._extender.logTable.convertRowIndexToModel(row)

        if data_col < 4:
            comp.setForeground(ColorConstants.BLACK)
            comp.setBackground(ColorConstants.WHITE)
            selected_rows = self._extender.logTable.getSelectedRows()
            if row in selected_rows:
                comp.setBackground(ColorConstants.SELECTED_BG)
            return comp

        value = self._extender.tableModel.getValueAt(model_row, col)
        comp.setForeground(Color.BLACK)
        comp.setBackground(Color.WHITE)
        should_mask = False

        if data_col == 4:
            status_view_col = self._extender.tableModel.getViewColumnIndex(5)
            status_value = self._extender.tableModel.getValueAt(model_row, status_view_col) if status_view_col >= 0 else ""
            should_mask = not self.shouldShowStatus(status_value)
        elif data_col == 5:
            should_mask = not self.shouldShowStatus(value)
        elif data_col >= 6:
            if data_col & 1:
                should_mask = not self.shouldShowStatus(value)
            else:
                status_view_col = self._extender.tableModel.getViewColumnIndex(data_col + 1)
                if status_view_col >= 0:
                    status_value = self._extender.tableModel.getValueAt(model_row, status_view_col)
                    should_mask = not self.shouldShowStatus(status_value)

        if should_mask:
            comp.setText("")
            comp.setBackground(Color.WHITE)
            comp.setForeground(Color.WHITE)
        elif data_col >= 4:
            if data_col == 5 or (data_col >= 6 and data_col & 1):
                if value == self._extender.BYPASSSED_STR:
                    comp.setBackground(ColorConstants.BYPASSED_BG)
                elif value == self._extender.IS_ENFORCED_STR:
                    comp.setBackground(ColorConstants.IS_ENFORCED_BG)
                elif value == self._extender.ENFORCED_STR:
                    comp.setBackground(ColorConstants.ENFORCED_BG)
                elif value == "Disabled":
                    comp.setBackground(ColorConstants.DISABLED_BG)
                comp.setForeground(ColorConstants.BLACK)

        selected_rows = self._extender.logTable.getSelectedRows()
        if row in selected_rows and not should_mask:
            comp.setBackground(ColorConstants.SELECTED_BG)
            comp.setForeground(ColorConstants.BLACK)

        return comp
    
    def shouldShowStatus(self, status):
        if not hasattr(self._extender, 'showBypassed'):
            return True
        
        if (self._extender.showBypassed.isSelected() and
            self._extender.showIsEnforced.isSelected() and
            self._extender.showEnforced.isSelected()):
            return True
        
        if status == "Disabled":
            return True
        elif self._extender.showBypassed.isSelected() and self._extender.BYPASSSED_STR == status:
            return True
        elif self._extender.showIsEnforced.isSelected() and self._extender.IS_ENFORCED_STR == status:
            return True
        elif self._extender.showEnforced.isSelected() and self._extender.ENFORCED_STR == status:
            return True
        
        return False

    def changeSelection(self, row, col, toggle, extend):
        logEntry = self._extender._log.get(self._extender.logTable.convertRowIndexToModel(row))
        data_col = self._extender.tableModel.getDataColumnIndex(col)

        if hasattr(self._extender, 'user_viewers'):
            for user_id, viewer in self._extender.user_viewers.items():
                user_data = logEntry.get_user_enforcement(user_id)
                if user_data and user_data['requestResponse']:
                    viewer['requestViewer'].setMessage(user_data['requestResponse'].getRequest(), True)
                    viewer['responseViewer'].setMessage(user_data['requestResponse'].getResponse(), False)
                else:
                    viewer['requestViewer'].setMessage("No data for this user", True)
                    viewer['responseViewer'].setMessage("No data for this user", False)

        self._extender._originalrequestViewer.setMessage(logEntry._originalrequestResponse.getRequest(), True)
        self._extender._originalresponseViewer.setMessage(logEntry._originalrequestResponse.getResponse(), False)

        if logEntry._unauthorizedRequestResponse is not None:
            self._extender._unauthorizedrequestViewer.setMessage(logEntry._unauthorizedRequestResponse.getRequest(), True)
            self._extender._unauthorizedresponseViewer.setMessage(logEntry._unauthorizedRequestResponse.getResponse(), False)
        else:
            self._extender._unauthorizedrequestViewer.setMessage("Request disabled", True)
            self._extender._unauthorizedresponseViewer.setMessage("Response disabled", False)

        self._extender._currentlyDisplayedItem = logEntry

        if data_col == 2:
            rebuildViewerPanel(self._extender)
        elif data_col == 3:
            if self._extender.viewer_visibility.get('original', True):
                expand(self._extender, self._extender.original_requests_tabs)
        elif data_col == 4 or data_col == 5:
            if self._extender.viewer_visibility.get('unauthenticated', True):
                expand(self._extender, self._extender.unauthenticated_requests_tabs)
        elif data_col >= 6 and hasattr(self._extender, 'userTab') and self._extender.userTab:
            user_ids = sorted(self._extender.userTab.user_tabs.keys())
            user_index = (data_col - 6) >> 1
            if user_index < len(user_ids):
                user_id = user_ids[user_index]
                key = 'user_{}'.format(user_id)
                if self._extender.viewer_visibility.get(key, True) and user_id in self._extender.user_viewers:
                    expand(self._extender, self._extender.user_viewers[user_id]['tabs'])

        self.updateContextMenuText(col)

        JTable.changeSelection(self, row, col, toggle, extend)
        return

    def updateContextMenuText(self, col):
        data_col = self._extender.tableModel.getDataColumnIndex(col)
        modified_text = "Send Modified Request to Repeater"
        comparer_text = "Send Responses to Comparer"
        if data_col >= 6 and hasattr(self._extender, 'userTab') and self._extender.userTab:
            user_index = (data_col - 6) // 2
            user_ids = sorted(self._extender.userTab.user_tabs.keys())
            if user_index < len(user_ids):
                user_id = user_ids[user_index]
                user_name = self._extender.userTab.user_tabs[user_id]['user_name']
                modified_text = "Send {} Request to Repeater".format(user_name)
                comparer_text = "Send {} Responses to Comparer".format(user_name)
        elif data_col == 4 or data_col == 5:
            modified_text = "Send Unauthenticated Request to Repeater"
            comparer_text = "Send Unauthenticated Responses to Comparer"
        if hasattr(self._extender, 'sendRequestMenu2'):
            self._extender.sendRequestMenu2.setText(modified_text)
        if hasattr(self._extender, 'sendResponseMenu'):
            self._extender.sendResponseMenu.setText(comparer_text)

    def updateTabTitles(self, user_name):
        if hasattr(self._extender, 'modified_requests_tabs'):
            self._extender.modified_requests_tabs.setTitleAt(0, "{} Request".format(user_name))
            self._extender.modified_requests_tabs.setTitleAt(1, "{} Response".format(user_name))

class TableExtension:
    def prepareRenderer(self, renderer, row, col):
        comp = JTable.prepareRenderer(self, renderer, row, col)
        data_col = self._extender.tableModel.getDataColumnIndex(col)
        model_row = self._extender.logTable.convertRowIndexToModel(row)

        if data_col < 5:
            comp.setForeground(ColorConstants.BLACK)
            comp.setBackground(ColorConstants.WHITE)
            
            selected_rows = self._extender.logTable.getSelectedRows()
            if row in selected_rows:
                comp.setBackground(ColorConstants.SELECTED_BG)
                comp.setForeground(ColorConstants.BLACK)
            
            return comp

        value = self._extender.tableModel.getValueAt(model_row, col)

        comp.setForeground(ColorConstants.BLACK)
        comp.setBackground(ColorConstants.WHITE)
        should_mask = False
        
        if data_col == 5:
            should_mask = not self.shouldShowStatus(value)
        elif data_col >= 6:
            if data_col & 1:
                should_mask = not self.shouldShowStatus(value)
            else:
                status_view_col = self._extender.tableModel.getViewColumnIndex(data_col + 1)
                if status_view_col >= 0:
                    status_value = self._extender.tableModel.getValueAt(model_row, status_view_col)
                    should_mask = not self.shouldShowStatus(status_value)

        if should_mask:
            comp.setText("")
            comp.setBackground(ColorConstants.WHITE)
            comp.setForeground(ColorConstants.WHITE)
        else:
            if data_col & 1 or data_col == 5:
                if value == self._extender.BYPASSSED_STR:
                    comp.setBackground(ColorConstants.BYPASSED_BG)
                elif value == self._extender.IS_ENFORCED_STR:
                    comp.setBackground(ColorConstants.IS_ENFORCED_BG)
                elif value == self._extender.ENFORCED_STR:
                    comp.setBackground(ColorConstants.ENFORCED_BG)
                elif value == "Disabled":
                    comp.setBackground(ColorConstants.DISABLED_BG)
                
                comp.setForeground(ColorConstants.BLACK)

        selected_rows = self._extender.logTable.getSelectedRows()
        if row in selected_rows and (not should_mask or data_col < 5):
            comp.setBackground(ColorConstants.SELECTED_BG)
            comp.setForeground(ColorConstants.BLACK)

        return comp

    def shouldShowStatus(self, status):
        if not hasattr(self._extender, 'showBypassed'):
            return True
        
        if (self._extender.showBypassed.isSelected() and
            self._extender.showIsEnforced.isSelected() and
            self._extender.showEnforced.isSelected()):
            return True
        
        if status == "Disabled":
            return True
        elif self._extender.showBypassed.isSelected() and self._extender.BYPASSSED_STR == status:
            return True
        elif self._extender.showIsEnforced.isSelected() and self._extender.IS_ENFORCED_STR == status:
            return True
        elif self._extender.showEnforced.isSelected() and self._extender.ENFORCED_STR == status:
            return True
        
        return False
    
class LogEntry:
    def __init__(self, id, method, url, originalrequestResponse, unauthorizedRequestResponse, enforcementStatusUnauthorized):
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
        if (hasattr(self._extender, 'showBypassed') and
            self._extender.showBypassed.isSelected() and
            self._extender.showIsEnforced.isSelected() and
            self._extender.showEnforced.isSelected()):
            return True
        tableModel = getattr(self._extender, 'tableModel', None)
        if not tableModel:
            return True
        for view_col in range(entry.getValueCount()):
            data_col = tableModel.getDataColumnIndex(view_col)
            if data_col == 5 or (data_col >= 6 and data_col % 2 == 1):
                status = entry.getValue(view_col)
                if self.statusMatchesFilter(status):
                    return True
        return False
    
    def statusMatchesFilter(self, status):
        if not hasattr(self._extender, 'showBypassed'):
            return True
            
        if self._extender.showBypassed.isSelected() and self._extender.BYPASSSED_STR == status:
            return True
        elif self._extender.showIsEnforced.isSelected() and self._extender.IS_ENFORCED_STR == status:
            return True
        elif self._extender.showEnforced.isSelected() and self._extender.ENFORCED_STR == status:
            return True
        elif status == "Disabled":
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