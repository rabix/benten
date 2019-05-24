#  Copyright (c) 2019 Seven Bridges. See LICENSE

import sys
import socketserver
import pathlib

from .configuration import Configuration

from benten.version import __version__
from benten.langserver.jsonrpc import JSONRPC2Connection, ReadWriter, TCPReadWriter
from benten.langserver.server import LangServer

from logging.handlers import RotatingFileHandler
import logging.config
import logging
logger = logging.getLogger()


# https://stackoverflow.com/a/47075664
# https://docs.python.org/3.6/library/socketserver.html#socketserver.ForkingMixIn
class ForkingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class LangserverTCPTransport(socketserver.StreamRequestHandler):

    config = None

    def handle(self):
        conn = JSONRPC2Connection(TCPReadWriter(self.rfile, self.wfile))
        s = LangServer(conn=conn, config=self.config)
        s.run()


def main():
    import argparse

    config = Configuration()

    log_fn = pathlib.Path(config.log_path, "benten-ls.log")
    roll_over = log_fn.exists()

    handler = RotatingFileHandler(log_fn, backupCount=5)
    formatter = logging.Formatter(
        fmt='[%(levelname)-7s] %(asctime)s (%(name)s) %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    if roll_over:
        handler.doRollover()

    # logging.basicConfig(filename=log_fn, filemode="w", level=logging.INFO)
    # logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="")
    parser.add_argument(
        "--mode", default="stdio", help="communication (stdio|tcp)")
    parser.add_argument(
        "--addr", default=4389, help="server listen (tcp)", type=int)
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--python_path")

    args = parser.parse_args()

    logging.basicConfig(level=(logging.DEBUG if args.debug else logging.WARNING))
    logger.addHandler(handler)

    logger.info(f"Benten {__version__}: CWL Language Server from Rabix (Seven Bridges)")

    config.initialize()

    if args.mode == "stdio":
        logger.info("Reading on stdin, writing on stdout")
        s = LangServer(
            conn=JSONRPC2Connection(ReadWriter(sys.stdin.buffer, sys.stdout.buffer)),
            config=config)
        s.run()
    elif args.mode == "tcp":
        host, addr = "0.0.0.0", args.addr
        logger.info("Accepting TCP connections on %s:%s", host, addr)
        ForkingTCPServer.allow_reuse_address = True
        ForkingTCPServer.daemon_threads = True
        LangserverTCPTransport.config = config
        s = ForkingTCPServer((host, addr), LangserverTCPTransport)
        try:
            s.serve_forever()
        finally:
            s.shutdown()


if __name__ == "__main__":
    main()
