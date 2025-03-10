import socket
import threading
import json
import time
import re

PORT = 5555
BUFFER_SIZE = 8192
MAX_UDP_PACKET_SIZE = 4096  # Safer UDP packet size limit


class Multiplayer:
    def __init__(self, is_host=False, host_ip=None):
        self.is_host = is_host
        self.host_ip = host_ip if not is_host else socket.gethostbyname(
            socket.gethostname())
        self.players = {}
        self.running = True
        self.player_id = 1 if is_host else None
        self.tcp_sock = None
        self.udp_sock = None
        self.pipe_list = []
        self.game_started = False
        self.connected_clients = 0
        self.client_ready = {}
        self.pipe_chunk_index = 0  # For tracking pipe data chunk sending

        if self.is_host:
            threading.Thread(target=self.host_server, daemon=True).start()
        else:
            threading.Thread(target=self.client_connect, daemon=True).start()

    def host_server(self):
        """Start the server for multiplayer hosting."""
        if self.tcp_sock:
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

                initial_data = {
                    "player_id": player_id,
                    "game_started": self.game_started,
                    "host_ip": self.host_ip
                }
                conn.send(json.dumps(initial_data).encode())

                print(f"[HOST] Player {player_id} connected from {addr}")
                self.players[player_id] = {"position": (
                    70, 400), "score": 0, "address": addr}
                self.client_ready[player_id] = False

                self.broadcast_player_count()

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
                if player_id != 1:
                    try:
                        self.udp_sock.sendto(
                            count_msg, (self.players[player_id]["address"][0], PORT))
                    except KeyError:
                        pass

    def listen_for_udp(self):
        """Handles UDP data for real-time player updates and pipe synchronization."""
        while self.running:
            try:
                data, addr = self.udp_sock.recvfrom(BUFFER_SIZE)
                message = json.loads(data.decode())

                if "id" in message and message["id"] in self.players:
                    self.players[message["id"]]["address"] = addr

                if message["type"] == "position":
                    player_id = message["id"]
                    if player_id in self.players:
                        self.players[player_id]["position"] = message["position"]

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
                    new_pipes = message["pipes"]
                    # Validate pipes to make sure they're not too close
                    if self.is_valid_pipe_placement(new_pipes):
                        self.pipe_list.extend(new_pipes)
                        self.broadcast_pipes(is_new=True)

                elif message["type"] == "request_pipes" and self.is_host:
                    # Client is requesting pipes, send the next chunk
                    client_chunk_index = message.get("chunk_index", 0)
                    self.send_pipe_chunk(addr, client_chunk_index)

                self.send_game_state(addr)

            except Exception as e:
                print(f"[ERROR] UDP server error: {e}")
                continue

    def is_valid_pipe_placement(self, new_pipes):
        """Check if the new pipes are valid (not too close to existing pipes)."""
        if not new_pipes:
            return True

        # Get X coordinates of existing pipes
        existing_x_coords = set()
        for pipe in self.pipe_list:
            existing_x_coords.add(pipe[0])  # X coordinate

        # Check if any new pipe is too close to existing pipes
        for pipe in new_pipes:
            pipe_x = pipe[0]
            for existing_x in existing_x_coords:
                if abs(pipe_x - existing_x) < 100:  # Minimum safe distance
                    return False

        return True

    def send_game_state(self, addr):
        """Send current game state to a specific client."""
        try:
            state = {
                "type": "game_state",
                "players": self.players,
                "game_started": self.game_started
            }
            # Don't include pipe data here to keep packet size small
            self.udp_sock.sendto(json.dumps(state).encode(), addr)
        except Exception as e:
            print(f"[ERROR] Failed to send game state: {e}")

    def send_pipe_chunk(self, addr, chunk_index):
        """Send a chunk of pipe data to avoid buffer overflow."""
        chunk_size = 20  # Number of pipes per chunk
        start_idx = chunk_index * chunk_size
        end_idx = min(start_idx + chunk_size, len(self.pipe_list))

        if start_idx >= len(self.pipe_list):
            # No more pipes to send
            return

        pipe_chunk = self.pipe_list[start_idx:end_idx]

        chunk_msg = json.dumps({
            "type": "pipe_chunk",
            "pipes": pipe_chunk,
            "chunk_index": chunk_index,
            "total_chunks": (len(self.pipe_list) + chunk_size - 1) // chunk_size,
            "timestamp": time.time()
        }).encode()

        try:
            if len(chunk_msg) <= MAX_UDP_PACKET_SIZE:
                self.udp_sock.sendto(chunk_msg, addr)
            else:
                print(
                    f"[WARNING] Pipe chunk too large ({len(chunk_msg)} bytes), reducing size")
                # Further reduce chunk size if needed
                smaller_chunk = self.pipe_list[start_idx:start_idx + chunk_size//2]
                smaller_msg = json.dumps({
                    "type": "pipe_chunk",
                    "pipes": smaller_chunk,
                    "chunk_index": chunk_index,
                    "total_chunks": (len(self.pipe_list) + chunk_size//2 - 1) // (chunk_size//2),
                    "timestamp": time.time()
                }).encode()
                self.udp_sock.sendto(smaller_msg, addr)
        except Exception as e:
            print(f"[ERROR] Failed to send pipe chunk: {e}")

    def broadcast_game_start(self):
        """Notify all clients that the game has started."""
        # Don't send full pipe list here, clients will request chunks
        start_msg = json.dumps({
            "type": "game_start",
            "pipe_count": len(self.pipe_list),
            "timestamp": time.time()
        }).encode()

        if self.udp_sock:
            for player_id in self.players:
                # Skip host and clients without address
                if player_id != 1 and "address" in self.players[player_id]:
                    self.udp_sock.sendto(
                        start_msg, (self.players[player_id]["address"][0], PORT))
            print("[HOST] Game start broadcast sent to all players")

    def broadcast_pipes(self, is_new=False):
        """Send signal that pipes have been updated."""
        notify_msg = json.dumps({
            "type": "pipes_updated",
            "is_new": is_new,
            "pipe_count": len(self.pipe_list),
            "timestamp": time.time()
        }).encode()

        if self.udp_sock:
            for player_id in self.players:
                if player_id != 1 and "address" in self.players[player_id]:
                    self.udp_sock.sendto(
                        notify_msg, (self.players[player_id]["address"][0], PORT))

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
                if not conn.recv(1):
                    break
        except:
            pass
        finally:
            print(f"[HOST] Player {player_id} disconnected.")
            self.players.pop(player_id, None)
            self.client_ready.pop(player_id, None)
            self.connected_clients -= 1
            conn.close()
            self.broadcast_player_count()

    def client_connect(self):
        """Connect to a host's server and get assigned a player ID."""
        if self.player_id is not None:
            return
        if not self.is_valid_ip(self.host_ip):
            print(f"[ERROR] Invalid IP format: {self.host_ip}")
            return

        try:
            self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_sock.connect((self.host_ip, PORT))

            initial_data = self.tcp_sock.recv(BUFFER_SIZE).decode()
            data = json.loads(initial_data)

            self.player_id = data["player_id"]
            self.game_started = data["game_started"]

            print(f"[CLIENT] Connected as player {self.player_id}")
            print(f"[CLIENT] Game in progress: {self.game_started}")

            self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            threading.Thread(target=self.client_udp_loop, daemon=True).start()

        except Exception as e:
            print(f"[CLIENT] Failed to connect: {e}")
            self.player_id = None
            return False

        return True

    def client_udp_loop(self):
        """Client: continuously send position updates and listen for game state."""
        last_position_update = 0
        last_pipe_request = 0
        current_pipe_chunk = 0
        total_pipe_chunks = 1

        while self.running and self.player_id:
            try:
                current_time = time.time()

                if current_time - last_position_update > 0.05:
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

                # Request pipe data periodically if needed
                if self.game_started and current_pipe_chunk < total_pipe_chunks:
                    if current_time - last_pipe_request > 0.2:
                        pipe_request = {
                            "type": "request_pipes",
                            "id": self.player_id,
                            "chunk_index": current_pipe_chunk
                        }
                        self.udp_sock.sendto(json.dumps(
                            pipe_request).encode(), (self.host_ip, PORT))
                        last_pipe_request = current_time

                self.udp_sock.settimeout(0.1)
                try:
                    data, _ = self.udp_sock.recvfrom(BUFFER_SIZE)
                    message = json.loads(data.decode())

                    if message["type"] == "game_state":
                        self.players = message["players"]
                        self.game_started = message["game_started"]

                    # In client_udp_loop() in Network.py
                    elif message["type"] == "game_start":
                        self.game_started = True
                        print("[CLIENT] Game started signal received from host!")
                        # Reset pipe chunk counters to start requesting chunks
                        current_pipe_chunk = 0
                        total_pipe_chunks = (message.get(
                            "pipe_count", 0) + 19) // 20

                    elif message["type"] == "pipe_chunk":
                        # Update the pipe chunk we're working with
                        chunk_pipes = message["pipes"]
                        chunk_index = message["chunk_index"]

                        # Merge this chunk into our pipe list
                        if chunk_index == 0:
                            # First chunk, reset the pipe list
                            self.pipe_list = chunk_pipes
                        else:
                            # Extend pipe list with new chunk
                            self.pipe_list.extend(chunk_pipes)

                        current_pipe_chunk = chunk_index + 1
                        total_pipe_chunks = message["total_chunks"]
                        print(
                            f"[CLIENT] Received pipe chunk {chunk_index+1}/{total_pipe_chunks} with {len(chunk_pipes)} pipes")

                    elif message["type"] == "pipes_updated":
                        # Host notifies that pipes have changed, need to request updates
                        if message.get("is_new", False):
                            # Only request the newest pipes (last chunk)
                            total_pipe_chunks = (message.get(
                                "pipe_count", 0) + 19) // 20
                            if total_pipe_chunks > 0:
                                current_pipe_chunk = total_pipe_chunks - 1
                                last_pipe_request = 0  # Request immediately

                    elif message["type"] == "player_count":
                        print(
                            f"[CLIENT] Players connected: {message['count']}")

                except socket.timeout:
                    pass

                time.sleep(0.01)

            except Exception as e:
                print(f"[CLIENT] UDP error: {e}")
                time.sleep(0.5)
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

        if not self.is_host and self.player_id is not None and self.udp_sock:
            try:
                disconnect_msg = json.dumps({
                    "type": "disconnect",
                    "id": self.player_id
                }).encode()
                self.udp_sock.sendto(disconnect_msg, (self.host_ip, PORT))
            except:
                pass

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
