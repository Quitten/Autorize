from javax.swing import JComboBox
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing import JList
from javax.swing import JScrollPane
from javax.swing import JTextArea
from javax.swing import JButton
from javax.swing import DefaultListModel
from java.awt import Color
from javax.swing.border import LineBorder
import re

def init_interception_filters(self):
        """  init interception filters tab
        """
        self.savedHeaders = [{"title": "Temporary headers", "headers": "Cookie: Insert=injected; cookie=or;\nHeader: here"}]
        # IFStrings has to contains : character
        IFStrings = ["Scope items only: (Content is not required)", 
                     "URL Contains (simple string): ",
                     "URL Contains (regex): ",
                     "URL Not Contains (simple string): ",
                     "URL Not Contains (regex): ",
                     "Only HTTP methods (newline separated): ",
                     "Ignore HTTP methods (newline separated): ",
                     "Ignore spider requests: (Content is not required)",
                     "Ignore proxy requests: (Content is not required)",
                     "Ignore target requests: (Content is not required)"]
        self.IFType = JComboBox(IFStrings)
        self.IFType.setBounds(80, 10, 430, 30)
       
        self.IFModel = DefaultListModel()
        self.IFList = JList(self.IFModel)

        scrollIFList = JScrollPane(self.IFList)
        scrollIFList.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollIFList.setBounds(80, 175, 300, 110)
        scrollIFList.setBorder(LineBorder(Color.BLACK))

        # Adding some default interception filters
        # self.IFModel.addElement("Scope items only: (Content is not required)") # commented for better first impression.
        self.IFModel.addElement("URL Not Contains (regex): \\.js|\\.css|\\.png|\\.jpg|\\.svg|\\.jpeg|\\.gif|\\.woff|\\.map|\\.bmp|\\.ico$")
        self.IFModel.addElement("Ignore spider requests: ")
        
        self.IFText = JTextArea("", 5, 30)

        scrollIFText = JScrollPane(self.IFText)
        scrollIFText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollIFText.setBounds(80, 50, 300, 110)

        IFLType = JLabel("Type:")
        IFLType.setBounds(10, 10, 140, 30)

        IFLContent = JLabel("Content:")
        IFLContent.setBounds(10, 50, 140, 30)

        IFLabelList = JLabel("Filter List:")
        IFLabelList.setBounds(10, 165, 140, 30)

        self.IFAdd = JButton("Add filter", actionPerformed=addIFFilter)
        self.IFAdd.setBounds(390, 85, 120, 30)
        self.IFDel = JButton("Remove filter", actionPerformed=delIFFilter)
        self.IFDel.setBounds(390, 210, 120, 30)
        self.IFMod = JButton("Modify filter", actionPerformed=modIFFilter)
        self.IFMod.setBounds(390, 250, 120, 30)

        self.filtersPnl = JPanel()
        self.filtersPnl.setLayout(None)
        self.filtersPnl.setBounds(0, 0, 1000, 1000)
        self.filtersPnl.add(IFLType)
        self.filtersPnl.add(self.IFType)
        self.filtersPnl.add(IFLContent)
        self.filtersPnl.add(scrollIFText)
        self.filtersPnl.add(self.IFAdd)
        self.filtersPnl.add(self.IFDel)
        self.filtersPnl.add(self.IFMod)
        self.filtersPnl.add(IFLabelList)
        self.filtersPnl.add(scrollIFList)

#
## FilterHelpers
#
def addFilterHelper(self, typeObj, model, textObj):
        typeName = typeObj.getSelectedItem().split(":")[0]
        model.addElement(typeName + ": " + textObj.getText().strip())
        textObj.setText("")

def delFilterHelper(self, listObj):
        index = listObj.getSelectedIndex()
        if not index == -1:
            listObj.getModel().remove(index)

def modFilterHelper(self, listObj, typeObj, textObj):
        index = listObj.getSelectedIndex()
        if not index == -1:
            valt = listObj.getSelectedValue()
            val = valt.split(":", 1)[1].strip()
            modifiedFilter = valt.split(":", 1)[0].strip() + ":"
            typeObj.getModel().setSelectedItem(modifiedFilter)
            if ("Scope items" not in valt) and ("Content-Len" not in valt):
                textObj.setText(val)
            listObj.getModel().remove(index)

def addIFFilter(self, event):
        self.addFilterHelper(self.IFType, self.IFModel, self.IFText)
        
def delIFFilter(self, event):
        self.delFilterHelper(self.IFList)
        
def modIFFilter(self, event):
        self.modFilterHelper(self.IFList, self.IFType, self.IFText)