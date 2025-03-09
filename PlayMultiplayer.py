from Network import Multiplayer
from Utilities import *
from GameLogic import *
import pygame
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


def play_multiplayer_logic(multiplayer):
    global bird_movement

    game_state = 'play_multiplayer'
    game_active = True
    score = 0

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

        # Only the host spawns pipes
        if event.type == SPAWNPIPE and multiplayer.is_host and multiplayer.game_started:
            new_pipes = create_pipe()
            new_pipe_data = [(p.x, p.y, p.width, p.height) for p in new_pipes]
            multiplayer.pipe_list.extend(new_pipe_data)

            # Broadcast the new pipe data to clients
            pipe_message = {
                "type": "pipe_spawn",
                "id": multiplayer.player_id,
                "pipes": new_pipe_data
            }
            if multiplayer.udp_sock:
                multiplayer.udp_sock.sendto(
                    json.dumps(pipe_message).encode(),
                    (multiplayer.host_ip, PORT)
                )

    # Move background as usual
    move_background()

    # ---------------------
    #  MAIN GAME LOGIC
    # ---------------------
    if multiplayer.game_started and game_active:
        # Update the bird
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement
        if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
            game_active = False

        # Tell the server our current position/score
        multiplayer.update_position(bird_rect.x, bird_rect.centery, score)

        # HOST: move the pipes
        if multiplayer.is_host:
            # Convert pipe list from network data to Rects
            host_pipe_list = [
                pygame.Rect(x, y, w, h) for (x, y, w, h) in multiplayer.pipe_list
            ]
            # Move them on the HOST side only
            host_pipe_list = move_pipes(host_pipe_list)

            # Update the authoritative pipe_list
            multiplayer.pipe_list = [(p.x, p.y, p.width, p.height)
                                     for p in host_pipe_list]

            # Draw them
            draw_pipes(host_pipe_list)
            active_pipe_rects = host_pipe_list

        else:
            # CLIENT: just read and draw. DO NOT move them here!
            client_pipe_list = [
                pygame.Rect(x, y, w, h) for (x, y, w, h) in multiplayer.pipe_list
            ]
            draw_pipes(client_pipe_list)
            active_pipe_rects = client_pipe_list

        # Now that we have the final pipe Rects for this frame (host or client),
        # we can check collisions for our local bird
        if check_collision(active_pipe_rects) == False:
            game_active = False
            game_state = 'game_over'

        # Draw other players
        for pid, data in multiplayer.players.items():
            if pid != str(multiplayer.player_id) and "position" in data:
                x_pos, y_pos = data["position"]
                color_idx = (int(pid) - 1) % len(PLAYER_COLORS)
                pygame.draw.circle(
                    SCREEN, PLAYER_COLORS[color_idx], (x_pos, y_pos), 20)
                label = font.render(str(pid), True, WHITE)
                SCREEN.blit(label, label.get_rect(center=(x_pos, y_pos)))

        # Draw our bird
        SCREEN.blit(bird_image, bird_rect)

        # Player count
        player_count_surf = font.render(
            f"Players: {len(multiplayer.players)}", True, WHITE)
        SCREEN.blit(player_count_surf, (20, 20))

        # Increment local score
        score += 0.01
        display_score(score)

    else:
        # When game hasn't started or we're not active
        if not multiplayer.game_started:
            waiting_text = font.render(
                "Waiting for host to start game...", True, WHITE)
            SCREEN.blit(waiting_text, (WIDTH/2 -
                        waiting_text.get_width()/2, HEIGHT/2))
            if multiplayer.is_host:
                start_button = pygame.Rect(
                    WIDTH/2 - 100, HEIGHT/2 + 50, 200, 50)
                pygame.draw.rect(
                    SCREEN, GREEN, start_button, border_radius=10)
                start_text = font.render("Start Game", True, BLACK)
                SCREEN.blit(
                    start_text, (WIDTH/2 - start_text.get_width()/2, HEIGHT/2 + 65))
                mouse_pos = pygame.mouse.get_pos()
                mouse_clicked = pygame.mouse.get_pressed()[0]
                if start_button.collidepoint(mouse_pos) and mouse_clicked:
                    multiplayer.request_game_start()
            player_count = font.render(
                f"Connected Players: {len(multiplayer.players)}", True, WHITE)
            SCREEN.blit(player_count, (WIDTH/2 -
                        player_count.get_width()/2, HEIGHT/2 - 50))
        elif not game_active:
            game_over_text = font.render(
                f"Game Over! Your Score: {int(score)}", True, WHITE)
            SCREEN.blit(game_over_text, (WIDTH/2 -
                        game_over_text.get_width()/2, HEIGHT/2))
            restart_text = font.render(
                "Press ESC to return to menu", True, WHITE)
            SCREEN.blit(restart_text, (WIDTH/2 -
                        restart_text.get_width()/2, HEIGHT/2 + 50))

    return game_state, multiplayer


def convert_pipe_data(pipe_data):
    """Convert pipe data from network format to Pygame Rect objects."""
    pipes = []
    for pipe in pipe_data:
        x, y, width, height = pipe
        pipes.append(pygame.Rect(x, y, width, height))
    return pipes
