import socket

class PortScanner:
    @staticmethod
    def is_port_available(host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex((host, port)) != 0

    @staticmethod
    def find_free_port(host: str, start_port: int, end_port: int) -> int:
        if PortScanner.is_port_available(host, start_port):
            return start_port

        for port in range(start_port + 1, end_port + 1):
            if PortScanner.is_port_available(host, port):
                return port
        raise RuntimeError("No free ports available in the specified range")
