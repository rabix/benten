"""
https://microsoft.github.io/language-server-protocol/specification#textDocument_didOpen

The document open notification is sent from the client to the server to signal
newly opened text documents. The document’s truth is now managed by the client
and the server must not try to read the document’s truth using the document’s Uri.
Open in this sense means it is managed by the client. It doesn’t necessarily
mean that its content is presented in an editor. An open notification must
not be sent more than once without a corresponding close notification send
before. This means open and close notification must be balanced and the max
open count for a particular textDocument is one. Note that a server’s ability
to fulfill requests is independent of whether a text document is open or closed.

Notes:
Multiple documents can be open at the same time. We need to keep track of this.

interface TextDocumentItem {
    /**
     * The text document's URI.
     */
    uri: DocumentUri;

    /**
     * The text document's language identifier.
     */
    languageId: string;

    /**
     * The version number of this document (it will increase after each
     * change, including undo/redo).
     */
    version: number;

    /**
     * The content of the opened text document.
     */
    text: string;
}
"""
import pathlib

from .base import CWLLangServerBase
from ..models.document import Document


class DidOpen(CWLLangServerBase):

    def serve_textDocument_didOpen(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]

        self.open_documents[doc_uri] = Document(
            base_path=pathlib.Path(doc_uri),
            text=params["textDocument"]["text"],
            version=params["textDocument"]["version"])
