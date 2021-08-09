#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
sys.path.append("..")

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

from helpers.filters import addFilterHelper, delFilterHelper, modFilterHelper

import re

class InterceptionFilters():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """  init interception filters tab
        """
        self._extender.savedHeaders = [{"title": "Temporary headers", "headers": "Cookie: Insert=injected; cookie=or;\nHeader: here"}]
        # IFStrings has to contains : character
        IFStrings = ["Scope items only: (Content is not required)", 
                     "URL Contains (simple string): ",
                     "URL Contains (regex): ",
                     "URL Not Contains (simple string): ",
                     "URL Not Contains (regex): ",
                     "Request Body contains (simple string): ",
                     "Request Body contains (regex): ",
                     "Request Body NOT contains (simple string): ",
                     "Request Body Not contains (regex): ",
                     "Response Body contains (simple string): ",
                     "Response Body contains (regex): ",
                     "Response Body NOT contains (simple string): ",
                     "Response Body Not contains (regex): ",
                     "Only HTTP methods (newline separated): ",
                     "Ignore HTTP methods (newline separated): ",
                     "Ignore spider requests: (Content is not required)",
                     "Ignore proxy requests: (Content is not required)",
                     "Ignore target requests: (Content is not required)"]
        self._extender.IFType = JComboBox(IFStrings)
        self._extender.IFType.setBounds(80, 10, 430, 30)
       
        self._extender.IFModel = DefaultListModel()
        self._extender.IFList = JList(self._extender.IFModel)

        scrollIFList = JScrollPane(self._extender.IFList)
        scrollIFList.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollIFList.setBounds(80, 175, 300, 110)
        scrollIFList.setBorder(LineBorder(Color.BLACK))

        # Adding some default interception filters
        # self.IFModel.addElement("Scope items only: (Content is not required)") # commented for better first impression.
        self._extender.IFModel.addElement("URL Not Contains (regex): \\.js|\\.css|\\.png|\\.jpg|\\.svg|\\.jpeg|\\.gif|\\.woff|\\.map|\\.bmp|\\.ico$")
        self._extender.IFModel.addElement("Ignore spider requests: ")
        
        self._extender.IFText = JTextArea("", 5, 30)

        scrollIFText = JScrollPane(self._extender.IFText)
        scrollIFText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollIFText.setBounds(80, 50, 300, 110)

        IFLType = JLabel("Type:")
        IFLType.setBounds(10, 10, 140, 30)

        IFLContent = JLabel("Content:")
        IFLContent.setBounds(10, 50, 140, 30)

        IFLabelList = JLabel("Filter List:")
        IFLabelList.setBounds(10, 165, 140, 30)

        self._extender.IFAdd = JButton("Add filter", actionPerformed=self.addIFFilter)
        self._extender.IFAdd.setBounds(390, 85, 120, 30)
        self._extender.IFDel = JButton("Remove filter", actionPerformed=self.delIFFilter)
        self._extender.IFDel.setBounds(390, 210, 120, 30)
        self._extender.IFMod = JButton("Modify filter", actionPerformed=self.modIFFilter)
        self._extender.IFMod.setBounds(390, 250, 120, 30)

        self._extender.filtersPnl = JPanel()
        self._extender.filtersPnl.setLayout(None)
        self._extender.filtersPnl.setBounds(0, 0, 1000, 1000)
        self._extender.filtersPnl.add(IFLType)
        self._extender.filtersPnl.add(self._extender.IFType)
        self._extender.filtersPnl.add(IFLContent)
        self._extender.filtersPnl.add(scrollIFText)
        self._extender.filtersPnl.add(self._extender.IFAdd)
        self._extender.filtersPnl.add(self._extender.IFDel)
        self._extender.filtersPnl.add(self._extender.IFMod)
        self._extender.filtersPnl.add(IFLabelList)
        self._extender.filtersPnl.add(scrollIFList)

    def addIFFilter(self, event):
        addFilterHelper(self._extender.IFType, self._extender.IFModel, self._extender.IFText)
        
    def delIFFilter(self, event):
        delFilterHelper(self._extender.IFList)

    def modIFFilter(self, event):
        modFilterHelper(self._extender.IFList, self._extender.IFType, self._extender.IFText)
