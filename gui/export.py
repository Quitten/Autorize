#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import sys
sys.path.append("..")

from javax.swing import JFileChooser
from javax.swing import JComboBox
from javax.swing import JButton
from javax.swing import JLabel
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing import JFrame
from java.awt import Font
from java.io import File

from save_restore import SaveRestore

class Export():
    def __init__(self, extender):
        self._extender = extender
        self.BYPASSSED_STR = extender.BYPASSSED_STR
        self.ENFORCED_STR = extender.ENFORCED_STR
        self.IS_ENFORCED_STR = extender.IS_ENFORCED_STR
        self._log = extender._log
        self.save_restore = SaveRestore(extender)

    def draw(self):
            """ init Save/Restore
            """
            
            exportLabel = JLabel("Export:")
            exportLabel.setBounds(10, 10, 100, 30)
            labelFont = exportLabel.getFont()
            boldFont = Font(labelFont.getFontName(), Font.BOLD, labelFont.getSize())
            exportLabel.setFont(boldFont)

            exportLType = JLabel("File Type:")
            exportLType.setBounds(10, 50, 100, 30)

            exportFileTypes = ["HTML", "CSV"]
            self.exportType = JComboBox(exportFileTypes)
            self.exportType.setBounds(100, 50, 200, 30)

            exportES = ["All Statuses", "As table filter",
                        self._extender.BYPASSSED_STR,
                        self._extender.IS_ENFORCED_STR,
                        self._extender.ENFORCED_STR]
            self.exportES = JComboBox(exportES)
            self.exportES.setBounds(100, 90, 200, 30)

            exportLES = JLabel("Statuses:")
            exportLES.setBounds(10, 90, 100, 30)

            self.exportButton = JButton("Export",
                                        actionPerformed=self.export)
            self.exportButton.setBounds(390, 50, 100, 30)

            saveRestoreLabel = JLabel("Save / Restore:")
            saveRestoreLabel.setBounds(10, 250, 100, 30)    
            saveRestoreLabel.setFont(boldFont)

            self.saveStateButton = JButton("Save state",
                                        actionPerformed=self.saveStateAction)
            self.saveStateButton.setBounds(10, 200, 100, 30)

            self.restoreStateButton = JButton("Restore state",
                                            actionPerformed=self.restoreStateAction)
            self.restoreStateButton.setBounds(390, 200, 100, 30)        
            
            self._extender.exportPnl = JPanel()
            exportPnl = self._extender.exportPnl 
            exportPnl.setLayout(None)
            exportPnl.setBounds(0, 0, 1000, 1000)
            exportPnl.add(exportLabel)
            exportPnl.add(exportLType)
            exportPnl.add(self.exportType)
            exportPnl.add(exportLES)
            exportPnl.add(self.exportES)
            exportPnl.add(self.exportButton)
            exportPnl.add(saveRestoreLabel)
            exportPnl.add(self.saveStateButton)
            exportPnl.add(self.restoreStateButton)

    def export(self, event):
            if self.exportType.getSelectedItem() == "HTML":
                self.exportToHTML()
            else:
                self.exportToCSV()

    def saveStateAction(self, event):
        self.save_restore.saveState()
        
    def restoreStateAction(self, event):
        self.save_restore.restoreState()

    def exportToHTML(self):
        parentFrame = JFrame()
        fileChooser = JFileChooser()
        fileChooser.setSelectedFile(File("AutorizeReport.html"))
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
        <thead><tr><th width=\"3%\">ID</th><th width=\"5%\">Method</th><th width=\"43%\">URL</th><th width=\"9%\">Original length</th><th width=\"9%\">Modified length</th><th width=\"9%\">Unauthorized length</th><th width=\"11%\">Authorization Enforcement Status</th><th width=\"11%\">Authorization Unauthenticated Status</th></tr></thead>
        <tbody>"""

        for i in range(0,self._log.size()):
            color_modified = ""
            if self._log.get(i)._enfocementStatus == self.BYPASSSED_STR:
                color_modified = "red"
            elif self._log.get(i)._enfocementStatus == self.IS_ENFORCED_STR:
                color_modified = "yellow"
            elif self._log.get(i)._enfocementStatus == self.ENFORCED_STR:
                color_modified = "LawnGreen"

            color_unauthorized = ""
            if self._log.get(i)._enfocementStatusUnauthorized == self.BYPASSSED_STR:
                color_unauthorized = "red"
            elif self._log.get(i)._enfocementStatusUnauthorized == self.IS_ENFORCED_STR:
                color_unauthorized = "yellow"
            elif self._log.get(i)._enfocementStatusUnauthorized == self.ENFORCED_STR:
                color_unauthorized = "LawnGreen"

            if enforcementStatusFilter == "All Statuses":
                htmlContent += "<tr><td>%d</td><td>%s</td><td><a href=\"%s\">%s</a></td><td>%d</td><td>%d</td><td>%d</td><td bgcolor=\"%s\">%s</td><td bgcolor=\"%s\">%s</td></tr>" % (self._log.get(i)._id, self._log.get(i)._method, self._log.get(i)._url, self._log.get(i)._url, len(self._log.get(i)._originalrequestResponse.getResponse()) if self._log.get(i)._originalrequestResponse is not None else 0, len(self._log.get(i)._requestResponse.getResponse()) if self._log.get(i)._requestResponse is not None else 0, len(self._log.get(i)._unauthorizedRequestResponse.getResponse()) if self._log.get(i)._unauthorizedRequestResponse is not None else 0, color_modified, self._log.get(i)._enfocementStatus, color_unauthorized, self._log.get(i)._enfocementStatusUnauthorized)
            elif enforcementStatusFilter == "As table filter":
                if ((self._extender.showAuthBypassModified.isSelected() and self.BYPASSSED_STR == self._log.get(i)._enfocementStatus) or
                    (self._extender.showAuthPotentiallyEnforcedModified.isSelected() and "Is enforced???" == self._log.get(i)._enfocementStatus) or
                    (self._extender.showAuthEnforcedModified.isSelected() and self.ENFORCED_STR == self._log.get(i)._enfocementStatus) or
                    (self._extender.showAuthBypassUnauthenticated.isSelected() and self.BYPASSSED_STR == self._log.get(i)._enfocementStatusUnauthorized) or
                    (self._extender.showAuthPotentiallyEnforcedUnauthenticated.isSelected() and "Is enforced???" == self._log.get(i)._enfocementStatusUnauthorized) or
                    (self._extender.showAuthEnforcedUnauthenticated.isSelected() and self.ENFORCED_STR == self._log.get(i)._enfocementStatusUnauthorized) or
                    (self._extender.showDisabledUnauthenticated.isSelected() and "Disabled" == self._log.get(i)._enfocementStatusUnauthorized)):
                    htmlContent += "<tr><td>%d</td><td>%s</td><td><a href=\"%s\">%s</a></td><td>%d</td><td>%d</td><td>%d</td><td bgcolor=\"%s\">%s</td><td bgcolor=\"%s\">%s</td></tr>" % (self._log.get(i)._id, self._log.get(i)._method, self._log.get(i)._url, self._log.get(i)._url, len(self._log.get(i)._originalrequestResponse.getResponse()) if self._log.get(i)._originalrequestResponse is not None else 0, len(self._log.get(i)._requestResponse.getResponse()) if self._log.get(i)._requestResponse is not None else 0, len(self._log.get(i)._unauthorizedRequestResponse.getResponse()) if self._log.get(i)._unauthorizedRequestResponse is not None else 0, color_modified, self._log.get(i)._enfocementStatus, color_unauthorized, self._log.get(i)._enfocementStatusUnauthorized)
            else:
                if (enforcementStatusFilter == self._log.get(i)._enfocementStatus) or (enforcementStatusFilter == self._log.get(i)._enfocementStatusUnauthorized):
                    htmlContent += "<tr><td>%d</td><td>%s</td><td><a href=\"%s\">%s</a></td><td>%d</td><td>%d</td><td>%d</td><td bgcolor=\"%s\">%s</td><td bgcolor=\"%s\">%s</td></tr>" % (self._log.get(i)._id, self._log.get(i)._method, self._log.get(i)._url, self._log.get(i)._url, len(self._log.get(i)._originalrequestResponse.getResponse()) if self._log.get(i)._originalrequestResponse is not None else 0, len(self._log.get(i)._requestResponse.getResponse()) if self._log.get(i)._requestResponse is not None else 0, len(self._log.get(i)._unauthorizedRequestResponse.getResponse()) if self._log.get(i)._unauthorizedRequestResponse is not None else 0, color_modified, self._log.get(i)._enfocementStatus, color_unauthorized, self._log.get(i)._enfocementStatusUnauthorized)

        htmlContent += "</tbody></table></div></body></html>"
        f = open(fileToSave.getAbsolutePath(), 'w')
        f.writelines(htmlContent)
        f.close()

    def exportToCSV(self):
        parentFrame = JFrame()
        fileChooser = JFileChooser()
        fileChooser.setSelectedFile(File("AutorizeReport.csv"))
        fileChooser.setDialogTitle("Save Autorize Report")
        userSelection = fileChooser.showSaveDialog(parentFrame)
        if userSelection == JFileChooser.APPROVE_OPTION:
            fileToSave = fileChooser.getSelectedFile()

        enforcementStatusFilter = self.exportES.getSelectedItem()
        csvContent = "id\tMethod\tURL\tOriginal length\tModified length\tUnauthorized length\tAuthorization Enforcement Status\tAuthorization Unauthenticated Status\n"

        for i in range(0,self._log.size()):

            if enforcementStatusFilter == "All Statuses":
                csvContent += "%d\t%s\t%s\t%d\t%d\t%d\t%s\t%s\n" % (self._log.get(i)._id, self._log.get(i)._method, self._log.get(i)._url, len(self._log.get(i)._originalrequestResponse.getResponse()) if self._log.get(i)._originalrequestResponse is not None else 0, len(self._log.get(i)._requestResponse.getResponse()) if self._log.get(i)._requestResponse is not None else 0, len(self._log.get(i)._unauthorizedRequestResponse.getResponse()) if self._log.get(i)._unauthorizedRequestResponse is not None else 0, self._log.get(i)._enfocementStatus, self._log.get(i)._enfocementStatusUnauthorized)
            elif enforcementStatusFilter == "As table filter":                
                if ((self._extender.showAuthBypassModified.isSelected() and self.BYPASSSED_STR == self._log.get(i)._enfocementStatus) or
                    (self._extender.showAuthPotentiallyEnforcedModified.isSelected() and "Is enforced???" == self._log.get(i)._enfocementStatus) or
                    (self._extender.showAuthEnforcedModified.isSelected() and self.ENFORCED_STR == self._log.get(i)._enfocementStatus) or
                    (self._extender.showAuthBypassUnauthenticated.isSelected() and self.BYPASSSED_STR == self._log.get(i)._enfocementStatusUnauthorized) or
                    (self._extender.showAuthPotentiallyEnforcedUnauthenticated.isSelected() and "Is enforced???" == self._log.get(i)._enfocementStatusUnauthorized) or
                    (self._extender.showAuthEnforcedUnauthenticated.isSelected() and self.ENFORCED_STR == self._log.get(i)._enfocementStatusUnauthorized) or
                    (self._extender.showDisabledUnauthenticated.isSelected() and "Disabled" == self._log.get(i)._enfocementStatusUnauthorized)):
                    csvContent += "%d\t%s\t%s\t%d\t%d\t%d\t%s\t%s\n" % (self._log.get(i)._id, self._log.get(i)._method, self._log.get(i)._url, len(self._log.get(i)._originalrequestResponse.getResponse()) if self._log.get(i)._originalrequestResponse is not None else 0, len(self._log.get(i)._requestResponse.getResponse()) if self._log.get(i)._requestResponse is not None else 0, len(self._log.get(i)._unauthorizedRequestResponse.getResponse()) if self._log.get(i)._unauthorizedRequestResponse is not None else 0, self._log.get(i)._enfocementStatus, self._log.get(i)._enfocementStatusUnauthorized)
            else:
                if (enforcementStatusFilter == self._log.get(i)._enfocementStatus) or (enforcementStatusFilter == self._log.get(i)._enfocementStatusUnauthorized):
                    csvContent += "%d\t%s\t%s\t%d\t%d\t%d\t%s\t%s\n" % (self._log.get(i)._id, self._log.get(i)._method, self._log.get(i)._url, len(self._log.get(i)._originalrequestResponse.getResponse()) if self._log.get(i)._originalrequestResponse is not None else 0, len(self._log.get(i)._requestResponse.getResponse()) if self._log.get(i)._requestResponse is not None else 0, len(self._log.get(i)._unauthorizedRequestResponse.getResponse()) if self._log.get(i)._unauthorizedRequestResponse is not None else 0, self._log.get(i)._enfocementStatus, self._log.get(i)._enfocementStatusUnauthorized)
        
        f = open(fileToSave.getAbsolutePath(), 'w')
        f.writelines(csvContent)
        f.close()
