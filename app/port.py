"""
File: port.py
Author: Dmitry Ryumin
Description: Utility functions to check and free ports by terminating processes holding them.
License: MIT License
"""

import socket
import psutil


def is_port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) == 0


def free_port(port: int) -> None:
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            for conn in proc.net_connections(kind="inet"):
                if conn.laddr.port == port:
                    proc.terminate()
                    proc.wait()
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
