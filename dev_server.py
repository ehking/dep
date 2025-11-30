"""Development HTTP server with friendly TLS-handshake handling.

Running ``python -m http.server`` can log a stream of ``400 Bad request version``
errors when a browser (or background service) accidentally opens an HTTPS
connection to the HTTP port. This module provides a small wrapper around
``ThreadingHTTPServer`` that detects TLS handshakes on the wrong port and
logs a concise hint instead of emitting noisy 400 errors.
"""

from __future__ import annotations

import argparse
import socket
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Tuple


def _looks_like_tls_handshake(data: bytes) -> bool:
    """Return ``True`` if the first bytes match a TLS/SSL handshake prefix.

    The leading ``0x16 0x03`` pattern is present on TLS ClientHello messages
    regardless of the minor version; the second prefix captures some legacy
    probes that start with a two-byte record length.
    """

    return data.startswith((b"\x16\x03", b"\x00\x02\x01\x00"))


class FriendlyHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP handler that ignores TLS handshakes on the HTTP port."""

    server_version = "FriendlyHTTP/1.0"

    def handle_one_request(self) -> None:  # noqa: WPS213
        try:
            self.raw_requestline = self.rfile.readline(65537)
        except (ConnectionResetError, socket.timeout) as exc:
            self.log_error("request line read failed: %s", exc)
            self.close_connection = True
            return

        if not self.raw_requestline:
            self.close_connection = True
            return

        if _looks_like_tls_handshake(self.raw_requestline):
            self.log_message("ignored TLS handshake on HTTP port; use https:// or plain http://")
            self.close_connection = True
            return

        if not self.parse_request():
            return

        mname = "do_" + self.command
        if not hasattr(self, mname):
            self.send_error(501, f"Unsupported method ({self.command!r})")
            return

        method = getattr(self, mname)
        method()
        self.wfile.flush()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the demo UI without TLS noise.")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument(
        "--directory",
        default=".",
        help="Directory to serve (default: current working directory)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    handler_factory = partial(FriendlyHTTPRequestHandler, directory=args.directory)
    address: Tuple[str, int] = ("0.0.0.0", args.port)

    with ThreadingHTTPServer(address, handler_factory) as httpd:
        print(f"Serving {args.directory!r} on http://{address[0]}:{address[1]} (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped by user.")


if __name__ == "__main__":
    main()
