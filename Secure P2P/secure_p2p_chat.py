import socket
import threading
import sqlite3
from cryptography.fernet import Fernet
import time

class SecureP2PChat:
    def __init__(self, username, discovery_server_ip, discovery_server_port):
        self.username = username
        self.discovery_server_ip = discovery_server_ip
        self.discovery_server_port = discovery_server_port
        self.peers = {}
        self.blocked_users = set()
        self.muted_users = {}
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect('local_data.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                               (chat_key text, sender text, message text, timestamp real)''')

    def generate_key(self):
        return Fernet.generate_key()

    def store_message(self, chat_key, sender, message):
        timestamp = time.time()
        self.cursor.execute("INSERT INTO messages VALUES (?, ?, ?, ?)", (chat_key, sender, message, timestamp))
        self.conn.commit()


    def send_message(self, chat_key, recipient, message):
        if recipient in self.blocked_users or recipient in self.muted_users:
            return

        encrypted_message = Fernet(chat_key).encrypt(message.encode())
        self.store_message(chat_key, self.username, message)

        recipient_ip, recipient_port = self.peers.get(recipient, (None, None))
        if recipient_ip and recipient_port:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((recipient_ip, recipient_port))
                s.sendall(encrypted_message)

    def listen_for_messages(self, ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ip, port))
            s.listen()

            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.handle_message, args=(conn, addr)).start()

    def handle_message(self, conn, addr):
        with conn:
            data = conn.recv(1024)
            for chat_key, (recipient, recipient_ip, recipient_port) in self.peers.items():
                if addr[0] == recipient_ip and addr[1] == recipient_port:
                    decrypted_message = Fernet(chat_key).decrypt(data).decode()
                    self.store_message(chat_key, recipient, decrypted_message)

    def block_user(self, user):
        self.blocked_users.add(user)

    def unblock_user(self, user):
        self.blocked_users.discard(user)

    def mute_user(self, user, duration):
        self.muted_users[user] = time.time() + duration

    def unmute_user(self, user):
        self.muted_users.pop(user, None)

    def check_muted_users(self):
        current_time = time.time()
        for user, mute_expiration in list(self.muted_users.items()):
            if mute_expiration <= current_time:
                self.unmute_user(user)


    def discover_peers(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.discovery_server_ip, self.discovery_server_port))
            s.sendall(f"DISCOVER:{self.username}".encode())
            data = s.recv(1024)
            self.update_peers(data.decode())

    def update_peers(self, data):
        lines = data.strip().split('\n')
        for line in lines:
            if not line:
                continue
            username, ip, port] = (ip, int(port))

    def send_keep_alive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.discovery_server_ip, self.discovery_server_port))
            s.sendall(f"KEEPALIVE:{self.username}".encode())

    def start(self, ip, port):
        threading.Thread(target=self.listen_for_messages, args=(ip, port)).start()
        threading.Thread(target=self.check_muted_users).start()
        while True:
            time.sleep(60)
            self.send_keep_alive()
            self.discover_peers()


