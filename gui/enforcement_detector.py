from javax.swing import JLabel
from javax.swing import JComboBox
from javax.swing import JList
from javax.swing import JScrollPane
from javax.swing import JTextArea
from javax.swing import JPanel
from javax.swing import JButton
from javax.swing import DefaultListModel
from java.awt import Color
from javax.swing.border import LineBorder

def init_enforcement_detector(self):
        """
        init enforcement detector tab
        """

        EDLType = JLabel("Type:")
        EDLType.setBounds(10, 10, 140, 30)

        EDLContent = JLabel("Content:")
        EDLContent.setBounds(10, 50, 140, 30)

        EDLabelList = JLabel("Filter List:")
        EDLabelList.setBounds(10, 165, 140, 30)

        EDStrings = ["Headers (simple string): (enforced message headers contains)",
                     "Headers (regex): (enforced message headers contains)",
                     "Body (simple string): (enforced message body contains)",
                     "Body (regex): (enforced message body contains)",
                     "Full response (simple string): (enforced message contains)",
                     "Full response (regex): (enforced message contains)",
                     "Full response length: (of enforced response)",
                     "Status code equals: (numbers only)"]
        self.EDType = JComboBox(EDStrings)
        self.EDType.setBounds(80, 10, 430, 30)
       
        self.EDText = JTextArea("", 5, 30)

        scrollEDText = JScrollPane(self.EDText)
        scrollEDText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDText.setBounds(80, 50, 300, 110)  

        self.EDModel = DefaultListModel()
        self.EDList = JList(self.EDModel)

        scrollEDList = JScrollPane(self.EDList)
        scrollEDList.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDList.setBounds(80, 175, 300, 110)
        scrollEDList.setBorder(LineBorder(Color.BLACK)) 

        self.EDAdd = JButton("Add filter", actionPerformed=addEDFilter)
        self.EDAdd.setBounds(390, 85, 120, 30)
        self.EDDel = JButton("Remove filter", actionPerformed=delEDFilter)
        self.EDDel.setBounds(390, 210, 120, 30)
        self.EDMod = JButton("Modify filter", actionPerformed=modEDFilter)
        self.EDMod.setBounds(390, 250, 120, 30)

        AndOrStrings = ["And", "Or"]
        self.AndOrType = JComboBox(AndOrStrings)
        self.AndOrType.setBounds(390, 170, 120, 30)       

        self.EDPnl = JPanel()
        self.EDPnl.setLayout(None)
        self.EDPnl.setBounds(0, 0, 1000, 1000)
        self.EDPnl.add(EDLType)
        self.EDPnl.add(self.EDType)
        self.EDPnl.add(EDLContent)
        self.EDPnl.add(scrollEDText)
        self.EDPnl.add(self.EDAdd)
        self.EDPnl.add(self.AndOrType)
        self.EDPnl.add(self.EDDel)
        self.EDPnl.add(self.EDMod)
        self.EDPnl.add(EDLabelList)
        self.EDPnl.add(scrollEDList)


def init_enforcement_detector_unauthorized(self):
        """ init enforcement detector tab
        """

        EDLType = JLabel("Type:")
        EDLType.setBounds(10, 10, 140, 30)

        EDLContent = JLabel("Content:")
        EDLContent.setBounds(10, 50, 140, 30)

        EDLabelList = JLabel("Filter List:")
        EDLabelList.setBounds(10, 165, 140, 30)

        EDStrings = ["Headers (simple string): (enforced message headers contains)",
                     "Headers (regex): (enforced message headers contains)",
                     "Body (simple string): (enforced message body contains)",
                     "Body (regex): (enforced message body contains)",
                     "Full response (simple string): (enforced message contains)",
                     "Full response (regex): (enforced message contains)",
                     "Full response length: (of enforced response)",
                     "Status code equals: (numbers only)"]
        self.EDTypeUnauth = JComboBox(EDStrings)
        self.EDTypeUnauth.setBounds(80, 10, 430, 30)
       
        self.EDTextUnauth = JTextArea("", 5, 30)

        scrollEDTextUnauth = JScrollPane(self.EDTextUnauth)
        scrollEDTextUnauth.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDTextUnauth.setBounds(80, 50, 300, 110)     

        self.EDModelUnauth = DefaultListModel()
        self.EDListUnauth = JList(self.EDModelUnauth)

        scrollEDListUnauth = JScrollPane(self.EDListUnauth)
        scrollEDListUnauth.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollEDListUnauth.setBounds(80, 175, 300, 110)
        scrollEDListUnauth.setBorder(LineBorder(Color.BLACK))    

        self.EDAddUnauth = JButton("Add filter",
                                   actionPerformed=addEDFilterUnauth)
        self.EDAddUnauth.setBounds(390, 85, 120, 30)
        self.EDDelUnauth = JButton("Remove filter",
                                   actionPerformed=delEDFilterUnauth)
        self.EDDelUnauth.setBounds(390, 210, 120, 30)
        self.EDModUnauth = JButton("Modify filter",
                                   actionPerformed=modEDFilterUnauth)
        self.EDModUnauth.setBounds(390, 250, 120, 30)

        AndOrStrings = ["And", "Or"]
        self.AndOrTypeUnauth = JComboBox(AndOrStrings)
        self.AndOrTypeUnauth.setBounds(390, 170, 120, 30)        

        self.EDPnlUnauth = JPanel()
        self.EDPnlUnauth.setLayout(None)
        self.EDPnlUnauth.setBounds(0, 0, 1000, 1000)
        self.EDPnlUnauth.add(EDLType)
        self.EDPnlUnauth.add(self.EDTypeUnauth)
        self.EDPnlUnauth.add(EDLContent)
        self.EDPnlUnauth.add(scrollEDTextUnauth)
        self.EDPnlUnauth.add(self.EDAddUnauth)
        self.EDPnlUnauth.add(self.AndOrTypeUnauth)
        self.EDPnlUnauth.add(self.EDDelUnauth)
        self.EDPnlUnauth.add(self.EDModUnauth)
        self.EDPnlUnauth.add(EDLabelList)
        self.EDPnlUnauth.add(scrollEDListUnauth)



def addEDFilter(self, event):
        self.addFilterHelper(self.EDType, self.EDModel, self.EDText)

def delEDFilter(self, event):
        self.delFilterHelper(self.EDList)

def modEDFilter(self, event):
        self.modFilterHelper(self.EDList, self.EDType, self.EDText)

def addEDFilterUnauth(self, event):
        self.addFilterHelper(self.EDTypeUnauth, self.EDModelUnauth, self.EDTextUnauth)

def delEDFilterUnauth(self, event):
        self.delFilterHelper(self.EDListUnauth)

def modEDFilterUnauth(self, event):
        self.modFilterHelper(self.EDListUnauth, self.EDTypeUnauth, self.EDTextUnauth)
