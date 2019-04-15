from typing import Dict
from enum import IntEnum

from ..models.document import Document

import logging

logger = logging.getLogger(__name__)
logger.propagate = True


# https://stackoverflow.com/a/24482131
class LSPErrCode(IntEnum):
    # Defined by JSON RPC
    ParseError = -32700
    InvalidRequest = -32600
    MethodNotFound = -32601
    InvalidParams = -32602
    InternalError = -32603
    serverErrorStart = -32099
    serverErrorEnd = -32000
    ServerNotInitialized = -32002
    UnknownErrorCode = -32001

    # Defined by the protocol.
    RequestCancelled = -32800
    ContentModified = -32801


class JSONRPC2Error(Exception):
    def __init__(self, code, message, data=None):
        self.code = code
        self.message = message
        self.data = data


class ServerError(Exception):
    def __init__(self, server_error_message, json_rpc_error):
        self.server_error_message: str = server_error_message
        self.json_rpc_error: JSONRPC2Error = json_rpc_error


class CWLLangServerBase:
    def __init__(self, conn, config):
        self.conn = conn
        self.running = True
        self.root_path = None
        self.fs = None
        self.all_symbols = None
        self.workspace = None
        self.streaming = True

        self.open_documents: Dict[str, Document] = {}
        self.initialization_request_received = False

        self.client_capabilities = {}

        self.config = config
