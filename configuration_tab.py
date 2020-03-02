from javax.swing import DefaultComboBoxModel
from java.awt.event import ActionListener
from javax.swing import JToggleButton
from javax.swing import JScrollPane
from javax.swing import JTabbedPane
from javax.swing import JOptionPane
from javax.swing import JComboBox
from javax.swing import JTextArea
from javax.swing import JCheckBox
from javax.swing import JButton
from javax.swing import JPanel

from table import clearList

class ConfigurationTab():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """  init configuration tab
        """

        self._extender.startButton = JToggleButton("Autorize is off",
                                    actionPerformed=self.startOrStop)
        self._extender.startButton.setBounds(10, 20, 230, 30)

        self._extender.clearButton = JButton("Clear List", actionPerformed=clearList)
        self._extender.clearButton.setBounds(10, 80, 100, 30)
        self._extender.autoScroll = JCheckBox("Auto Scroll")
        self._extender.autoScroll.setBounds(145, 80, 130, 30)

        self._extender.ignore304 = JCheckBox("Ignore 304/204 status code responses")
        self._extender.ignore304.setBounds(280, 5, 300, 30)
        self._extender.ignore304.setSelected(True)

        self._extender.prevent304 = JCheckBox("Prevent 304 Not Modified status code")
        self._extender.prevent304.setBounds(280, 25, 300, 30)    
        self._extender.interceptRequestsfromRepeater = JCheckBox("Intercept requests from Repeater")
        self._extender.interceptRequestsfromRepeater.setBounds(280, 45, 300, 30)

        self._extender.doUnauthorizedRequest = JCheckBox("Check unauthenticated")
        self._extender.doUnauthorizedRequest.setBounds(280, 65, 300, 30)
        self._extender.doUnauthorizedRequest.setSelected(True)

        self._extender.saveHeadersButton = JButton("Save headers",
                                        actionPerformed=self.saveHeaders)
        self._extender.saveHeadersButton.setBounds(360, 115, 120, 30)

        savedHeadersTitles = self.getSavedHeadersTitles()
        self._extender.savedHeadersTitlesCombo = JComboBox(savedHeadersTitles)
        self._extender.savedHeadersTitlesCombo.addActionListener(savedHeaderChange(self))
        self._extender.savedHeadersTitlesCombo.setBounds(10, 115, 300, 30)

        self._extender.replaceString = JTextArea("Cookie: Insert=injected; cookie=or;\nHeader: here", 5, 30)
        self._extender.replaceString.setWrapStyleWord(True)
        self._extender.replaceString.setLineWrap(True)
        scrollReplaceString = JScrollPane(self._extender.replaceString)
        scrollReplaceString.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollReplaceString.setBounds(10, 150, 470, 150)

        self._extender.fetchButton = JButton("Fetch cookies from last request",
                                actionPerformed=self.fetchCookies)
        self._extender.fetchButton.setEnabled(False)
        self._extender.fetchButton.setBounds(10, 305, 250, 30)

        self._extender.filtersTabs = JTabbedPane()
        self._extender.filtersTabs = self._extender.filtersTabs
        self._extender.filtersTabs.addTab("Enforcement Detector", self._extender.EDPnl)
        self._extender.filtersTabs.addTab("Detector Unauthenticated", self._extender.EDPnlUnauth)
        self._extender.filtersTabs.addTab("Interception Filters", self._extender.filtersPnl)
        self._extender.filtersTabs.addTab("Match/Replace", self._extender.MRPnl)
        self._extender.filtersTabs.addTab("Table Filter", self._extender.filterPnl)
        self._extender.filtersTabs.addTab("Save/Restore", self._extender.exportPnl)
        

        self._extender.filtersTabs.setSelectedIndex(2)
        self._extender.filtersTabs.setBounds(0, 350, 2000, 700)
        

        self._extender.pnl = JPanel()
        self.pnl = self._extender.pnl
        self.pnl.setBounds(0, 0, 1000, 1000)
        self.pnl.setLayout(None)
        self.pnl.add(self._extender.startButton)
        self.pnl.add(self._extender.clearButton)
        self.pnl.add(scrollReplaceString)
        self.pnl.add(self._extender.saveHeadersButton)
        self.pnl.add(self._extender.savedHeadersTitlesCombo)
        self.pnl.add(self._extender.fetchButton)
        self.pnl.add(self._extender.autoScroll)
        self.pnl.add(self._extender.interceptRequestsfromRepeater)
        self.pnl.add(self._extender.ignore304)
        self.pnl.add(self._extender.prevent304)
        self.pnl.add(self._extender.doUnauthorizedRequest)
        self.pnl.add(self._extender.filtersTabs)
    
    def startOrStop(self, event):
        if self._extender.startButton.getText() == "Autorize is off":
            self._extender.startButton.setText("Autorize is on")
            self._extender.startButton.setSelected(True)
            self._extender.intercept = 1
        else:
            self._extender.startButton.setText("Autorize is off")
            self._extender.startButton.setSelected(False)
            self._extender.intercept = 0

    def saveHeaders(self, event):
        savedHeadersTitle = JOptionPane.showInputDialog("Please provide saved headers title:")
        self._extender.savedHeaders.append({'title': savedHeadersTitle, 'headers': self._extender.replaceString.getText()})
        self._extender.savedHeadersTitlesCombo.setModel(DefaultComboBoxModel(self.getSavedHeadersTitles()))
        self._extender.savedHeadersTitlesCombo.getModel().setSelectedItem(savedHeadersTitle)

    def getSavedHeadersTitles(self):
        titles = []
        for savedHeaderObj in self._extender.savedHeaders:
            titles.append(savedHeaderObj['title'])
        return titles

    def fetchCookies(self, event):
        if self._extender.lastCookies:
            self._extender.replaceString.setText(self._extender.lastCookies)

class savedHeaderChange(ActionListener):
    def __init__(self, extender):
        self._extender = extender

    def actionPerformed(self, e):
        selectedTitle = self._extender.savedHeadersTitlesCombo.getSelectedItem()
        headers = [x for x in self._extender.savedHeaders if x['title'] == selectedTitle]
        self._extender.replaceString.setText(headers[0]['headers'])

