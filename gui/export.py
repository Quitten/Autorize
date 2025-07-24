#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

from java.io import File
from java.awt import Font
from javax.swing import JLabel
from javax.swing import JLabel
from javax.swing import JPanel
from javax.swing import JFrame
from javax.swing import JButton
from javax.swing import JCheckBox
from javax.swing import JComboBox
from javax.swing import GroupLayout
from javax.swing import JFileChooser
from java.awt.event import ItemListener

from save_restore import SaveRestore

class RemoveDups(ItemListener):
    def __init__(self, extender):
        self._extender = extender

    def itemStateChanged(self, e):
        return True

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

        self.removeDuplicates = JCheckBox("Remove Duplicates")
        self.removeDuplicates.setBounds(8, 120, 300, 30)
        self.removeDuplicates.setSelected(True)
        self.removeDuplicates.addItemListener(RemoveDups(self._extender))

        self.exportButton = JButton("Export",
                                    actionPerformed=self.export)
        self.exportButton.setBounds(390, 50, 100, 30)

        saveRestoreLabel = JLabel("State (incl. Configuration):")
        saveRestoreLabel.setBounds(10, 160, 250, 30)
        saveRestoreLabel.setFont(boldFont)

        self.saveStateButton = JButton("Save",
                                    actionPerformed=self.saveStateAction)
        self.saveStateButton.setBounds(10, 200, 100, 30)

        self.restoreStateButton = JButton("Restore",
                                        actionPerformed=self.restoreStateAction)
        self.restoreStateButton.setBounds(390, 200, 100, 30)

        self._extender.exportPnl = JPanel()
        layout = GroupLayout(self._extender.exportPnl)
        self._extender.exportPnl.setLayout(layout)
        layout.setAutoCreateGaps(True)
        layout.setAutoCreateContainerGaps(True)

        layout.setHorizontalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup()
                .addComponent(
                    exportLabel,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    exportLType,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    exportLES,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self.removeDuplicates,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    saveRestoreLabel,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self.saveStateButton,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(
                    self.exportES,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self.exportType,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup()
                .addComponent(
                    self.exportButton,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self.restoreStateButton,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
        )
        
        layout.setVerticalGroup(layout.createSequentialGroup()
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                    exportLabel,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                    exportLType,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self.exportType,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self.exportButton,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                    exportLES,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self.exportES,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createSequentialGroup()
                .addComponent(
                    self.removeDuplicates,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createSequentialGroup()
                .addComponent(
                    saveRestoreLabel,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
            )
            .addGroup(layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                .addComponent(
                    self.saveStateButton,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )
                .addComponent(
                    self.restoreStateButton,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                    GroupLayout.PREFERRED_SIZE,
                )    
            )
        )

    def export(self, event):
            if self.exportType.getSelectedItem() == "HTML":
                self.exportToHTML()
            else:
                self.exportToCSV()

    def saveStateAction(self, event):
        self.save_restore.saveState()

    def restoreStateAction(self, event):
        self.save_restore.restoreState()

    def shouldIncludeRow(self, logEntry, enforcementStatusFilter):
        should_include = False
        
        if enforcementStatusFilter == "All Statuses":
            should_include = True
        elif enforcementStatusFilter == "As table filter":
            if hasattr(self._extender, 'showBypassed') and hasattr(self._extender, 'showIsEnforced') and hasattr(self._extender, 'showEnforced'):
                # Check unauthenticated status
                unauth_status = logEntry._enfocementStatusUnauthorized
                if ((self._extender.showBypassed.isSelected() and self.BYPASSSED_STR == unauth_status) or
                    (self._extender.showIsEnforced.isSelected() and self.IS_ENFORCED_STR == unauth_status) or
                    (self._extender.showEnforced.isSelected() and self.ENFORCED_STR == unauth_status) or
                    ("Disabled" == unauth_status)):
                    should_include = True
                
                for user_id in logEntry.get_all_users():
                    user_data = logEntry.get_user_enforcement(user_id)
                    if user_data:
                        user_status = user_data['enforcementStatus']
                        if ((self._extender.showBypassed.isSelected() and self.BYPASSSED_STR == user_status) or
                            (self._extender.showIsEnforced.isSelected() and self.IS_ENFORCED_STR == user_status) or
                            (self._extender.showEnforced.isSelected() and self.ENFORCED_STR == user_status)):
                            should_include = True
                            break
            else:
                should_include = True
        else:
            if enforcementStatusFilter == logEntry._enfocementStatusUnauthorized:
                should_include = True
            else:
                for user_id in logEntry.get_all_users():
                    user_data = logEntry.get_user_enforcement(user_id)
                    if user_data and enforcementStatusFilter == user_data['enforcementStatus']:
                        should_include = True
                        break
        
        return should_include

    def exportToHTML(self):
        parentFrame = JFrame()
        fileChooser = JFileChooser()
        fileChooser.setSelectedFile(File("AutorizeReport.html"))
        fileChooser.setDialogTitle("Save Autorize Report")
        userSelection = fileChooser.showSaveDialog(parentFrame)
        if userSelection == JFileChooser.APPROVE_OPTION:
            fileToSave = fileChooser.getSelectedFile()

        enforcementStatusFilter = self.exportES.getSelectedItem()

        header_html = "<thead><tr><th width=\"3%\">ID</th><th width=\"5%\">Method</th><th width=\"30%\">URL</th><th width=\"7%\">Original length</th><th width=\"7%\">Unauth length</th><th width=\"10%\">Unauth Status</th>"
        
        if hasattr(self._extender, 'userTab') and self._extender.userTab:
            for user_id in sorted(self._extender.userTab.user_tabs.keys()):
                user_name = self._extender.userTab.user_tabs[user_id]['user_name']
                header_html += "<th width=\"7%\">{} Len</th><th width=\"10%\">{} Status</th>".format(user_name, user_name)
        
        header_html += "</tr></thead>"
        
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
        <div class="datagrid"><table>""" + header_html + """
        <tbody>"""
        
        unique_HTML_lines = set()
        for i in range(0, self._log.size()):
            logEntry = self._log.get(i)
            
            if self.removeDuplicates.isSelected():
                user_statuses = []
                for user_id in sorted(logEntry.get_all_users()):
                    user_data = logEntry.get_user_enforcement(user_id)
                    if user_data:
                        user_statuses.append(user_data['enforcementStatus'])
                
                lineData = "\t%s\t%s\t%s\t%s" % (logEntry._method, logEntry._url, 
                                                logEntry._enfocementStatusUnauthorized, 
                                                "\t".join(user_statuses))
                if lineData in unique_HTML_lines:
                    continue
                else:
                    unique_HTML_lines.add(lineData)

            if not self.shouldIncludeRow(logEntry, enforcementStatusFilter):
                continue

            row_html = "<tr><td>%d</td><td>%s</td><td><a href=\"%s\">%s</a></td>" % (
                logEntry._id, logEntry._method, logEntry._url, logEntry._url)

            orig_len = len(logEntry._originalrequestResponse.getResponse()) if logEntry._originalrequestResponse else 0
            row_html += "<td>%d</td>" % orig_len
            
            unauth_len = 0
            if logEntry._unauthorizedRequestResponse:
                unauth_len = len(logEntry._unauthorizedRequestResponse.getResponse())
            
            unauth_color = ""
            if logEntry._enfocementStatusUnauthorized == self.BYPASSSED_STR:
                unauth_color = "red"
            elif logEntry._enfocementStatusUnauthorized == self.IS_ENFORCED_STR:
                unauth_color = "yellow"
            elif logEntry._enfocementStatusUnauthorized == self.ENFORCED_STR:
                unauth_color = "LawnGreen"
            
            row_html += "<td>%d</td><td bgcolor=\"%s\">%s</td>" % (unauth_len, unauth_color, logEntry._enfocementStatusUnauthorized)
            
            # User data
            if hasattr(self._extender, 'userTab') and self._extender.userTab:
                for user_id in sorted(self._extender.userTab.user_tabs.keys()):
                    user_data = logEntry.get_user_enforcement(user_id)
                    if user_data and user_data['requestResponse']:
                        user_len = len(user_data['requestResponse'].getResponse())
                        user_status = user_data['enforcementStatus']
                        
                        user_color = ""
                        if user_status == self.BYPASSSED_STR:
                            user_color = "red"
                        elif user_status == self.IS_ENFORCED_STR:
                            user_color = "yellow"
                        elif user_status == self.ENFORCED_STR:
                            user_color = "LawnGreen"
                        
                        row_html += "<td>%d</td><td bgcolor=\"%s\">%s</td>" % (user_len, user_color, user_status)
                    else:
                        row_html += "<td>0</td><td>N/A</td>"
            
            row_html += "</tr>"
            htmlContent += row_html

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
        
        csvContent = "ID,Method,URL,Original Length,Unauth Length,Unauth Status"
        
        if hasattr(self._extender, 'userTab') and self._extender.userTab:
            for user_id in sorted(self._extender.userTab.user_tabs.keys()):
                user_name = self._extender.userTab.user_tabs[user_id]['user_name']
                csvContent += ",{} Length,{} Status".format(user_name, user_name)
        
        csvContent += "\n"

        unique_CSV_lines = set()
        for i in range(0, self._log.size()):
            logEntry = self._log.get(i)
            
            if self.removeDuplicates.isSelected():
                user_statuses = []
                for user_id in sorted(logEntry.get_all_users()):
                    user_data = logEntry.get_user_enforcement(user_id)
                    if user_data:
                        user_statuses.append(user_data['enforcementStatus'])
                
                lineData = ",{},{},{},{}".format(logEntry._method, logEntry._url, 
                                                logEntry._enfocementStatusUnauthorized, 
                                                ",".join(user_statuses))
                if lineData in unique_CSV_lines:
                    continue
                else:
                    unique_CSV_lines.add(lineData)

            if not self.shouldIncludeRow(logEntry, enforcementStatusFilter):
                continue

            orig_len = len(logEntry._originalrequestResponse.getResponse()) if logEntry._originalrequestResponse else 0
            unauth_len = len(logEntry._unauthorizedRequestResponse.getResponse()) if logEntry._unauthorizedRequestResponse else 0
            
            url_safe = '"{}"'.format(str(logEntry._url).replace('"', '""'))
            
            csv_row = '{},{},{},{},{},"{}"'.format(
                logEntry._id, logEntry._method, url_safe, orig_len, unauth_len, logEntry._enfocementStatusUnauthorized)
            
            # User data
            if hasattr(self._extender, 'userTab') and self._extender.userTab:
                for user_id in sorted(self._extender.userTab.user_tabs.keys()):
                    user_data = logEntry.get_user_enforcement(user_id)
                    if user_data and user_data['requestResponse']:
                        user_len = len(user_data['requestResponse'].getResponse())
                        user_status = user_data['enforcementStatus']
                        csv_row += ',{},"{}"'.format(user_len, user_status)
                    else:
                        csv_row += ',0,"N/A"'
            
            csv_row += "\n"
            csvContent += csv_row

        f = open(fileToSave.getAbsolutePath(), 'w')
        f.writelines(csvContent)
        f.close()