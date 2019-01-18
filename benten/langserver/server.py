from typing import Dict
import pathlib
from enum import IntEnum

import benten
import benten.langserver.configuration as cfg
import benten.langserver.cwldocument as cwldoc


import logging
logger = logging.getLogger(__name__)


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


class LangServer:
    def __init__(self, conn):
        self.conn = conn
        self.running = True
        self.root_path = None
        self.fs = None
        self.all_symbols = None
        self.workspace = None
        self.streaming = True

        self.open_documents: Dict[str, cwldoc.CwlDocument] = {}
        self.initialization_request_received = False

        self.client_capabilities = {}

        self.configuration = cfg.Configuration(benten.config_dir)

        logger.info("Starting up ...")

    def run(self):
        while self.running:
            try:
                request = self.conn.read_message()
                self.handle(request)
            except EOFError:
                break
            except Exception as e:
                logger.error("Unexpected error: %s", e, exc_info=True)

    # Request message:
    # {
    # 	"jsonrpc": "2.0",
    # 	"id": 1, # <----------  if this field is missing, it's a notification
    #                       	and should not receive a response. Otherwise,
    #                           the response should carry this id for accounting
    #                           purposes
    # 	"method": "...",
    # 	"params": {
    # 		...
    # 	}
    # }
    def handle(self, client_query):
        logger.info("Request: {}".format(client_query))

        is_a_request = "id" in client_query

        if self.premature_request(client_query, is_a_request):
            return

        if self.duplicate_initialization(client_query, is_a_request):
            return

        try:
            response = {
                "initialize": self.serve_initialize,
                "initialized": self.serve_ignore,
                "textDocument/didOpen": self.serve_doc_did_open,
                "textDocument/didChange": self.serve_doc_did_change,
                "textDocument/completion": self.serve_completion,
                "textDocument/hover": self.serve_hover,
                "textDocument/codeAction": self.serve_available_commands,
                # "textDocument/definition": self.serve_definition,
                # "textDocument/xdefinition": self.serve_x_definition,
                # "textDocument/references": self.serve_references,
                # "workspace/xreferences": self.serve_x_references,
                # "textDocument/documentSymbol": self.serve_document_symbols,
                # "workspace/symbol": self.serve_symbols,
                # "workspace/xpackages": self.serve_x_packages,
                # "workspace/xdependencies": self.serve_x_dependencies,
                "$/cancelRequest": self.serve_ignore,
                "shutdown": self.serve_ignore,
                "exit": self.serve_exit,
            }.get(client_query["method"], self.serve_unknown)(client_query)

            if is_a_request:
                self.conn.write_response(client_query["id"], response)

        except ServerError as e:
            logger.error(e.server_error_message)

            if is_a_request:
                self.conn.write_error(
                    client_query["id"],
                    code=e.json_rpc_error.code,
                    message=str(e.json_rpc_error.message),
                    data=e.json_rpc_error.data)

    def premature_request(self, client_query, is_a_request):
        if not self.initialization_request_received and \
                client_query.get("method", None) not in ["initialize", "exit"]:
            logger.warning("Client sent a request/notification without initializing")
            if is_a_request:
                self.conn.write_error(
                    client_query["id"],
                    code=LSPErrCode.ServerNotInitialized,
                    message="",
                    data={})
            return True
        else:
            return False

    def duplicate_initialization(self, client_query, is_a_request):
        if self.initialization_request_received and client_query.get("method", None) == "initialize":
            logger.warning("Client sent duplicate initialization")
            if is_a_request:
                self.conn.write_error(
                    client_query["id"],
                    code=LSPErrCode.InvalidRequest,
                    message="Client sent duplicate initialization",
                    data={})
            return True
        else:
            return False

    @staticmethod
    def serve_unknown(client_query):
        msg = "Unknown method: {}".format(client_query["method"])
        raise ServerError(
            server_error_message=msg,
            json_rpc_error=JSONRPC2Error(
                code=LSPErrCode.MethodNotFound,
                message=msg))

    @staticmethod
    def serve_ignore(client_query):
        return None

    # https://microsoft.github.io/language-server-protocol/specification#initialize
    def serve_initialize(self, client_query):
        self.initialization_request_received = True

        self.client_capabilities = client_query.get("capabilities", {})

        return {
            "capabilities": {
                "textDocumentSync": 2,  # Incremental
                "completionProvider": {
                    "resolveProvider": True,
                    "triggerCharacters": []
                },
                "hoverProvider": True,
                "definitionProvider": True,
                "referencesProvider": True,
                "documentSymbolProvider": True,
                "workspaceSymbolProvider": True,
                "streaming": True,
                "xdefinitionProvider": True,
                "xworkspaceReferencesProvider": True,
            }
        }

    def serve_exit(self, client_query):
        logging.shutdown()
        self.running = False

    # https://microsoft.github.io/language-server-protocol/specification#textDocument_didOpen
    # The document open notification is sent from the client to the server to signal newly opened text documents. The
    # document’s truth is now managed by the client and the server must not try to read the document’s truth using
    # the document’s Uri. Open in this sense means it is managed by the client. It doesn’t necessarily mean that its
    # content is presented in an editor. An open notification must not be sent more than once without a corresponding
    # close notification send before. This means open and close notification must be balanced and the max open count
    # for a particular textDocument is one. Note that a server’s ability to fulfill requests is independent of
    # whether a text document is open or closed.

    # Notes:
    # Multiple documents can be open at the same time. We need to keep track of this.
    def serve_doc_did_open(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]
        if doc_uri in self.open_documents:
            msg = "Document {} duplicated open".format(doc_uri)
            raise ServerError(
                server_error_message=msg,
                json_rpc_error=JSONRPC2Error(
                    code=LSPErrCode.InvalidRequest,
                    message=msg))

        self.open_documents[doc_uri] = cwldoc.CwlDocument(
            base_path=pathlib.Path(doc_uri),
            raw_cwl=params["textDocument"]["text"],
            version=params["textDocument"]["version"],
            configuration=self.configuration
        )

    def serve_doc_did_change(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]

        if doc_uri not in self.open_documents:
            msg = "No such document {} referred to in change".format(doc_uri)
            raise ServerError(
                server_error_message=msg,
                json_rpc_error=JSONRPC2Error(
                    code=LSPErrCode.InvalidRequest,
                    message=msg))

        self.open_documents[doc_uri].did_change(
            changed_text=params["contentChanges"][0]["text"],
            version=params["textDocument"]["version"]
        )

    def serve_completion(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]

        if doc_uri not in self.open_documents:
            msg = "No such document {} referred to in change".format(doc_uri)
            raise ServerError(
                server_error_message=msg,
                json_rpc_error=JSONRPC2Error(
                    code=LSPErrCode.InvalidRequest,
                    message=msg))

        return self.open_documents[doc_uri].auto_complete(
            line=params["position"]["line"],
            character=params["position"]["character"]
        )

    def serve_hover(self, client_query):
        return {}

    def serve_available_commands(self, client_query):
        return {}
