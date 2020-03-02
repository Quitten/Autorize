from java.awt.event import AdjustmentListener
from java.awt.event import ActionListener
from java.awt.event import MouseAdapter
from java.awt.event import ItemListener
from javax.swing import RowFilter
from javax.swing import JCheckBox
from javax.swing import JTable
from javax.swing import JLabel
from javax.swing import JPanel
from java.lang import Runnable
from java.awt import Color

def init_filter(self):
        """
        init show tab
        """

        filterLModified = JLabel("Modified:")
        filterLModified.setBounds(10, 10, 100, 30)

        filterLUnauthenticated = JLabel("Unauthenticated:")
        filterLUnauthenticated.setBounds(250, 10, 100, 30)

        self.showAuthBypassModified = JCheckBox(self.BYPASSSED_STR)
        self.showAuthBypassModified.setBounds(10, 35, 200, 30)
        self.showAuthBypassModified.setSelected(True)
        self.showAuthBypassModified.addItemListener(tabTableFilter(self))

        self.showAuthPotentiallyEnforcedModified = JCheckBox("Is enforced???")
        self.showAuthPotentiallyEnforcedModified.setBounds(10, 60, 200, 30)
        self.showAuthPotentiallyEnforcedModified.setSelected(True)
        self.showAuthPotentiallyEnforcedModified.addItemListener(tabTableFilter(self))

        self.showAuthEnforcedModified = JCheckBox(self.ENFORCED_STR)
        self.showAuthEnforcedModified.setBounds(10, 85, 200, 30)
        self.showAuthEnforcedModified.setSelected(True)
        self.showAuthEnforcedModified.addItemListener(tabTableFilter(self))

        self.showAuthBypassUnauthenticated = JCheckBox(self.BYPASSSED_STR)
        self.showAuthBypassUnauthenticated.setBounds(250, 35, 200, 30)
        self.showAuthBypassUnauthenticated.setSelected(True)
        self.showAuthBypassUnauthenticated.addItemListener(tabTableFilter(self))

        self.showAuthPotentiallyEnforcedUnauthenticated = JCheckBox("Is enforced???")
        self.showAuthPotentiallyEnforcedUnauthenticated.setBounds(250, 60, 200, 30)
        self.showAuthPotentiallyEnforcedUnauthenticated.setSelected(True)
        self.showAuthPotentiallyEnforcedUnauthenticated.addItemListener(tabTableFilter(self))

        self.showAuthEnforcedUnauthenticated = JCheckBox(self.ENFORCED_STR)
        self.showAuthEnforcedUnauthenticated.setBounds(250, 85, 200, 30)
        self.showAuthEnforcedUnauthenticated.setSelected(True)
        self.showAuthEnforcedUnauthenticated.addItemListener(tabTableFilter(self))

        self.showDisabledUnauthenticated = JCheckBox("Disabled")
        self.showDisabledUnauthenticated.setBounds(250, 110, 200, 30)
        self.showDisabledUnauthenticated.setSelected(True)
        self.showDisabledUnauthenticated.addItemListener(tabTableFilter(self))        

        self.filterPnl = JPanel()
        self.filterPnl.setLayout(None)
        self.filterPnl.setBounds(0, 0, 1000, 1000)

        self.filterPnl.add(filterLModified)
        self.filterPnl.add(filterLUnauthenticated)
        self.filterPnl.add(self.showAuthBypassModified)
        self.filterPnl.add(self.showAuthPotentiallyEnforcedModified)
        self.filterPnl.add(self.showAuthEnforcedModified)
        self.filterPnl.add(self.showAuthBypassUnauthenticated)
        self.filterPnl.add(self.showAuthPotentiallyEnforcedUnauthenticated)
        self.filterPnl.add(self.showAuthEnforcedUnauthenticated)                
        self.filterPnl.add(self.showDisabledUnauthenticated)

class tabTableFilter(ItemListener):
    def __init__(self, extender):
        self._extender = extender

    def itemStateChanged(self, e):
        self._extender.tableSorter.sort()

class Table(JTable):

    def __init__(self, extender):
        self._extender = extender
        self.setModel(extender)
        self.addMouseListener(mouseclick(self._extender))
        self.getColumnModel().getColumn(0).setPreferredWidth(450)
        self.setRowSelectionAllowed(True)
        return

    def prepareRenderer(self, renderer, row, col):
        comp = JTable.prepareRenderer(self, renderer, row, col)
        value = self._extender.getValueAt(self._extender.logTable.convertRowIndexToModel(row), col)

        if col == 6 or col == 7:
            if value == self._extender.BYPASSSED_STR:
                comp.setBackground(Color(179, 0, 0))
                comp.setForeground(Color.BLACK)
            elif value == self._extender.IS_ENFORCED_STR:
                comp.setBackground(Color(255, 153, 51))
                comp.setForeground(Color.BLACK)
            elif value == self._extender.ENFORCED_STR:
                comp.setBackground(Color(0, 153, 51))
                comp.setForeground(Color.BLACK)
        else:
            comp.setForeground(Color.BLACK)
            comp.setBackground(Color.LIGHT_GRAY)

        selectedRow = self._extender.logTable.getSelectedRow()
        if selectedRow == row:
          comp.setBackground(Color.WHITE)
          comp.setForeground(Color.BLACK)

        return comp
    
    def changeSelection(self, row, col, toggle, extend):
        # show the log entry for the selected row
        logEntry = self._extender._log.get(self._extender.logTable.convertRowIndexToModel(row))
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
            self._extender.tabs.setSelectedIndex(3)
        elif col == 4 or col == 6:
            self._extender.tabs.setSelectedIndex(1)
        elif col == 5 or col == 7:
            self._extender.tabs.setSelectedIndex(5)
        else:
            self._extender.tabs.setSelectedIndex(2)

        JTable.changeSelection(self, row, col, toggle, extend)
        return

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
        return

class mouseclick(MouseAdapter):

    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        if evt.button == 3:
            self._extender.menu.show(evt.getComponent(), evt.getX(), evt.getY())


class sendRequestRepeater(ActionListener):
    def __init__(self, extender, callbacks, original):
        self._extender = extender
        self._callbacks = callbacks
        self.original = original

    def actionPerformed(self, e):
        if self.original:
                request = self._extender._currentlyDisplayedItem._originalrequestResponse
        else:
                request = self._extender._currentlyDisplayedItem._requestResponse
        host = request.getHttpService().getHost()
        port = request.getHttpService().getPort()
        
        self._callbacks.sendToRepeater(host, port, 1, request.getRequest(), "Autorize");


class tableFilter(RowFilter):

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

class autoScrollListener(AdjustmentListener):
    def __init__(self, extender):
        self._extender = extender

    def adjustmentValueChanged(self, e):
        if self._extender.autoScroll.isSelected() is True:
            e.getAdjustable().setValue(e.getAdjustable().getMaximum())

class copySelectedURL(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        stringSelection = StringSelection(str(self._extender._helpers.analyzeRequest(self._extender._currentlyDisplayedItem._requestResponse).getUrl()))
        clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard()
        clpbrd.setContents(stringSelection, None)

class retestSelectedRequest(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
    	print self._extender.logTable.getSelectedRows()
        start_new_thread(self._extender.checkAuthorization, (self._extender._currentlyDisplayedItem._originalrequestResponse, self._extender._helpers.analyzeResponse(self._extender._currentlyDisplayedItem._originalrequestResponse.getResponse()).getHeaders(), self._extender.doUnauthorizedRequest.isSelected()))

class deleteSelectedRequest(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e): # bug after first delete!
        pass
        # logBackup = self._extender._log[:]
        # self._extender.clearList(self)
        # self._extender._lock.acquire()
        # print self._extender._currentlyDisplayedItem
        # logBackup.remove(self._extender._currentlyDisplayedItem)
        # self._extender._log = logBackup
        # row = self._extender._log.size()
        # start_new_thread(self._extender.UpdateTableEDT, (self._extender,"insert",row,row))
        # SwingUtilities.invokeLater(UpdateTableEDT(self,"delete",0, oldSize - 1))
        # self._extender._lock.release()

class sendResponseComparer(ActionListener):
    def __init__(self, extender, callbacks):
        self._extender = extender
        self._callbacks = callbacks

    def actionPerformed(self, e):
        originalResponse = self._extender._currentlyDisplayedItem._originalrequestResponse
        modifiedResponse = self._extender._currentlyDisplayedItem._requestResponse
        unauthorizedResponse = self._extender._currentlyDisplayedItem._unauthorizedRequestResponse
        
        self._callbacks.sendToComparer(originalResponse.getResponse());
        self._callbacks.sendToComparer(modifiedResponse.getResponse());
        self._callbacks.sendToComparer(unauthorizedResponse.getResponse());


class UpdateTableEDT(Runnable):
    def __init__(self,extender,action,firstRow,lastRow):
        self._extender=extender
        self._action=action
        self._firstRow=firstRow
        self._lastRow=lastRow

    def run(self):
        if self._action == "insert":
            self._extender.fireTableRowsInserted(self._firstRow, self._lastRow)
        elif self._action == "update":
            self._extender.fireTableRowsUpdated(self._firstRow, self._lastRow)
        elif self._action == "delete":
            self._extender.fireTableRowsDeleted(self._firstRow, self._lastRow)
        else:
            print("Invalid action in UpdateTableEDT")

def clearList(self, event):
    self._lock.acquire()
    oldSize = self._log.size()
    self._log.clear()
    SwingUtilities.invokeLater(UpdateTableEDT(self,"delete",0, oldSize - 1))
    #self.fireTableRowsDeleted(0, oldSize - 1)
    self._lock.release()