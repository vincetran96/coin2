"""Connection utils
"""
import logging
import socket
from contextlib import closing


def is_socket_open(host: str, port: int):
    """Check availability of socket

    Returns:
        bool
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        result = sock.connect_ex((host, port)) == 0
        if result:
            logging.info(f"Socket {host}:{port} is open")
        else:
            logging.warning(f"Socket {host}:{port} is not open")
    return result
