"""
Copyright (c) 2016 Sourcegraph
Copyright (c) 2019 Seven Bridges. See LICENSE

This code is assembled and reorganized
Retrieved from: https://github.com/sourcegraph/python-langserver/blob/master/langserver/jsonrpc.py

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import logging
import queue
import threading
from collections import deque

logger = logging.getLogger(__name__)


class JSONRPC2ProtocolError(Exception):
    pass


class ReadWriter:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    def readline(self, *args):
        return self.reader.readline(*args).decode("utf-8")

    def read(self, *args):
        return self.reader.read(*args).decode("utf-8")

    def write(self, out):
        self.writer.write(out.encode("utf-8"))
        self.writer.flush()


class TCPReadWriter(ReadWriter):
    def readline(self, *args):
        data = self.reader.readline(*args)
        return data.decode("utf-8")

    def read(self, *args):
        return self.reader.read(*args).decode("utf-8")

    def write(self, out):
        self.writer.write(out.encode())
        self.writer.flush()


class JSONRPC2Connection:
    def __init__(self, conn=None):
        self.conn = conn
        self._msg_buffer = deque()
        self._next_id = 1

    def _read_header_content_length(self, line):
        if len(line) < 2 or line[-2:] != "\r\n":
            raise JSONRPC2ProtocolError("Line endings must be \\r\\n")
        if line.startswith("Content-Length: "):
            _, value = line.split("Content-Length: ")
            value = value.strip()
            try:
                return int(value)
            except ValueError:
                raise JSONRPC2ProtocolError(
                    "Invalid Content-Length header: {}".format(value))

    def _receive(self):
        line = self.conn.readline()
        if line == "":
            raise EOFError()
        length = self._read_header_content_length(line)
        # Keep reading headers until we find the sentinel line for the JSON
        # request.
        while line != "\r\n":
            line = self.conn.readline()
        body = self.conn.read(length)
        logger.debug("RECV %s", body)
        return json.loads(body)

    def read_message(self, want=None):
        """Read a JSON RPC message sent over the current connection.
        If id is None, the next available message is returned.
        """
        if want is None:
            if self._msg_buffer:
                return self._msg_buffer.popleft()
            return self._receive()

        # First check if our buffer contains something we want.
        msg = deque_find_and_pop(self._msg_buffer, want)
        if msg:
            return msg

        # We need to keep receiving until we find something we want.
        # Things we don't want are put into the buffer for future callers.
        while True:
            msg = self._receive()
            if want(msg):
                return msg
            self._msg_buffer.append(msg)

    def _send(self, body):
        body = json.dumps(body, separators=(",", ":"))
        content_length = len(body)
        response = (
            "Content-Length: {}\r\n"
            "Content-Type: application/vscode-jsonrpc; charset=utf8\r\n\r\n"
            "{}".format(content_length, body))
        self.conn.write(response)
        logger.debug("SEND %s", body)

    def write_response(self, rid, result):
        body = {
            "jsonrpc": "2.0",
            "id": rid,
            "result": result,
        }
        self._send(body)

    def write_error(self, rid, code, message, data=None):
        e = {
            "code": code,
            "message": message,
        }
        if data is not None:
            e["data"] = data
        body = {
            "jsonrpc": "2.0",
            "id": rid,
            "error": e,
        }
        self._send(body)

    def send_request(self, method: str, params):
        rid = self._next_id
        self._next_id += 1
        body = {
            "jsonrpc": "2.0",
            "id": rid,
            "method": method,
            "params": params,
        }
        self._send(body)
        return self.read_message(want=lambda msg: msg.get("id") == rid)

    def send_notification(self, method: str, params):
        body = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
        }
        self._send(body)

    def send_request_batch(self, requests):
        """Pipelines requests and returns responses.
        The responses is a generator where the nth response corresponds
        with the nth request. Users must read the generator until the
        end, otherwise you will leak a thread.
        """

        # We communicate the request ids using a thread safe queue.
        # It also allows us to bound the number of concurrent requests.
        q = queue.Queue(100)

        def send():
            for method, params in requests:
                rid = self._next_id
                self._next_id += 1
                q.put(rid)
                body = {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "method": method,
                    "params": params,
                }
                self._send(body)

            # Sentinel value to indicate we are done
            q.put(None)

        threading.Thread(target=send).start()

        while True:
            rid = q.get()
            if rid is None:
                break
            yield self.read_message(want=lambda msg: msg.get("id") == rid)


def deque_find_and_pop(d, f):
    idx = None
    for i, v in enumerate(d):
        if f(v):
            idx = i
            break
    if idx is None:
        return None
    d.rotate(-idx)
    v = d.popleft()
    d.rotate(idx)
    return v
