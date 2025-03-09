import socket
import threading
import json
import time

# Network Constants
PORT = 5555  # Port to use for networking
BUFFER_SIZE = 1024  # Packet size


class Multiplayer:
    def __init__(self, is_host=False, host_ip=None):
        self.is_host = is_host
        self.host_ip = host_ip
        self.players = {}
        self.pipes = []
        self.running = True

        if self.is_host:
            threading.Thread(target=self.host_server, daemon=True).start()
        else:
            threading.Thread(target=self.client_connect, daemon=True).start()

    def host_server(self):
        """Start the server for multiplayer."""
        print("[HOST] Starting game server...")

        # Create a TCP socket (reliable connection for initial setup)
        tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_sock.bind(("0.0.0.0", PORT))
        tcp_sock.listen(5)

        # UDP Socket (for fast position updates)
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(("0.0.0.0", PORT))

        print(f"[HOST] Server started on port {PORT}")

        def listen_for_clients():
            while self.running:
                try:
                    conn, addr = tcp_sock.accept()
                    print(f"[HOST] Player connected: {addr}")
                    threading.Thread(target=self.handle_client,
                                     args=(conn,), daemon=True).start()
                except:
                    break

        threading.Thread(target=listen_for_clients, daemon=True).start()

        while self.running:
            try:
                data, addr = udp_sock.recvfrom(BUFFER_SIZE)
                message = json.loads(data.decode())

                if message["type"] == "position":
                    self.players[message["id"]] = message["position"]

                for player_id, pos in self.players.items():
                    udp_sock.sendto(json.dumps(
                        {"type": "update", "players": self.players}).encode(), addr)
            except:
                break

    def handle_client(self, conn):
        """Handle new player connections."""
        try:
            player_id = len(self.players) + 1
            conn.send(str(player_id).encode())

            while self.running:
                data = conn.recv(BUFFER_SIZE).decode()
                if not data:
                    break
                message = json.loads(data)

                if message["type"] == "player_joined":
                    self.players[message["id"]] = (
                        70, 400)

            conn.close()
        except:
            pass

    def client_connect(self):
        """Connect to a host server."""
        try:
            tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_sock.connect((self.host_ip, PORT))

            player_id = int(tcp_sock.recv(BUFFER_SIZE).decode())
            print(f"[CLIENT] Connected as player {player_id}")

            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            while self.running:
                udp_sock.sendto(json.dumps({"type": "position", "id": player_id, "position": (
                    70, 400)}).encode(), (self.host_ip, PORT))

                data, _ = udp_sock.recvfrom(BUFFER_SIZE)
                message = json.loads(data.decode())

                if message["type"] == "update":
                    self.players = message["players"]

                time.sleep(0.05)
        except:
            print("[CLIENT] Failed to connect")
