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
    global bird_movement  # For the local player's bird

    game_state = 'play_multiplayer'
    game_active = True
    score = 0

    if multiplayer is None:
        print("[ERROR] Multiplayer instance is not set! Returning to multiplayer menu.")
        return 'multiplayer menu', multiplayer

    # Initialize a persistent local pipe list (only for the client)
    if not hasattr(play_multiplayer_logic, "local_pipe_list"):
        play_multiplayer_logic.local_pipe_list = []

    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            multiplayer.cleanup()  # Properly cleanup network resources
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird_movement = -6  # Jump
            elif event.key == pygame.K_ESCAPE:
                game_state = 'multiplayer menu'
                return game_state, multiplayer
        # Only the host spawns new pipes
        if event.type == SPAWNPIPE and multiplayer.is_host and multiplayer.game_started:
            new_pipes = create_pipe()
            new_pipe_data = [(pipe.x, pipe.y, pipe.width, pipe.height)
                             for pipe in new_pipes]
            multiplayer.pipe_list.extend(new_pipe_data)
            pipe_message = {
                "type": "pipe_spawn",
                "id": multiplayer.player_id,
                "pipes": new_pipe_data
            }
            if multiplayer.udp_sock:
                multiplayer.udp_sock.sendto(json.dumps(
                    pipe_message).encode(), (multiplayer.host_ip, PORT))

    # Background movement
    move_background()

    # Game logic if game has started and we're active
    if multiplayer.game_started and game_active:
        # Bird physics
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        # Check for game over by screen bounds
        if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
            game_active = False

        # Update our position on the server
        multiplayer.update_position(bird_rect.x, bird_rect.centery, score)

        # --- Client-side pipe simulation ---
        # For clients, we use our persistent local copy rather than rebuilding
        # from the network state every frame.
        if not multiplayer.is_host:
            # If the network pipe list has changed (for example, new pipes spawned),
            # update our local copy.
            if multiplayer.pipe_list and (len(multiplayer.pipe_list) != len(play_multiplayer_logic.local_pipe_list)):
                play_multiplayer_logic.local_pipe_list = [pygame.Rect(x, y, w, h)
                                                          for (x, y, w, h) in multiplayer.pipe_list]
            # Otherwise, continue moving our local pipe list.
            if play_multiplayer_logic.local_pipe_list:
                play_multiplayer_logic.local_pipe_list = move_pipes(
                    play_multiplayer_logic.local_pipe_list)
                draw_pipes(play_multiplayer_logic.local_pipe_list)
            pipe_list = play_multiplayer_logic.local_pipe_list
        else:
            # For the host, rebuild the pipe list from the network state.
            pipe_list = []
            for pipe_data in multiplayer.pipe_list:
                if len(pipe_data) == 4:
                    x, y, width, height = pipe_data
                    pipe_list.append(pygame.Rect(x, y, width, height))
            if pipe_list:
                pipe_list = move_pipes(pipe_list)
                draw_pipes(pipe_list)
                # Host updates its own network state so future messages are current.
                multiplayer.pipe_list = [
                    (pipe.x, pipe.y, pipe.width, pipe.height) for pipe in pipe_list]

        # Collision detection using our chosen pipe list (local copy for client)
        if check_collision(pipe_list) == False:
            game_active = False
            game_state = 'game_over'

        # Draw other players' birds
        for player_id, data in multiplayer.players.items():
            if player_id != str(multiplayer.player_id) and "position" in data:
                pos = data["position"]
                color_idx = (int(player_id) - 1) % len(PLAYER_COLORS)
                color = PLAYER_COLORS[color_idx]
                pygame.draw.circle(SCREEN, color, (pos[0], pos[1]), 20)
                player_num = font.render(str(player_id), True, WHITE)
                num_rect = player_num.get_rect(center=(pos[0], pos[1]))
                SCREEN.blit(player_num, num_rect)

        # Draw our bird
        SCREEN.blit(bird_image, bird_rect)

        # Display player count
        player_count = font.render(
            f"Players: {len(multiplayer.players)}", True, WHITE)
        SCREEN.blit(player_count, (20, 20))

        # Increment score and display it
        if game_active:
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
                pygame.draw.rect(SCREEN, GREEN, start_button, border_radius=10)
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
