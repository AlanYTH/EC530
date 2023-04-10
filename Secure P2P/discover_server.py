import socket
import threading

class DiscoveryServer:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.users = {}

    def handle_client(self, conn, addr):
        with conn:
            data = conn.recv(1024).decode()
            cmd, username = data.split(":", 1)

            if cmd == "DISCOVER":
                response = "\n".join(f"{user}:{ip}:{port}" for user, (ip, port) in self.users.items())
                conn.sendall(response.encode())

            elif cmd == "KEEPALIVE":
                self.users[username] = addr

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.ip, self.port))
            s.listen()

            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    discovery_server = DiscoveryServer("0.0.0.0", 8000)
    discovery_server.start()
