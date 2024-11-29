import socket

class PortManager:
    @staticmethod
    def is_port_available(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0

    @staticmethod
    def find_free_port(start_port: int, end_port: int) -> int:
        if PortManager.is_port_available(start_port):
            return start_port

        for port in range(start_port + 1, end_port + 1):
            if PortManager.is_port_available(port):
                return port
        raise RuntimeError("No free ports available in the specified range")