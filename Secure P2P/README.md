A secure peer-to-peer (P2P) chat module implemented in Python. It allows users to communicate directly without storing messages on a central server. Local databases are used to store messages, and cryptography is utilized to secure communication between users.

Features
Secure message encryption using Fernet symmetric encryption.
Local SQLite database for storing messages.
Centralized server for user discovery and IP address management.
Keep-alive packets to maintain an up-to-date list of online users.
Users can block/unblock and mute/unmute other users.
Synchronization of messages with newly discovered users.
