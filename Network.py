import socket
import threading
import json
import time
import re  # Added for IP validation

PORT = 5555  # Port used for networking
BUFFER_SIZE = 8192  # Packet size


class Multiplayer:
    def __init__(self, is_host=False, host_ip=None):
        self.is_host = is_host
        self.host_ip = host_ip if not is_host else socket.gethostbyname(
            socket.gethostname())
        self.players = {}  # {player_id: {"position": (x, y), "score": 0}}
        self.running = True
        self.player_id = 1 if is_host else None  # Host is always player 1
        self.tcp_sock = None
        self.udp_sock = None
        self.pipe_list = []  # Stores synchronized pipes
        self.game_started = False
        self.connected_clients = 0
        self.client_ready = {}  # Track which clients are ready

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
            self.tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_sock.bind(("0.0.0.0", PORT))
            self.tcp_sock.listen(5)

            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_sock.bind(("0.0.0.0", PORT))

            # Automatically add host as Player 1
            self.players[1] = {"position": (70, 400), "score": 0}

            print(f"[HOST] Server started on {self.host_ip}:{PORT}")
            print(f"[HOST] Share this IP with other players: {self.host_ip}")

            threading.Thread(target=self.listen_for_clients,
                             daemon=True).start()
            threading.Thread(target=self.listen_for_udp, daemon=True).start()

        except OSError as e:
            print(f"[ERROR] Failed to start server: {e}")
            self.stop_server()

    def listen_for_clients(self):
        """Handles new client connections."""
        while self.running:
            try:
                conn, addr = self.tcp_sock.accept()
                player_id = len(self.players) + 1
                self.connected_clients += 1

                # Send the player their ID and current game state
                initial_data = {
                    "player_id": player_id,
                    "game_started": self.game_started,
                    "host_ip": self.host_ip
                }
                conn.send(json.dumps(initial_data).encode())

                print(f"[HOST] Player {player_id} connected from {addr}")
                self.players[player_id] = {"position": (70, 400), "score": 0}
                self.client_ready[player_id] = False

                # Broadcast player count update to all clients
                self.broadcast_player_count()

                # Start a thread to listen for client disconnection
                threading.Thread(target=self.handle_client, args=(
                    conn, player_id), daemon=True).start()

            except OSError as e:
                print(f"[ERROR] Issue accepting client: {e}")
                break

    def broadcast_player_count(self):
        """Send updated player count to all clients."""
        count_msg = json.dumps({
            "type": "player_count",
            "count": self.connected_clients
        }).encode()

        if self.udp_sock:
            for player_id in self.players:
                if player_id != 1:  # Don't send to host
                    try:
                        self.udp_sock.sendto(
                            count_msg, (self.players[player_id]["address"][0], PORT))
                    except KeyError:
                        pass  # Address not yet stored

    def listen_for_udp(self):
        """Handles UDP data for real-time player updates and pipe synchronization."""
        while self.running:
            try:
                data, addr = self.udp_sock.recvfrom(BUFFER_SIZE)
                message = json.loads(data.decode())

                # Store client address for sending updates
                if "id" in message and message["id"] in self.players:
                    self.players[message["id"]]["address"] = addr

                if message["type"] == "position":
                    player_id = message["id"]
                    if player_id in self.players:
                        self.players[player_id]["position"] = message["position"]

                        # If this is the host and game is in progress, update score
                        if self.is_host and self.game_started and "score" in message:
                            self.players[player_id]["score"] = message["score"]

                elif message["type"] == "ready":
                    player_id = message["id"]
                    self.client_ready[player_id] = message["ready"]
                    print(
                        f"[HOST] Player {player_id} ready status: {message['ready']}")

                elif message["type"] == "start_game" and self.is_host:
                    self.game_started = True
                    self.broadcast_game_start()
                    print("[HOST] Game started by host")

                elif message["type"] == "pipe_spawn" and self.is_host:
                    # Only host should manage pipes to keep them in sync
                    new_pipes = message["pipes"]
                    # Use extend instead of append to keep flat structure
                    self.pipe_list.extend(new_pipes)
                    self.broadcast_pipes()

                # Send updated game state to the client who sent this update
                self.send_game_state(addr)

            except Exception as e:
                print(f"[ERROR] UDP server error: {e}")
                continue  # Continue instead of breaking to maintain connection

    def send_game_state(self, addr):
        """Send current game state to a specific client."""
        try:
            state = {
                "type": "game_state",
                "players": self.players,
                "pipes": self.pipe_list,
                "game_started": self.game_started
            }
            self.udp_sock.sendto(json.dumps(state).encode(), addr)
        except Exception as e:
            print(f"[ERROR] Failed to send game state: {e}")

    def broadcast_game_start(self):
        """Notify all clients that the game has started and send the FULL pipe list."""
        start_msg = json.dumps({
            "type": "game_start",
            "pipes": self.pipe_list,  # Send the COMPLETE pipe list
            "timestamp": time.time()  # Include a timestamp for sync
        }).encode()

        if self.udp_sock:
            for player_id in self.players:
                # Skip host and clients without address
                if player_id != 1 and "address" in self.players[player_id]:
                    self.udp_sock.sendto(
                        start_msg, self.players[player_id]["address"])
            print("[HOST] Game start broadcast sent to all players with full pipe data")

    def broadcast_pipes(self):
        """Send updated pipes to all connected clients with timestamp."""
        pipe_msg = json.dumps({
            "type": "pipe_update",
            "pipes": self.pipe_list,
            "timestamp": time.time()  # Add timestamp for clients to sync with
        }).encode()

        if self.udp_sock:
            for player_id in self.players:
                # Skip host
                if player_id != 1 and "address" in self.players[player_id]:
                    self.udp_sock.sendto(
                        pipe_msg, self.players[player_id]["address"])

    def start_game(self):
        """Host tells all clients to start the game."""
        if self.is_host:
            self.game_started = True
            self.broadcast_game_start()
            return True
        return False

    def stop_server(self):
        """Gracefully shuts down the multiplayer server."""
        self.running = False
        if self.tcp_sock:
            self.tcp_sock.close()
            self.tcp_sock = None
        if self.udp_sock:
            self.udp_sock.close()
            self.udp_sock = None
        print("[HOST] Server stopped.")

    def handle_client(self, conn, player_id):
        """Handles client disconnection and cleanup."""
        try:
            while self.running:
                if not conn.recv(1):  # If the connection is lost
                    break
        except:
            pass
        finally:
            print(f"[HOST] Player {player_id} disconnected.")
            self.players.pop(player_id, None)  # Remove player safely
            self.client_ready.pop(player_id, None)
            self.connected_clients -= 1
            conn.close()
            self.broadcast_player_count()

    def client_connect(self):
        """Connect to a host's server and get assigned a player ID."""
        if self.player_id is not None:
            return  # Prevent reconnecting

        if not self.is_valid_ip(self.host_ip):
            print(f"[ERROR] Invalid IP format: {self.host_ip}")
            return

        try:
            self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_sock.connect((self.host_ip, PORT))

            # Receive player ID and initial game state
            initial_data = self.tcp_sock.recv(BUFFER_SIZE).decode()
            data = json.loads(initial_data)

            self.player_id = data["player_id"]
            self.game_started = data["game_started"]

            print(f"[CLIENT] Connected as player {self.player_id}")
            print(f"[CLIENT] Game in progress: {self.game_started}")

            # Initialize the UDP socket for game updates
            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # Start the thread to send and receive position updates
            threading.Thread(target=self.client_udp_loop, daemon=True).start()

        except Exception as e:
            print(f"[CLIENT] Failed to connect: {e}")
            self.player_id = None
            return False

        return True

    def client_udp_loop(self):
        """Client: continuously send position updates and listen for game state."""
        last_position_update = 0
        while self.running and self.player_id:
            try:
                current_time = time.time()

                # Send our position update (throttled to avoid flooding)
                if current_time - last_position_update > 0.05:  # 20 updates per second
                    if self.player_id is not None:
                        position_data = {
                            "type": "position",
                            "id": self.player_id,
                            "position": (70, 400),
                            "score": 0,
                            "timestamp": current_time
                        }
                        self.udp_sock.sendto(json.dumps(
                            position_data).encode(), (self.host_ip, PORT))
                        last_position_update = current_time

                # Try to receive game state updates
                self.udp_sock.settimeout(0.1)
                try:
                    data, _ = self.udp_sock.recvfrom(BUFFER_SIZE)
                    message = json.loads(data.decode())

                    if message["type"] == "game_state":
                        self.players = message["players"]
                        # Don't overwrite pipe list here, let pipe_update handle it
                        self.game_started = message["game_started"]

                    elif message["type"] == "game_start":
                        self.game_started = True
                        # On game start, fully replace our pipe list with the host's
                        self.pipe_list = message["pipes"]
                        print(
                            "[CLIENT] Game started by host! Received full pipe data.")

                    elif message["type"] in ["pipe_update", "pipe_sync", "pipe_spawn"]:
                        # For any pipe-related update, fully adopt the server's pipe list
                        server_pipes = message["pipes"]
                        # Complete replacement instead of interpolation for sync events
                        self.pipe_list = server_pipes
                        print(
                            f"[CLIENT] Received pipe update with {len(server_pipes)} pipes")

                    elif message["type"] == "player_count":
                        print(
                            f"[CLIENT] Players connected: {message['count']}")

                except socket.timeout:
                    pass  # No data received, continue

                time.sleep(0.01)  # Small sleep to prevent CPU overload

            except Exception as e:
                print(f"[CLIENT] UDP error: {e}")
                time.sleep(0.5)  # Wait before retrying
                continue

    def update_position(self, x, y, score=0):
        """Update current player's position to send to server."""
        if self.player_id and self.udp_sock:
            try:
                position_data = {
                    "type": "position",
                    "id": self.player_id,
                    "position": (x, y),
                    "score": score
                }
                self.udp_sock.sendto(json.dumps(
                    position_data).encode(), (self.host_ip, PORT))
            except Exception as e:
                print(f"[ERROR] Failed to send position update: {e}")

    def set_ready(self, ready_status):
        """Client tells server it's ready to start."""
        if self.player_id and self.udp_sock:
            try:
                ready_data = {
                    "type": "ready",
                    "id": self.player_id,
                    "ready": ready_status
                }
                self.udp_sock.sendto(json.dumps(
                    ready_data).encode(), (self.host_ip, PORT))
            except Exception as e:
                print(f"[ERROR] Failed to send ready status: {e}")

    def request_game_start(self):
        """Host requests to start the game."""
        if self.is_host and self.udp_sock:
            try:
                start_data = {
                    "type": "start_game",
                    "id": self.player_id
                }
                self.udp_sock.sendto(json.dumps(
                    start_data).encode(), (self.host_ip, PORT))
                return True
            except Exception as e:
                print(f"[ERROR] Failed to request game start: {e}")
                return False
        return False

    @staticmethod
    def is_valid_ip(ip):
        """Validates if the provided IP is in the correct format."""
        if not ip:
            return False
        return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip) is not None

    def get_player_count(self):
        """Returns the current number of players."""
        return len(self.players)

    def cleanup(self):
        """Clean up resources when the game exits."""
        print("[NETWORK] Cleaning up multiplayer resources...")
        self.running = False

        # Send a disconnect message if we're a client
        if not self.is_host and self.player_id is not None and self.udp_sock:
            try:
                disconnect_msg = json.dumps({
                    "type": "disconnect",
                    "id": self.player_id
                }).encode()
                self.udp_sock.sendto(disconnect_msg, (self.host_ip, PORT))
            except:
                pass  # Ignore errors during cleanup

        # Close all network resources
        if self.tcp_sock:
            try:
                self.tcp_sock.close()
            except:
                pass
            self.tcp_sock = None

        if self.udp_sock:
            try:
                self.udp_sock.close()
            except:
                pass
            self.udp_sock = None

        # Clear data structures
        self.pipe_list = []
        self.players = {}
        self.game_started = False

        print("[NETWORK] Cleanup completed")
