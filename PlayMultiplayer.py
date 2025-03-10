from Network import Multiplayer
from Utilities import *
from GameLogic import *
import time
import random
import json
from Constants import *

# Define player colors to distinguish different players
PLAYER_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (128, 0, 128)   # Purple
]

# Global variables for synchronization
last_sync_time = 0
SYNC_INTERVAL = 0.2  # Sync every 200ms
PIPE_SPEED = 5  # Define the pipe speed explicitly for consistency


def play_multiplayer_logic(multiplayer):
    """
    Main multiplayer game loop for both host and client.
    Improved with better pipe synchronization.
    """
    global bird_movement, last_sync_time

    game_state = 'play_multiplayer'
    game_active = True
    score = 0
    current_time = time.time()

    if multiplayer is None:
        print("[ERROR] Multiplayer instance is not set! Returning to multiplayer menu.")
        return 'multiplayer menu', multiplayer

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            multiplayer.cleanup()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = -6  # Jump
            elif event.key == pygame.K_ESCAPE:
                game_state = 'multiplayer menu'
                return game_state, multiplayer

        # Host still manages pipe spawning on timer
        if event.type == SPAWNPIPE and multiplayer.is_host and multiplayer.game_started:
            new_pipes = create_pipe()
            new_pipe_data = [(p.x, p.y, p.width, p.height) for p in new_pipes]
            multiplayer.pipe_list.extend(new_pipe_data)

            # Force a broadcast of the new pipe list with EVERY pipe spawn
            pipe_message = {
                "type": "pipe_spawn",
                "id": multiplayer.player_id,
                "pipes": multiplayer.pipe_list,  # Send FULL pipe list, not just new pipes
                "timestamp": current_time
            }
            if multiplayer.udp_sock:
                multiplayer.udp_sock.sendto(
                    json.dumps(pipe_message).encode(),
                    (multiplayer.host_ip, PORT)
                )

    # Move background as usual
    move_background()

    # ----------------------------------------------------------------
    #  MAIN GAME LOGIC
    # ----------------------------------------------------------------
    if multiplayer.game_started and game_active:
        # Update the bird
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        # Check for out-of-bounds
        if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
            game_active = False

        # Tell the server our current position/score
        multiplayer.update_position(bird_rect.x, bird_rect.centery, score)

        # ------------------------
        # PIPE SYNCHRONIZATION LOGIC
        # ------------------------

        # Convert pipe_list from network data to Rects
        pipe_rects = [
            pygame.Rect(x, y, w, h)
            for (x, y, w, h) in multiplayer.pipe_list
        ]

        # Move pipes at the SAME speed for both host and client
        pipe_rects = [pipe.move(-PIPE_SPEED, 0) for pipe in pipe_rects]

        # Update the multiplayer pipe_list with new positions
        multiplayer.pipe_list = [
            (p.x, p.y, p.width, p.height) for p in pipe_rects
        ]

        # Host - periodically broadcast full pipe list to clients
        if multiplayer.is_host and (current_time - last_sync_time) > SYNC_INTERVAL:
            pipe_message = {
                "type": "pipe_sync",
                "id": multiplayer.player_id,
                "pipes": multiplayer.pipe_list,
                "timestamp": current_time
            }
            if multiplayer.udp_sock:
                multiplayer.udp_sock.sendto(
                    json.dumps(pipe_message).encode(),
                    (multiplayer.host_ip, PORT)
                )
            last_sync_time = current_time

        # Draw the pipes
        draw_pipes(pipe_rects)

        # Collision check for local bird
        if check_collision(pipe_rects) == False:
            game_active = False
            game_state = 'game_over'

        # Draw other players
        for pid, data in multiplayer.players.items():
            # Skip our own ID
            if pid != multiplayer.player_id and "position" in data:
                x_pos, y_pos = data["position"]
                color_idx = (int(pid) - 1) % len(PLAYER_COLORS)
                pygame.draw.circle(
                    SCREEN, PLAYER_COLORS[color_idx], (x_pos, y_pos), 20)
                label = font.render(str(pid), True, WHITE)
                SCREEN.blit(label, label.get_rect(center=(x_pos, y_pos)))

        # Draw our local bird
        SCREEN.blit(bird_image, bird_rect)

        # Player count
        player_count_surf = font.render(
            f"Players: {len(multiplayer.players)}", True, WHITE
        )
        SCREEN.blit(player_count_surf, (20, 20))

        # Increment local score
        score += 0.01
        display_score(score)

    else:
        # If the game hasn't started yet, or not active
        if not multiplayer.game_started:
            waiting_text = font.render(
                "Waiting for host to start game...", True, WHITE
            )
            SCREEN.blit(waiting_text, (WIDTH / 2 -
                        waiting_text.get_width() / 2, HEIGHT / 2))

            if multiplayer.is_host:
                start_button = pygame.Rect(
                    WIDTH / 2 - 100, HEIGHT / 2 + 50, 200, 50)
                pygame.draw.rect(SCREEN, GREEN, start_button, border_radius=10)
                start_text = font.render("Start Game", True, BLACK)
                SCREEN.blit(
                    start_text, (WIDTH / 2 -
                                 start_text.get_width() / 2, HEIGHT / 2 + 65)
                )
                mouse_pos = pygame.mouse.get_pos()
                mouse_clicked = pygame.mouse.get_pressed()[0]
                if start_button.collidepoint(mouse_pos) and mouse_clicked:
                    # Pre-generate all pipes before starting
                    if multiplayer.is_host and len(multiplayer.pipe_list) < 100:
                        # Make sure we have plenty of pipes ready
                        from Multiplayer import generate_initial_pipes
                        multiplayer.pipe_list = generate_initial_pipes(
                            pipe_count=50)

                    multiplayer.request_game_start()

            player_count = font.render(
                f"Connected Players: {len(multiplayer.players)}", True, WHITE
            )
            SCREEN.blit(
                player_count,
                (WIDTH / 2 - player_count.get_width() / 2, HEIGHT / 2 - 50),
            )

        elif not game_active:
            # Game over scenario
            game_over_text = font.render(
                f"Game Over! Your Score: {int(score)}", True, WHITE
            )
            SCREEN.blit(
                game_over_text,
                (WIDTH / 2 - game_over_text.get_width() / 2, HEIGHT / 2),
            )
            restart_text = font.render(
                "Press ESC to return to menu", True, WHITE
            )
            SCREEN.blit(
                restart_text,
                (WIDTH / 2 - restart_text.get_width() / 2, HEIGHT / 2 + 50),
            )

    return game_state, multiplayer


def convert_pipe_data(pipe_data):
    """
    Convert pipe data from network format to Pygame Rect objects.
    (Not strictly needed if you handle them in the main logic.)
    """
    pipes = []
    for pipe in pipe_data:
        x, y, width, height = pipe
        pipes.append(pygame.Rect(x, y, width, height))
    return pipes
