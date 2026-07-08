from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from threading import Event

from pygls.io_ import run_websocket

logger = logging.getLogger(__name__)


def start_persistent_ws(_server, host: str, port: int) -> None:
    """WebSocket LSP qui reste actif après la déconnexion d'un client."""
    try:
        from websockets.asyncio.server import serve
    except ImportError as error:
        raise SystemExit(
            "Le serveur WebSocket nécessite websockets.\n"
            "Installe-le avec : pip install -e '.[lsp]'"
        ) from error

    async def lsp_connection(websocket) -> None:
        from frlang.lsp.server import build_server

        connection_server = build_server()
        stop_event = Event()
        logger.debug("Client LSP connecté")
        try:
            await run_websocket(
                stop_event=stop_event,
                websocket=websocket,
                protocol=connection_server.protocol,
                logger=logger,
                error_handler=connection_server.report_server_error,
            )
        finally:
            logger.debug("Client LSP déconnecté")
            connection_server.shutdown()

    async def ws_server() -> None:
        async with serve(lsp_connection, host, port) as ws_server_instance:
            addrs = ", ".join(str(sock.getsockname()) for sock in ws_server_instance.sockets)
            logger.info("Serveur LSP WebSocket sur %s", addrs)
            await asyncio.Future()

    logger.info("Démarrage du serveur LSP WebSocket sur %s:%s", host, port)
    try:
        asyncio.run(ws_server())
    except (KeyboardInterrupt, SystemExit):
        pass


def parse_ws_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serveur LSP FrLang (WebSocket persistant)")
    parser.add_argument("--host", default="127.0.0.1", help="Adresse d'écoute")
    parser.add_argument("--port", type=int, default=8765, help="Port d'écoute")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_ws_args(argv)
    # Le serveur LSP est instancié par connexion WebSocket.
    start_persistent_ws(None, args.host, args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
