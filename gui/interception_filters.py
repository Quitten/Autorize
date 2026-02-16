#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
sys.path.append("..")

from javax.swing import JList
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing import JButton
from javax.swing import JComboBox
from javax.swing import JTextArea
from javax.swing import JScrollPane
from javax.swing import GroupLayout
from javax.swing import DefaultListModel
from javax.swing.border import LineBorder
from java.awt import Color
from helpers.filters import addFilterHelper, delFilterHelper, modFilterHelper


class InterceptionFilters():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """  init interception filters tab
        """
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
                     "Request headers contain: ",
                     "Request headers don't contain: ",
                     "Response headers contain: ",
                     "Response headers don't contain: ",
                     "Only HTTP methods (newline separated): ",
                     "Ignore HTTP methods (newline separated): ",
                     "Ignore spider requests: (Content is not required)",
                     "Ignore proxy requests: (Content is not required)",
                     "Ignore target requests: (Content is not required)",
                     "Ignore OPTIONS requests: (Content is not required)",
                     "Drop proxy listener ports: (Separated by comma)"
                     ]
        self._extender.IFType = JComboBox(IFStrings)
        self._extender.IFType.setBounds(80, 10, 430, 30)
       
        self._extender.IFModel = DefaultListModel()
        self._extender.IFList = JList(self._extender.IFModel)
        self._extender.IFList.setPrototypeCellValue("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        scrollIFList = JScrollPane(self._extender.IFList)
        scrollIFList.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollIFList.setHorizontalScrollBarPolicy(JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED)
        scrollIFList.setBounds(80, 175, 300, 110)
        scrollIFList.setBorder(LineBorder(Color.BLACK))

        # Adding some default interception filters
        # self.IFModel.addElement("Scope items only: (Content is not required)") # commented for better first impression.
        self._extender.IFModel.addElement("URL Not Contains (regex): (\\.js|\\.css|\\.png|\\.jpg|\\.svg|\\.jpeg|\\.gif|\\.woff|\\.map|\\.bmp|\\.ico)(?![a-z]+)[?]*[\S]*$")
        self._extender.IFModel.addElement("Ignore spider requests: ")
        
        self._extender.IFText = JTextArea("", 5, 30)

        scrollIFText = JScrollPane(self._extender.IFText)
        scrollIFText.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED)
        scrollIFText.setBounds(80, 50, 300, 110)
        scrollIFText.setBorder(LineBorder(Color.BLACK))

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
        layout = GroupLayout(self._extender.filtersPnl)
        self._extender.filtersPnl.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        layout.setHorizontalGroup(layout.createSequentialGroup()
            .addGroup(
                layout.createParallelGroup()
                    .addComponent(
                        IFLType,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        IFLContent,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        IFLabelList,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                )
            .addGroup(
                layout.createParallelGroup()
                    .addComponent(
                        self._extender.IFType,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        scrollIFText,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        scrollIFList,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addComponent(
                        self._extender.IFAdd,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                    .addGroup(
                        layout.createSequentialGroup()
                            .addComponent(
                                self._extender.IFDel,
                                GroupLayout.PREFERRED_SIZE,
                                GroupLayout.PREFERRED_SIZE,
                                GroupLayout.PREFERRED_SIZE,
                            )
                            .addComponent(
                                self._extender.IFMod,
                                GroupLayout.PREFERRED_SIZE,
                                GroupLayout.PREFERRED_SIZE,
                                GroupLayout.PREFERRED_SIZE,
                            )
                    )
                )
            )
        

        layout.setVerticalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                    IFLType,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self._extender.IFType,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                    IFLContent,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    scrollIFText,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addComponent(
                self._extender.IFAdd,
                GroupLayout.PREFERRED_SIZE,
                GroupLayout.PREFERRED_SIZE,
                GroupLayout.PREFERRED_SIZE,
            )
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                    IFLabelList,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    scrollIFList,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                        self._extender.IFDel,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                        GroupLayout.PREFERRED_SIZE,
                    )
                .addComponent(
                    self._extender.IFMod,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
        )
    




    def addIFFilter(self, event):
        addFilterHelper(self._extender.IFType, self._extender.IFModel, self._extender.IFText)
        
    def delIFFilter(self, event):
        delFilterHelper(self._extender.IFList)

    def modIFFilter(self, event):
        modFilterHelper(self._extender.IFList, self._extender.IFType, self._extender.IFText)
