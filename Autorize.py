from burp import ITab
from burp import IBurpExtender
from burp import IHttpListener
from burp import IContextMenuFactory
from burp import IMessageEditorController
from javax.swing import JList
from javax.swing import JTable
from javax.swing import JFrame
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing import JButton
from javax.swing import JComboBox
from javax.swing import JCheckBox
from javax.swing import JMenuItem
from javax.swing import JTextArea
from javax.swing import JPopupMenu
from javax.swing import JSplitPane
from javax.swing import JScrollPane
from javax.swing import JTabbedPane
from javax.swing import JFileChooser
from javax.swing import DefaultListModel
from javax.swing import JCheckBoxMenuItem
from threading import Lock
from java.io import File
from java.net import URL
from java.awt import Color
from java.awt import Toolkit
from java.awt.event import ItemListener
from java.awt.event import MouseAdapter
from java.awt.event import ActionListener
from java.awt.event import AdjustmentListener
from java.awt.datatransfer import Clipboard
from java.awt.datatransfer import StringSelection
from javax.swing.border import LineBorder
from javax.swing.table import AbstractTableModel
from java.util import LinkedList
from java.util import ArrayList
#from java.lang import Integer
import re
#import array

'''
ToDo
- Add one "Enforcement detector" tab for unauthorized responses
- Add one column with the "Authroization enforcement status" for the unauthorized response
- Add one ID column with an incremental ID
- Add autosorting to the columns of the table
'''

class BurpExtender(IBurpExtender, ITab, IHttpListener, IMessageEditorController, AbstractTableModel, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        # keep a reference to our callbacks object
        self._callbacks = callbacks
        # obtain an extension helpers object
        self._helpers = callbacks.getHelpers()
        
        # set our extension name
        callbacks.setExtensionName("Autorize")
        
        # create the log and a lock on which to synchronize when adding log entries
        self._log = ArrayList()
        self._lock = Lock()
        self._enfocementStatuses = ["Authorization bypass!","Authorization enforced??? (please configure enforcement detector)","Authorization enforced!"]
        self.intercept = 0

        self.initInterceptionFilters()

        self.initEnforcementDetector()

        self.initExport()

        self.initConfigurationTab()

        self.initTabs()
        
        self.initCallbacks()
        
        print "Thank you for installing Autorize v0.9 extension"
        print "by Barak Tawily"
        return
        

    def initExport(self):
        #
        ## init enforcement detector tab
        #

        exportLType = JLabel("File Type:")
        exportLType.setBounds(10, 10, 100, 30)
       
        exportLES = JLabel("Enforcement Statuses:")
        exportLES.setBounds(10, 50, 160, 30)

        exportFileTypes = ["HTML"]
        self.exportType = JComboBox(exportFileTypes)
        self.exportType.setBounds(100, 10, 200, 30)

        exportES = ["All Statuses", self._enfocementStatuses[0], self._enfocementStatuses[1], self._enfocementStatuses[2]]
        self.exportES = JComboBox(exportES)
        self.exportES.setBounds(100, 50, 200, 30)

        exportLES = JLabel("Statuses:")
        exportLES.setBounds(10, 50, 100, 30)

        self.exportButton = JButton("Export",actionPerformed=self.exportToHTML)
        self.exportButton.setBounds(390, 25, 100, 30)

        self.exportPnl = JPanel()
        self.exportPnl.setLayout(None);
        self.exportPnl.setBounds(0, 0, 1000, 1000);
        self.exportPnl.add(exportLType)
        self.exportPnl.add(self.exportType)
        self.exportPnl.add(exportLES)
        self.exportPnl.add(self.exportES)
        self.exportPnl.add(self.exportButton)

    def initEnforcementDetector(self):
        #
        ## init enforcement detector tab
        #

        self.EDFP = ArrayList()
        self.EDCT = ArrayList()

        EDLType = JLabel("Type:")
        EDLType.setBounds(10, 10, 140, 30)

        EDLContent = JLabel("Content:")
        EDLContent.setBounds(10, 50, 140, 30)

        EDLabelList = JLabel("Filter List:")
        EDLabelList.setBounds(10, 165, 140, 30)

        #EDStrings = ["Finger Print: (enforced message body contains)", "Content-Length: (constant Content-Length number of enforced response)", "Headers: (enforced message headers contains)", "Regex: (headers + body)"]
        EDStrings = ["Headers (simple string): (enforced message headers contains)", "Headers (regex): (enforced messege headers contains)", "Body (simple string): (enforced messege body contains)", "Body (regex): (enforced messege body contains)", "Full request (simple string): (enforced messege contains)", "Full request (regex): (enforced messege contains)", "Content-Length: (constant Content-Length number of enforced response)"]
        self.EDType = JComboBox(EDStrings)
        self.EDType.setBounds(80, 10, 430, 30)
       
        self.EDText = JTextArea("", 5, 30)
        self.EDText.setBounds(80, 50, 300, 110)

        self.EDModel = DefaultListModel();
        self.EDList = JList(self.EDModel);
        self.EDList.setBounds(80, 175, 300, 110)
        self.EDList.setBorder(LineBorder(Color.BLACK))

        self.EDAdd = JButton("Add filter",actionPerformed=self.addEDFilter)
        self.EDAdd.setBounds(390, 85, 120, 30)
        self.EDDel = JButton("Remove filter",actionPerformed=self.delEDFilter)
        self.EDDel.setBounds(390, 210, 120, 30)

        self.EDPnl = JPanel()
        self.EDPnl.setLayout(None);
        self.EDPnl.setBounds(0, 0, 1000, 1000);
        self.EDPnl.add(EDLType)
        self.EDPnl.add(self.EDType)
        self.EDPnl.add(EDLContent)
        self.EDPnl.add(self.EDText)
        self.EDPnl.add(self.EDAdd)
        self.EDPnl.add(self.EDDel)
        self.EDPnl.add(EDLabelList)
        self.EDPnl.add(self.EDList)

    def initInterceptionFilters(self):
        #
        ##  init interception filters tab
        #

        IFStrings = ["Scope items only: (Content is not required)","URL Contains (simple string): ","URL Contains (regex): ","URL Not Contains (simple string): ","URL Not Contains (regex): "]
        self.IFType = JComboBox(IFStrings)
        self.IFType.setBounds(80, 10, 430, 30)
       
        self.IFModel = DefaultListModel();
        self.IFList = JList(self.IFModel);
        self.IFList.setBounds(80, 175, 300, 110)
        self.IFList.setBorder(LineBorder(Color.BLACK))

        self.IFText = JTextArea("", 5, 30)
        self.IFText.setBounds(80, 50, 300, 110)

        IFLType = JLabel("Type:")
        IFLType.setBounds(10, 10, 140, 30)

        IFLContent = JLabel("Content:")
        IFLContent.setBounds(10, 50, 140, 30)

        IFLabelList = JLabel("Filter List:")
        IFLabelList.setBounds(10, 165, 140, 30)

        self.IFAdd = JButton("Add filter",actionPerformed=self.addIFFilter)
        self.IFAdd.setBounds(390, 85, 120, 30)
        self.IFDel = JButton("Remove filter",actionPerformed=self.delIFFilter)
        self.IFDel.setBounds(390, 210, 120, 30)

        self.filtersPnl = JPanel()
        self.filtersPnl.setLayout(None);
        self.filtersPnl.setBounds(0, 0, 1000, 1000);
        self.filtersPnl.add(IFLType)
        self.filtersPnl.add(self.IFType)
        self.filtersPnl.add(IFLContent)
        self.filtersPnl.add(self.IFText)
        self.filtersPnl.add(self.IFAdd)
        self.filtersPnl.add(self.IFDel)
        self.filtersPnl.add(IFLabelList)
        self.filtersPnl.add(self.IFList)


    def initConfigurationTab(self):
        #
        ##  init configuration tab
        #
        self.prevent304 = JCheckBox("Prevent 304 Not Modified status code")
        self.prevent304.setBounds(290, 25, 300, 30)

        self.ignore304 = JCheckBox("Ignore 304/204 status code responses")
        self.ignore304.setBounds(290, 5, 300, 30)
        self.ignore304.setSelected(True)

        self.autoScroll = JCheckBox("Auto Scroll")
        #self.autoScroll.setBounds(290, 45, 140, 30)
        self.autoScroll.setBounds(160, 40, 140, 30)

        self.doUnauthorizedRequest = JCheckBox("Check unauthorized")
        self.doUnauthorizedRequest.setBounds(290, 45, 300, 30)
        self.doUnauthorizedRequest.setSelected(True)

        startLabel = JLabel("Authorization checks:")
        startLabel.setBounds(10, 10, 140, 30)
        self.startButton = JButton("Autorize is off",actionPerformed=self.startOrStop)
        self.startButton.setBounds(160, 10, 120, 30)
        self.startButton.setBackground(Color(255, 100, 91, 255))

        self.clearButton = JButton("Clear List",actionPerformed=self.clearList)
        self.clearButton.setBounds(10, 40, 100, 30)

        self.replaceString = JTextArea("Cookie: Insert=injected; header=here;", 5, 30)
        self.replaceString.setWrapStyleWord(True);
        self.replaceString.setLineWrap(True)
        self.replaceString.setBounds(10, 80, 470, 180)

        self.filtersTabs = JTabbedPane()
        self.filtersTabs.addTab("Enforcement Detector", self.EDPnl)
        self.filtersTabs.addTab("Interception Filters", self.filtersPnl)
        self.filtersTabs.addTab("Export", self.exportPnl)

        self.filtersTabs.setBounds(0, 280, 2000, 700)

        self.pnl = JPanel()
        self.pnl.setBounds(0, 0, 1000, 1000);
        self.pnl.setLayout(None);
        self.pnl.add(self.startButton)
        self.pnl.add(self.clearButton)
        self.pnl.add(self.replaceString)
        self.pnl.add(startLabel)
        self.pnl.add(self.autoScroll)
        self.pnl.add(self.ignore304)
        self.pnl.add(self.prevent304)
        self.pnl.add(self.doUnauthorizedRequest)
        self.pnl.add(self.filtersTabs)

    def initTabs(self):
        #
        ##  init autorize tabs
        #
        
        self.logTable = Table(self)
        self._splitpane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT)
        self._splitpane.setResizeWeight(1)
        self.scrollPane = JScrollPane(self.logTable)
        self._splitpane.setLeftComponent(self.scrollPane)
        self.scrollPane.getVerticalScrollBar().addAdjustmentListener(autoScrollListener(self))
        self.menuES0 = JCheckBoxMenuItem(self._enfocementStatuses[0],True)
        self.menuES1 = JCheckBoxMenuItem(self._enfocementStatuses[1],True)
        self.menuES2 = JCheckBoxMenuItem(self._enfocementStatuses[2],True)
        self.menuES0.addItemListener(menuTableFilter(self))
        self.menuES1.addItemListener(menuTableFilter(self))
        self.menuES2.addItemListener(menuTableFilter(self))

        copyURLitem = JMenuItem("Copy URL");
        copyURLitem.addActionListener(copySelectedURL(self))
        self.menu = JPopupMenu("Popup")
        self.menu.add(copyURLitem)
        self.menu.add(self.menuES0)
        self.menu.add(self.menuES1)
        self.menu.add(self.menuES2)

        self.tabs = JTabbedPane()
        self._requestViewer = self._callbacks.createMessageEditor(self, False)
        self._responseViewer = self._callbacks.createMessageEditor(self, False)

        self._originalrequestViewer = self._callbacks.createMessageEditor(self, False)
        self._originalresponseViewer = self._callbacks.createMessageEditor(self, False)

        self._unauthorizedrequestViewer = self._callbacks.createMessageEditor(self, False)
        self._unauthorizedresponseViewer = self._callbacks.createMessageEditor(self, False)        

        self.tabs.addTab("Modified Request", self._requestViewer.getComponent())
        self.tabs.addTab("Modified Response", self._responseViewer.getComponent())

        self.tabs.addTab("Original Request", self._originalrequestViewer.getComponent())
        self.tabs.addTab("Original Response", self._originalresponseViewer.getComponent())

        self.tabs.addTab("Unauthorized Request", self._unauthorizedrequestViewer.getComponent())
        self.tabs.addTab("Unauthorized Response", self._unauthorizedresponseViewer.getComponent())        

        self.tabs.addTab("Configuration", self.pnl)
        self.tabs.setSelectedIndex(6)
        self._splitpane.setRightComponent(self.tabs)

    def initCallbacks(self):
        #
        ##  init callbacks
        #

        # customize our UI components
        self._callbacks.customizeUiComponent(self._splitpane)
        self._callbacks.customizeUiComponent(self.logTable)
        self._callbacks.customizeUiComponent(self.scrollPane)
        self._callbacks.customizeUiComponent(self.tabs)
        self._callbacks.customizeUiComponent(self.filtersTabs)
        self._callbacks.registerContextMenuFactory(self)
        # add the custom tab to Burp's UI
        self._callbacks.addSuiteTab(self)


    #
    ## Events functions
    #
    def startOrStop(self, event):
        if self.startButton.getText() == "Autorize is off":
            self.startButton.setText("Autorize is on")
            self.startButton.setBackground(Color.GREEN)
            self.intercept = 1
            self._callbacks.registerHttpListener(self)
        else:
            self.startButton.setText("Autorize is off")
            self.startButton.setBackground(Color(255, 100, 91, 255))
            self.intercept = 0
            self._callbacks.removeHttpListener(self)

    def addEDFilter(self, event):
        typeName = self.EDType.getSelectedItem().split(":")[0]
        self.EDModel.addElement(typeName + ": " + self.EDText.getText())

    def delEDFilter(self, event):
        index = self.EDList.getSelectedIndex();
        if not index == -1:
            self.EDModel.remove(index);

    def addIFFilter(self, event):
        typeName = self.IFType.getSelectedItem().split(":")[0]
        self.IFModel.addElement(typeName + ": " + self.IFText.getText())

    def delIFFilter(self, event):
        index = self.IFList.getSelectedIndex();
        if not index == -1:
            self.IFModel.remove(index);

    def clearList(self, event):
        self._lock.acquire()
        self._log = ArrayList()
        row = self._log.size()
        self.fireTableRowsInserted(row, row)
        self._lock.release()

    def exportToHTML(self, event):
        parentFrame = JFrame()
        fileChooser = JFileChooser()
        fileChooser.setSelectedFile(File("AutorizeReprort.html"));
        fileChooser.setDialogTitle("Save Autorize Report")
        userSelection = fileChooser.showSaveDialog(parentFrame)
        if userSelection == JFileChooser.APPROVE_OPTION:
            fileToSave = fileChooser.getSelectedFile()

        enforcementStatusFilter = self.exportES.getSelectedItem()
        htmlContent = """<html><title>Autorize Report by Barak Tawily</title>
        <style>
        .datagrid table { border-collapse: collapse; text-align: left; width: 100%; }
         .datagrid {font: normal 12px/150% Arial, Helvetica, sans-serif; background: #fff; overflow: hidden; border: 1px solid #006699; -webkit-border-radius: 3px; -moz-border-radius: 3px; border-radius: 3px; }
         .datagrid table td, .datagrid table th { padding: 3px 10px; }
         .datagrid table thead th {background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #006699), color-stop(1, #00557F) );background:-moz-linear-gradient( center top, #006699 5%, #00557F 100% );filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699', endColorstr='#00557F');background-color:#006699; color:#FFFFFF; font-size: 15px; font-weight: bold; border-left: 1px solid #0070A8; } .datagrid table thead th:first-child { border: none; }.datagrid table tbody td { color: #00496B; border-left: 1px solid #E1EEF4;font-size: 12px;font-weight: normal; }.datagrid table tbody .alt td { background: #E1EEF4; color: #00496B; }.datagrid table tbody td:first-child { border-left: none; }.datagrid table tbody tr:last-child td { border-bottom: none; }.datagrid table tfoot td div { border-top: 1px solid #006699;background: #E1EEF4;} .datagrid table tfoot td { padding: 0; font-size: 12px } .datagrid table tfoot td div{ padding: 2px; }.datagrid table tfoot td ul { margin: 0; padding:0; list-style: none; text-align: right; }.datagrid table tfoot  li { display: inline; }.datagrid table tfoot li a { text-decoration: none; display: inline-block;  padding: 2px 8px; margin: 1px;color: #FFFFFF;border: 1px solid #006699;-webkit-border-radius: 3px; -moz-border-radius: 3px; border-radius: 3px; background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #006699), color-stop(1, #00557F) );background:-moz-linear-gradient( center top, #006699 5%, #00557F 100% );filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#006699', endColorstr='#00557F');background-color:#006699; }.datagrid table tfoot ul.active, .datagrid table tfoot ul a:hover { text-decoration: none;border-color: #006699; color: #FFFFFF; background: none; background-color:#00557F;}div.dhtmlx_window_active, div.dhx_modal_cover_dv { position: fixed !important; }
        table {
        width: 100%;
        table-layout: fixed;
        }
        td {
            border: 1px solid #35f;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        td.a {
            width: 13%;
            white-space: nowrap;
        }
        td.b {
            width: 9%;
            word-wrap: break-word;
        }
        </style>
        <body>
        <h1>Autorize Report<h1>
        <div class="datagrid"><table>
        <thead><tr><th>URL</th><th>Authorization Enforcement Status</th></tr></thead>
        <tbody>"""

        for i in range(0,self._log.size()):
            color = ""
            if self._log.get(i)._enfocementStatus == self._enfocementStatuses[0]:
                color = "red"
            if self._log.get(i)._enfocementStatus == self._enfocementStatuses[1]:
                color = "yellow"
            if self._log.get(i)._enfocementStatus == self._enfocementStatuses[2]:
                color = "LawnGreen"

            if enforcementStatusFilter == "All Statuses":
                htmlContent += "<tr bgcolor=\"%s\"><td><a href=\"%s\">%s</a></td><td>%s</td></tr>" % (color,self._log.get(i)._url,self._log.get(i)._url, self._log.get(i)._enfocementStatus)
            else:
                if enforcementStatusFilter == self._log.get(i)._enfocementStatus:
                    htmlContent += "<tr bgcolor=\"%s\"><td><a href=\"%s\">%s</a></td><td>%s</td></tr>" % (color,self._log.get(i)._url,self._log.get(i)._url, self._log.get(i)._enfocementStatus)

        htmlContent += "</tbody></table></div></body></html>"
        f = open(fileToSave.getAbsolutePath(), 'w')
        f.writelines(htmlContent)
        f.close()




    #
    # implement IContextMenuFactory
    #
    def createMenuItems(self, invocation):
        responses = invocation.getSelectedMessages();
        if responses > 0:
            ret = LinkedList()
            requestMenuItem = JMenuItem("Send request to Autorize");
            cookieMenuItem = JMenuItem("Send cookie to Autorize");
            requestMenuItem.addActionListener(handleMenuItems(self,responses[0], "request"))
            cookieMenuItem.addActionListener(handleMenuItems(self, responses[0], "cookie"))   
            ret.add(requestMenuItem);
            ret.add(cookieMenuItem);
            return(ret);
        return null;


    #
    # implement ITab
    #
    def getTabCaption(self):
        return "Autorize"
    
    def getUiComponent(self):
        return self._splitpane
        
        #
    # extend AbstractTableModel
    #
    
    def getRowCount(self):
        try:
            return self._log.size()
        except:
            return 0

    def getColumnCount(self):
        return 5

    def getColumnName(self, columnIndex):
        if columnIndex == 0:
            return "URL"
        if columnIndex == 1:
            return "Orig. Length"            
        if columnIndex == 2:
            return "Modif. Length" 
        if columnIndex == 3:
            return "Unauth. Length"           
        if columnIndex == 4:
            return "Authorization Enforcement Status"
        return ""

    def getValueAt(self, rowIndex, columnIndex):
        logEntry = self._log.get(rowIndex)
        if columnIndex == 0:
            return logEntry._url.toString()
        if columnIndex == 1:
            return str(len(logEntry._originalrequestResponse.getResponse()))
        if columnIndex == 2:
            return str(len(logEntry._requestResponse.getResponse()))
        if columnIndex == 3:
            if logEntry._unauthorizedRequestResponse != None:
                return str(len(logEntry._unauthorizedRequestResponse.getResponse()))
            else:
                return "-"
        if columnIndex == 4:
            return logEntry._enfocementStatus            
        return ""

    #
    # implement IMessageEditorController
    # this allows our request/response viewers to obtain details about the messages being displayed
    #
    
    def getHttpService(self):
        return self._currentlyDisplayedItem.getHttpService()

    def getRequest(self):
        return self._currentlyDisplayedItem.getRequest()

    def getResponse(self):
        return self._currentlyDisplayedItem.getResponse()


    #
    # implement IHttpListener
    #
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):

        #print "PROCESS HTTP MESSAGE"

        if (self.intercept == 1) and (toolFlag != self._callbacks.TOOL_EXTENDER):
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
                if not self.replaceString.getText() in self._helpers.analyzeRequest(messageInfo).getHeaders():
                    if self.ignore304.isSelected():
                        firstHeader = self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders()[0]
                        if "304" in firstHeader or "204" in firstHeader:
                           return
                    if self.IFList.getModel().getSize() == 0:
                        self.checkAuthorization(messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())
                    else:
                        urlString = str(self._helpers.analyzeRequest(messageInfo).getUrl())
                        
                        do_the_check = 1

                        for i in range(0,self.IFList.getModel().getSize()):

                            # IFStrings = ["Scope items only: (Content is not required)","URL Contains (simple string): ","URL Contains (regex): ","URL Not Contains (simple string): ","URL Not Contains (regex): "]
                            if self.IFList.getModel().getElementAt(i).split(":")[0] == "Scope items only":
                                currentURL = URL(urlString)
                                if not self._callbacks.isInScope(currentURL):
                                    do_the_check = do_the_check and 0
                                    #self.checkAuthorization(messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())
                            if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Contains (simple string)":
                                if self.IFList.getModel().getElementAt(i)[30:] not in urlString:
                                    do_the_check = do_the_check and 0
                                    #self.checkAuthorization(messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())
                            if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Contains (regex)":
                                regex_string = self.IFList.getModel().getElementAt(i)[22:]
                                p = re.compile(regex_string, re.IGNORECASE)
                                if not p.search(urlString):
                                    do_the_check = do_the_check and 0
                                    #self.checkAuthorization(messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())  
                            if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Not Contains (simple string)":
                                if self.IFList.getModel().getElementAt(i)[34:] in urlString:
                                    do_the_check = do_the_check and 0
                                    #self.checkAuthorization(messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())
                            if self.IFList.getModel().getElementAt(i).split(":")[0] == "URL Not Contains (regex)":
                                regex_string = self.IFList.getModel().getElementAt(i)[26:]
                                p = re.compile(regex_string, re.IGNORECASE)
                                if p.search(urlString):
                                    do_the_check = do_the_check and 0
                                    #self.checkAuthorization(messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders())                                                                        

                        if do_the_check:
                            print "TEST"
                            print self.doUnauthorizedRequest.isSelected()
                            self.checkAuthorization(messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),self.doUnauthorizedRequest.isSelected())

                        # Unauthorized check
                        #if self.doUnauthorizedRequest.isSelected():
                        #    self.checkAuthorization(messageInfo,self._helpers.analyzeResponse(messageInfo.getResponse()).getHeaders(),False)


        return


    def makeRequest(self, messageInfo, message):
        requestURL = self._helpers.analyzeRequest(messageInfo).getUrl()
        return self._callbacks.makeHttpRequest(self._helpers.buildHttpService(str(requestURL.getHost()), int(requestURL.getPort()), requestURL.getProtocol() == "https"), message)

    def makeMessage(self, messageInfo, removeOrNot, authorizeOrNot):
        requestInfo = self._helpers.analyzeRequest(messageInfo)
        headers = requestInfo.getHeaders()
        if removeOrNot:
            headers = list(headers)
            removeHeaders = ArrayList()
            removeHeaders.add(self.replaceString.getText()[0:self.replaceString.getText().index(":")])

            for header in headers[:]:
                for removeHeader in removeHeaders:
                    if removeHeader in header:
                        headers.remove(header)

            if authorizeOrNot:
                #print self.replaceString.getText()
                headers.append(self.replaceString.getText())

        msgBody = messageInfo.getRequest()[requestInfo.getBodyOffset():]
        return self._helpers.buildHttpMessage(headers, msgBody)

    def checkAuthorization(self, messageInfo, originalHeaders, checkUnauthorized):
        message = self.makeMessage(messageInfo,True,True)
        requestResponse = self.makeRequest(messageInfo, message)
        analyzedResponse = self._helpers.analyzeResponse(requestResponse.getResponse())
        
        oldStatusCode = originalHeaders[0]
        newStatusCode = analyzedResponse.getHeaders()[0]
        oldContentLen = self.getContentLength(originalHeaders)
        newContentLen = self.getContentLength(analyzedResponse.getHeaders())

        # Check unauthorized request
        if checkUnauthorized:
            messageUnauthorized = self.makeMessage(messageInfo,True,False)
            requestResponseUnauthorized = self.makeRequest(messageInfo, messageUnauthorized)
            analyzedResponseUnauthorized = self._helpers.analyzeResponse(requestResponseUnauthorized.getResponse())  
            statusCodeUnauthorized = analyzedResponseUnauthorized.getHeaders()[0]
            contentLenUnauthorized = self.getContentLength(analyzedResponseUnauthorized.getHeaders())

        impression = ""

        EDFilters = self.EDModel.toArray()
        if oldStatusCode == newStatusCode:
            if oldContentLen == newContentLen:
                impression = self._enfocementStatuses[0]
            else:

                auth_enforced = 1
                
                for filter in EDFilters:

                    if str(filter).startswith("Headers (simple string): "):

                        if not(filter[25:] in self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])):
                            auth_enforced = 0

                    if str(filter).startswith("Headers (regex): "):
                        regex_string = filter[17:]
                        p = re.compile(regex_string, re.IGNORECASE)
                        if not p.search(self._helpers.bytesToString(requestResponse.getResponse()[0:analyzedResponse.getBodyOffset()])):
                            auth_enforced = 0

                    if str(filter).startswith("Body (simple string): "):
                        if filter[22:] not in self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():]):
                            auth_enforced = 0

                    if str(filter).startswith("Body (regex): "):
                        regex_string = filter[14:]
                        p = re.compile(regex_string, re.IGNORECASE)
                        if not p.search(self._helpers.bytesToString(requestResponse.getResponse()[analyzedResponse.getBodyOffset():])):
                            auth_enforced = 0

                    if str(filter).startswith("Full request (simple string): "):
                        if filter[30:] not in self._helpers.bytesToString(requestResponse.getResponse()):
                            auth_enforced = 0

                    if str(filter).startswith("Full request (regex): "):
                        regex_string = filter[22:]
                        p = re.compile(regex_string, re.IGNORECASE)
                        if not p.search(self._helpers.bytesToString(requestResponse.getResponse())):
                            auth_enforced = 0

                    if str(filter).startswith("Content-Length: "):
                        if newContentLen != filter:
                            auth_enforced = 0


                
                if auth_enforced:
                    impression = self._enfocementStatuses[2]
                else:
                    impression = self._enfocementStatuses[1]
                         
        else:
            impression = self._enfocementStatuses[2]

        self._lock.acquire()
        row = self._log.size()
        
        if checkUnauthorized:
            self._log.add(LogEntry(self._callbacks.saveBuffersToTempFiles(requestResponse), self._helpers.analyzeRequest(requestResponse).getUrl(),messageInfo,impression,self._callbacks.saveBuffersToTempFiles(requestResponseUnauthorized))) # same requests not include again.
        else:
            self._log.add(LogEntry(self._callbacks.saveBuffersToTempFiles(requestResponse), self._helpers.analyzeRequest(requestResponse).getUrl(),messageInfo,impression,None)) # same requests not include again.
        
        #self._log.add(LogEntry(self._callbacks.saveBuffersToTempFiles(requestResponse), self._helpers.analyzeRequest(requestResponse).getUrl(),messageInfo,impression)) # same requests not include again.
        self.fireTableRowsInserted(row, row)
        self._lock.release()

    def getContentLength(self, analyzedResponseHeaders):
        for header in analyzedResponseHeaders:
            if "Content-Length:" in header:
                return header;
        return "null"

    def getCookieFromMessage(self, messageInfo):
        headers = list(self._helpers.analyzeRequest(messageInfo.getRequest()).getHeaders())
        for header in headers:
            if "Cookie:" in header:
                return header
        return None

#
# extend JTable to handle cell selection
#
    
class Table(JTable):

    def __init__(self, extender):
        self._extender = extender
        self.setModel(extender)
        self.addMouseListener(mouseclick(self._extender))
        self.getColumnModel().getColumn(0).setPreferredWidth(450)
        return

    def prepareRenderer(self, renderer, row, col):
        comp = JTable.prepareRenderer(self,renderer, row, col)
        #value = self._extender.getValueAt(row,3)
        value = self._extender.getValueAt(row,col)
        #if (getSelectedRow() == row) {
        if (value == "Authorization bypass!" and col == 4):
            comp.setBackground(Color(255,135,31))
        elif (value == "Authorization enforced??? (please configure enforcement detector)" and col == 4):
            comp.setBackground(Color(255,255,133));
        elif (value == "Authorization enforced!" and col == 4):
            comp.setBackground(Color(192,250,20));
        else:
            comp.setBackground(Color.white);

        return comp
    

    '''
    def prepareRenderer(self, renderer, row, column):
        c = JTable.prepareRenderer(self,renderer, row, column)
        impressionColor = {"Authorization bypass!":Color(255,135,31),
                            "Authorization enforced??? (please configure enforcement detector)":Color(255,255,133),
                            "Authorization enforced!":Color(192,250,20)}
        for impression in impressionColor:
            #modelColumn = self.convertColumnIndexToModel(column)
            if self._extender.getValueAt(row,3) == impression:

                #modelColumn = self.convertColumnIndexToModel(column)
                #modelRow = self.convertRowIndexToModel(row)
                #if modelColumn == 3:
                #if (self.getSelectedRow() == row) and (column == 3):
                #cellRenederer = self.getCellRenderer(row,3)
                #cellRenederer.setBackground(impressionColor[impression])
                c.setBackground(impressionColor[impression])
        
        return c
    '''
    def changeSelection(self, row, col, toggle, extend):
        # show the log entry for the selected row
        logEntry = self._extender._log.get(row)
        self._extender._requestViewer.setMessage(logEntry._requestResponse.getRequest(), True)
        self._extender._responseViewer.setMessage(logEntry._requestResponse.getResponse(), False)
        self._extender._originalrequestViewer.setMessage(logEntry._originalrequestResponse.getRequest(), True)
        self._extender._originalresponseViewer.setMessage(logEntry._originalrequestResponse.getResponse(), False)

        if logEntry._unauthorizedRequestResponse != None:
            self._extender._unauthorizedrequestViewer.setMessage(logEntry._unauthorizedRequestResponse.getRequest(), True)
            self._extender._unauthorizedresponseViewer.setMessage(logEntry._unauthorizedRequestResponse.getResponse(), False)
        else:
            self._extender._unauthorizedrequestViewer.setMessage("Request disabled", True)
            self._extender._unauthorizedresponseViewer.setMessage("Response disabled", False)

        self._extender._currentlyDisplayedItem = logEntry._requestResponse
        JTable.changeSelection(self, row, col, toggle, extend)
        return

'''
class LogEntry:

    def __init__(self, requestResponse, url, originalrequestResponse, enforcementStatus):
        self._requestResponse = requestResponse
        self._originalrequestResponse = originalrequestResponse
        self._url = url
        self._enfocementStatus =  enforcementStatus
        return
'''

class LogEntry:

    def __init__(self, requestResponse, url, originalrequestResponse, enforcementStatus, unauthorizedRequestResponse):
        self._requestResponse = requestResponse
        self._originalrequestResponse = originalrequestResponse
        self._url = url
        self._enfocementStatus =  enforcementStatus
        self._unauthorizedRequestResponse = unauthorizedRequestResponse
        return

class mouseclick(MouseAdapter):

    def __init__(self, extender):
        self._extender = extender

    def mouseReleased(self, evt):
        if evt.button == 3:
            self._extender.menu.show(evt.getComponent(), evt.getX(), evt.getY())


class autoScrollListener(AdjustmentListener):
    def __init__(self, extender):
        self._extender = extender

    def adjustmentValueChanged(self, e):
        if (self._extender.autoScroll.isSelected() == True):
            e.getAdjustable().setValue(e.getAdjustable().getMaximum())

class copySelectedURL(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        stringSelection = StringSelection(str(self._extender._helpers.analyzeRequest(self._extender._currentlyDisplayedItem).getUrl()));
        clpbrd = Toolkit.getDefaultToolkit().getSystemClipboard();
        clpbrd.setContents(stringSelection, None);

class handleMenuItems(ActionListener):
    def __init__(self, extender, messageInfo, menuName):
        self._extender = extender
        self._menuName = menuName
        self._messageInfo = messageInfo

    def actionPerformed(self, e):
        if self._menuName == "request":
            if self._messageInfo.getResponse() == None:
                message = self._extender.makeMessage(self._messageInfo,False,True)
                requestResponse = self._extender.makeRequest(self._messageInfo, message)
                self._extender.checkAuthorization(requestResponse,self._extender._helpers.analyzeResponse(requestResponse.getResponse()).getHeaders(),False)
            else:
                self._extender.checkAuthorization(self._messageInfo,self._extender._helpers.analyzeResponse(self._messageInfo.getResponse()).getHeaders(),False)
        if self._menuName == "cookie":
            self._extender.replaceString.setText(self._extender.getCookieFromMessage(self._messageInfo))

class menuTableFilter(ItemListener):
    def __init__(self, extender):
        self._extender = extender

    def itemStateChanged(self, e):
        oldLog = self._extender._log
        newLog = ArrayList()
        for logEntry in oldLog:
            if self._extender.menuES0.getState() == True and self._extender.menuES0.getText() == logEntry._enfocementStatus:
                newLog.add(logEntry)
            if self._extender.menuES1.getState() == True and self._extender.menuES1.getText() == logEntry._enfocementStatus:
                newLog.add(logEntry)
            if self._extender.menuES2.getState() == True and self._extender.menuES2.getText() == logEntry._enfocementStatus:
                newLog.add(logEntry)                

        self._extender._log = newLog
        self._extender._lock.acquire()
        row = newLog.size()
        self._extender.fireTableRowsInserted(row, row)
        self._extender._lock.release()
