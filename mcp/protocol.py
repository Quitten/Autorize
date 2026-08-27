#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Minimal MCP over JSON-RPC 2.0 (Streamable HTTP transport, non-streaming).
# Supports: initialize, notifications/initialized, ping, tools/list, tools/call.
# Stateless (no Mcp-Session-Id), no SSE, no batching.

import json

from mcp import tools as tools_module

PROTOCOL_VERSION = "2025-06-18"


def _error(msg_id, code, message):
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _result(msg_id, result):
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def handle_request(server, body_text):
    """Return (http_status, response_text). An empty response_text means no body."""
    if not body_text:
        return (400, json.dumps(_error(None, -32600, "empty request")))

    try:
        payload = json.loads(body_text)
    except Exception:
        return (400, json.dumps(_error(None, -32700, "parse error")))

    if isinstance(payload, list):
        return (400, json.dumps(_error(None, -32600, "batch requests are not supported")))
    if not isinstance(payload, dict):
        return (400, json.dumps(_error(None, -32600, "invalid request")))

    method = payload.get("method")
    msg_id = payload.get("id")
    params = payload.get("params") or {}

    if method == "notifications/initialized":
        return (202, "")

    if method is None:
        return (400, json.dumps(_error(msg_id, -32600, "missing method")))

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "autorize-mcp",
                           "version": getattr(server.extender, 'version', '')},
        }
        return (200, json.dumps(_result(msg_id, result)))

    if method == "ping":
        return (200, json.dumps(_result(msg_id, {})))

    if method == "tools/list":
        return (200, json.dumps(_result(msg_id, {"tools": tools_module.list_tools()})))

    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        handler = tools_module.get_handler(name)
        if handler is None:
            result = {"content": [{"type": "text", "text": "Unknown tool: %s" % name}],
                      "isError": True}
            return (200, json.dumps(_result(msg_id, result)))
        try:
            result_obj = handler(server, arguments)
            result = {"content": [{"type": "text", "text": json.dumps(result_obj)}],
                      "isError": False}
        except Exception as e:
            result = {"content": [{"type": "text", "text": "Error: %s" % str(e)}],
                      "isError": True}
        return (200, json.dumps(_result(msg_id, result)))

    # Unknown notification (no id) -> accept silently; unknown request -> error.
    if msg_id is None:
        return (202, "")
    return (200, json.dumps(_error(msg_id, -32601, "method not found: %s" % method)))
