import socket
import threading
import json
import time

PORT = 5555  # Port used for networking
BUFFER_SIZE = 1024  # Packet size


class Multiplayer:
    def __init__(self, is_host=False, host_ip=None):
        self.is_host = is_host
        self.host_ip = host_ip
        self.players = {}  # {player_id: (x, y)}
        self.running = True
        self.player_id = None
        self.tcp_sock = None
        self.udp_sock = None

        if self.is_host:
            threading.Thread(target=self.host_server, daemon=True).start()
        else:
            threading.Thread(target=self.client_connect, daemon=True).start()

    def host_server(self):
        """Start the server for multiplayer hosting."""
        if self.tcp_sock:  # Prevent multiple instances
            print("[HOST] Server is already running!")
            return

        print("[HOST] Starting server...")

        try:
            self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse
            self.tcp_sock.bind(("0.0.0.0", PORT))
            self.tcp_sock.listen(5)

            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse
            self.udp_sock.bind(("0.0.0.0", PORT))

            print(f"[HOST] Server started on port {PORT}")

            threading.Thread(target=self.listen_for_clients,
                             daemon=True).start()
            self.listen_for_udp()

        except OSError as e:
            print(f"[ERROR] Failed to start server: {e}")
            self.stop_server()

    def listen_for_clients(self):
        """Handles new client connections."""
        while self.running:
            try:
                conn, addr = self.tcp_sock.accept()
                player_id = len(self.players) + 1
                conn.send(str(player_id).encode())
                print(f"[HOST] Player {player_id} connected from {addr}")
                self.players[player_id] = (70, 400)

                # Start a thread to listen for client disconnection
                threading.Thread(target=self.handle_client, args=(
                    conn, player_id), daemon=True).start()

            except OSError as e:
                print(f"[ERROR] Issue accepting client: {e}")
                break

    def handle_client(self, conn, player_id):
        """Handles client disconnection."""
        try:
            while self.running:
                if not conn.recv(1):  # If connection is closed
                    break
        except:
            pass
        finally:
            print(f"[HOST] Player {player_id} disconnected.")
            if player_id in self.players:
                del self.players[player_id]
            conn.close()

    def listen_for_udp(self):
        """Handles UDP data for real-time player updates."""
        while self.running:
            try:
                data, addr = self.udp_sock.recvfrom(BUFFER_SIZE)
                message = json.loads(data.decode())

                if message["type"] == "position":
                    self.players[message["id"]] = message["position"]

                # Send the updated positions back to all clients
                for player_id, pos in self.players.items():
                    self.udp_sock.sendto(json.dumps(
                        {"type": "update", "players": self.players}).encode(), addr)
            except OSError as e:
                print(f"[ERROR] UDP server error: {e}")
                break

    def stop_server(self):
        """Gracefully stops the server."""
        self.running = False
        if self.tcp_sock:
            self.tcp_sock.close()
            self.tcp_sock = None
        if self.udp_sock:
            self.udp_sock.close()
            self.udp_sock = None
        print("[HOST] Server stopped.")

    def client_connect(self):
        """Connect to a host's server."""
        try:
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_sock.connect((self.host_ip, PORT))

            self.player_id = int(tcp_sock.recv(BUFFER_SIZE).decode())
            print(f"[CLIENT] Connected as player {self.player_id}")

            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            while self.running:
                # Send player position to server
                udp_sock.sendto(json.dumps({"type": "position", "id": self.player_id, "position": (
                    70, 400)}).encode(), (self.host_ip, PORT))

                # Receive updated positions from server
                data, _ = udp_sock.recvfrom(BUFFER_SIZE)
                message = json.loads(data.decode())

                if message["type"] == "update":
                    self.players = message["players"]

                time.sleep(0.05)

        except Exception as e:
            print(f"[CLIENT] Failed to connect: {e}")
