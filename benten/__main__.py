import sys
import socketserver
import pathlib

import benten
from benten.langserver.jsonrpc import JSONRPC2Connection, ReadWriter, TCPReadWriter
from benten.langserver.server import LangServer

import logging
logger = logging.getLogger(__name__)


class ForkingTCPServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass


class LangserverTCPTransport(socketserver.StreamRequestHandler):
    def handle(self):
        conn = JSONRPC2Connection(TCPReadWriter(self.rfile, self.wfile))
        s = LangServer(conn)
        s.run()


def main():
    import argparse

    log_fn = pathlib.Path(benten.config_dir, "benten-ls.log")
    logging.basicConfig(filename=log_fn, filemode="w", level=logging.INFO)

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--mode", default="stdio", help="communication (stdio|tcp)")
    parser.add_argument(
        "--addr", default=4389, help="server listen (tcp)", type=int)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--python_path")

    args = parser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.debug else logging.INFO))

    if args.mode == "stdio":
        logging.info("Reading on stdin, writing on stdout")
        s = LangServer(conn=JSONRPC2Connection(ReadWriter(sys.stdin.buffer, sys.stdout.buffer)))
        s.run()
    elif args.mode == "tcp":
        host, addr = "0.0.0.0", args.addr
        logging.info("Accepting TCP connections on %s:%s", host, addr)
        ForkingTCPServer.allow_reuse_address = True
        ForkingTCPServer.daemon_threads = True
        s = ForkingTCPServer((host, addr), LangserverTCPTransport)
        try:
            s.serve_forever()
        finally:
            s.shutdown()


if __name__ == "__main__":
    main()