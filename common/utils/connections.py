"""Connection utils
"""
import logging
import socket
from contextlib import closing


def is_socket_open(socket_str: str):
    """Check availability of socket

    Args:
        socket (str): socket, with format `XX.XX.XX.XX:YYYY`

    Returns:
        bool

    """
    host, port = socket_str.split(":")
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        result = sock.connect_ex((host, int(port))) == 0
        if result:
            logging.info(f"Socket {host}:{port} is open")
        else:
            logging.warning(f"Socket {host}:{port} is not open")
    return result
