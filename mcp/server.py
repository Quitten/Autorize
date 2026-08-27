#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Loopback-only, token-authenticated HTTP JSON-RPC endpoint that speaks MCP.
#
# Implemented directly on java.net.ServerSocket (java.base) rather than
# com.sun.net.httpserver, because Burp's bundled/trimmed JRE does not include
# the jdk.httpserver module.
#
# Security model: the results table can hold live session cookies / Authorization
# headers, so the server binds to 127.0.0.1 only and requires a bearer token
# (generated with SecureRandom at start, held in memory only, never persisted).

import jarray

from java.net import ServerSocket, InetAddress
from java.util.concurrent import Executors
from java.security import SecureRandom, MessageDigest
from java.io import ByteArrayOutputStream, BufferedInputStream
from java.lang import String as JString
from java.lang import Thread as JThread
from java.lang import Runnable

DEFAULT_PORT = 9877

_REASONS = {
    200: "OK", 202: "Accepted", 400: "Bad Request", 401: "Unauthorized",
    404: "Not Found", 405: "Method Not Allowed", 500: "Internal Server Error",
}


def _generate_token():
    raw = jarray.zeros(32, 'b')
    SecureRandom().nextBytes(raw)
    return ''.join('%02x' % (b & 0xff) for b in raw)


def _tokens_equal(a, b):
    if a is None or b is None:
        return False
    return MessageDigest.isEqual(JString(a).getBytes("UTF-8"), JString(b).getBytes("UTF-8"))


def _read_line(ins):
    """Read one CRLF/LF-terminated line, returned as a python str (no line ending)."""
    buf = ByteArrayOutputStream()
    while True:
        b = ins.read()
        if b == -1:
            break
        if b == 0x0a:  # \n
            break
        if b != 0x0d:  # skip \r
            buf.write(b)
    return str(buf.toString("UTF-8"))


class _AcceptRunnable(Runnable):
    def __init__(self, server):
        self._server = server

    def run(self):
        self._server._accept_loop()


class _ClientRunnable(Runnable):
    def __init__(self, server, sock):
        self._server = server
        self._sock = sock

    def run(self):
        self._server._handle_socket(self._sock)


class McpServer:
    def __init__(self, extender):
        self.extender = extender
        self.port = DEFAULT_PORT
        self.token = None
        self._serversocket = None
        self._executor = None
        self._accept_thread = None
        self._stopping = False
        self._unauthorized_count = 0

    # -- lifecycle ---------------------------------------------------------

    def load_settings_and_maybe_autostart(self):
        self._set_status("Stopped")
        print("[Autorize MCP] server available (disabled by default).")

    def start(self, port=None):
        if self._serversocket is not None:
            self.stop()
        if port is None:
            port = self.port or DEFAULT_PORT
        self.port = port
        self.token = _generate_token()
        try:
            self._serversocket = ServerSocket(port, 50, InetAddress.getByName("127.0.0.1"))
            self._stopping = False
            self._executor = Executors.newFixedThreadPool(4)
            t = JThread(_AcceptRunnable(self))
            t.setDaemon(True)
            t.setName("Autorize-MCP-accept")
            t.start()
            self._accept_thread = t
        except Exception as e:
            self.token = None
            self._teardown_sockets()
            self._set_status("Error: %s" % e)
            self._set_enabled_checkbox(False)
            print("[Autorize MCP] failed to start on 127.0.0.1:%s: %s" % (port, e))
            return
        self._set_token_field(self.token)
        self._set_status("Running on 127.0.0.1:%d" % port)
        print("[Autorize MCP] server started on 127.0.0.1:%d" % port)

    def stop(self):
        self._stopping = True
        self._teardown_sockets()
        self.token = None
        self._set_token_field("")
        self._set_status("Stopped")
        print("[Autorize MCP] server stopped")

    def _teardown_sockets(self):
        if self._serversocket is not None:
            try:
                self._serversocket.close()  # unblocks accept()
            except Exception:
                pass
            self._serversocket = None
        if self._executor is not None:
            try:
                self._executor.shutdownNow()
            except Exception:
                pass
            self._executor = None
        self._accept_thread = None

    def regenerate_token(self):
        if self._serversocket is None:
            return
        self.token = _generate_token()
        self._set_token_field(self.token)
        print("[Autorize MCP] token regenerated")

    def is_running(self):
        return self._serversocket is not None

    # -- request handling --------------------------------------------------

    def _accept_loop(self):
        while not self._stopping:
            try:
                sock = self._serversocket.accept()
            except Exception:
                break  # socket closed on stop()
            try:
                self._executor.submit(_ClientRunnable(self, sock))
            except Exception:
                try:
                    sock.close()
                except Exception:
                    pass

    def _handle_socket(self, sock):
        try:
            ins = BufferedInputStream(sock.getInputStream())
            outs = sock.getOutputStream()

            request_line = _read_line(ins)
            if not request_line:
                return
            parts = request_line.split(" ")
            method = parts[0] if len(parts) > 0 else ""
            path = parts[1] if len(parts) > 1 else ""

            headers = {}
            while True:
                line = _read_line(ins)
                if line == "":
                    break
                idx = line.find(":")
                if idx > 0:
                    headers[line[:idx].strip().lower()] = line[idx + 1:].strip()

            # Honor Expect: 100-continue (curl uses it for larger bodies).
            if headers.get("expect", "").lower() == "100-continue":
                outs.write(JString("HTTP/1.1 100 Continue\r\n\r\n").getBytes("UTF-8"))
                outs.flush()

            content_length = 0
            try:
                content_length = int(headers.get("content-length", "0"))
            except ValueError:
                content_length = 0

            body_text = ""
            if content_length > 0:
                body = jarray.zeros(content_length, 'b')
                read = 0
                while read < content_length:
                    n = ins.read(body, read, content_length - read)
                    if n == -1:
                        break
                    read += n
                body_text = self.extender._helpers.bytesToString(body)

            if path.split("?")[0] != "/mcp":
                self._write(outs, 404, '{"error":"not found"}')
                return
            if method != "POST":
                self._write(outs, 405, '{"error":"method not allowed"}')
                return

            auth = headers.get("authorization")
            provided = None
            if auth and auth.startswith("Bearer "):
                provided = auth[7:].strip()
            if not _tokens_equal(provided, self.token):
                self._unauthorized_count += 1
                self._write(outs, 401,
                            '{"jsonrpc":"2.0","id":null,"error":{"code":-32001,"message":"unauthorized"}}')
                return

            from mcp.protocol import handle_request
            status, resp_text = handle_request(self, body_text)
            self._write(outs, status, resp_text)
        except Exception as e:
            print("[Autorize MCP] request error: %s" % e)
        finally:
            try:
                sock.close()
            except Exception:
                pass

    def _write(self, outs, status, text):
        reason = _REASONS.get(status, "OK")
        if text:
            body = JString(text).getBytes("UTF-8")
            length = len(body)
        else:
            body = None
            length = 0
        head = ("HTTP/1.1 %d %s\r\n"
                "Content-Type: application/json\r\n"
                "Content-Length: %d\r\n"
                "Connection: close\r\n\r\n") % (status, reason, length)
        outs.write(JString(head).getBytes("UTF-8"))
        if body is not None:
            outs.write(body)
        outs.flush()

    # -- UI helpers (safe if widgets not yet built) ------------------------

    def _set_status(self, text):
        label = getattr(self.extender, 'mcpStatusLabel', None)
        if label is not None:
            label.setText(text)

    def _set_token_field(self, text):
        field = getattr(self.extender, 'mcpTokenField', None)
        if field is not None:
            field.setText(text)

    def _set_enabled_checkbox(self, selected):
        box = getattr(self.extender, 'mcpEnabled', None)
        if box is not None:
            box.setSelected(selected)
