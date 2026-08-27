#!/usr/bin/env python
# -*- coding: utf-8 -*-

from javax.swing import JPanel
from javax.swing import JLabel
from javax.swing import JButton
from javax.swing import JCheckBox
from javax.swing import JTextField
from javax.swing import BoxLayout
from java.awt import FlowLayout
from java.awt import Component
from java.awt import Toolkit
from java.awt.datatransfer import StringSelection


class MCPServerTab():
    def __init__(self, extender):
        self._extender = extender

    def draw(self):
        """ init the MCP Server tab """
        ext = self._extender

        ext.mcpEnabled = JCheckBox("Enable MCP Server", actionPerformed=self.toggle)

        ext.mcpPortField = JTextField("9877", 6)

        ext.mcpTokenField = JTextField("", 40)
        ext.mcpTokenField.setEditable(False)

        self.regenButton = JButton("Regenerate Token", actionPerformed=self.regenerate)
        self.copyButton = JButton("Copy Token", actionPerformed=self.copy_token)

        ext.mcpStatusLabel = JLabel("Stopped")

        info = JLabel("Loopback-only (127.0.0.1) MCP endpoint at POST /mcp. "
                      "Every request requires the header:  Authorization: Bearer <token>")

        pnl = JPanel()
        pnl.setLayout(BoxLayout(pnl, BoxLayout.Y_AXIS))

        def row(*components):
            r = JPanel(FlowLayout(FlowLayout.LEFT))
            r.setAlignmentX(Component.LEFT_ALIGNMENT)
            for c in components:
                r.add(c)
            pnl.add(r)
            return r

        row(ext.mcpEnabled)
        row(JLabel("Port:"), ext.mcpPortField)
        row(JLabel("Token:"), ext.mcpTokenField, self.regenButton, self.copyButton)
        row(JLabel("Status:"), ext.mcpStatusLabel)
        row(info)

        ext.mcpPnl = pnl

    def toggle(self, event):
        ext = self._extender
        mcp = getattr(ext, 'mcp', None)
        if ext.mcpEnabled.isSelected():
            try:
                port = int(ext.mcpPortField.getText().strip())
            except (ValueError, AttributeError):
                ext.mcpStatusLabel.setText("Invalid port")
                ext.mcpEnabled.setSelected(False)
                return
            if mcp is not None:
                mcp.start(port)
        else:
            if mcp is not None:
                mcp.stop()

    def regenerate(self, event):
        mcp = getattr(self._extender, 'mcp', None)
        if mcp is not None:
            mcp.regenerate_token()

    def copy_token(self, event):
        token = self._extender.mcpTokenField.getText()
        if token:
            clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
            clipboard.setContents(StringSelection(token), None)
