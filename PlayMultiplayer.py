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
    pipe_list = []  # Local copy, will be updated by network
    score = 0

    if multiplayer is None:
        print("[ERROR] Multiplayer instance is not set! Returning to multiplayer menu.")
        return 'multiplayer menu', multiplayer

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
                # Allow players to exit back to the menu
                game_state = 'multiplayer menu'
                return game_state, multiplayer

        # Check if it's time to spawn a pipe (only host manages pipe creation)
        if event.type == SPAWNPIPE and multiplayer.is_host and multiplayer.game_started:
            new_pipes = create_pipe()
            # Update the host’s own pipe list directly
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

    # Game logic
    if multiplayer.game_started and game_active:
        # Handle physics for our bird
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        # Check for game over condition
        if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
            game_active = False

        # Update our position on the server
        multiplayer.update_position(bird_rect.x, bird_rect.centery, score)

        # Get pipe list from multiplayer
        # Get pipe list from multiplayer
        if multiplayer.pipe_list:
            pipe_list = []
            for pipe_data in multiplayer.pipe_list:
                if len(pipe_data) == 4:
                    x, y, width, height = pipe_data
                    pipe_list.append(pygame.Rect(x, y, width, height))

        # Only move pipes if host has started the game
        if pipe_list:
            pipe_list = move_pipes(pipe_list)
            draw_pipes(pipe_list)
            # If we're the host, update the network state with new positions.
            if multiplayer.is_host:
                multiplayer.pipe_list = [
                    (pipe.x, pipe.y, pipe.width, pipe.height) for pipe in pipe_list]

        # Check for collisions with pipes
        if check_collision(pipe_list) == False:
            game_active = False
            game_state = 'game_over'

        # Draw all other players' birds
        for player_id, data in multiplayer.players.items():
            if player_id != str(multiplayer.player_id) and "position" in data:
                pos = data["position"]
                color_idx = (int(player_id) - 1) % len(PLAYER_COLORS)
                color = PLAYER_COLORS[color_idx]

                # Draw other player birds (simple circle with player number)
                pygame.draw.circle(SCREEN, color, (pos[0], pos[1]), 20)

                # Display player number
                player_num = font.render(str(player_id), True, WHITE)
                num_rect = player_num.get_rect(center=(pos[0], pos[1]))
                SCREEN.blit(player_num, num_rect)

        # Draw our bird
        SCREEN.blit(bird_image, bird_rect)

        # Display player count
        player_count = font.render(
            f"Players: {len(multiplayer.players)}", True, WHITE)
        SCREEN.blit(player_count, (20, 20))

        # Increment score (only while actively playing)
        if game_active:
            score += 0.01
            display_score(score)

    else:
        # Display "waiting for host" message if game hasn't started
        if not multiplayer.game_started:
            waiting_text = font.render(
                "Waiting for host to start game...", True, WHITE)
            SCREEN.blit(waiting_text, (WIDTH/2 -
                        waiting_text.get_width()/2, HEIGHT/2))

            # If host, display start button
            if multiplayer.is_host:
                start_button = pygame.Rect(
                    WIDTH/2 - 100, HEIGHT/2 + 50, 200, 50)
                pygame.draw.rect(SCREEN, GREEN, start_button, border_radius=10)
                start_text = font.render("Start Game", True, BLACK)
                SCREEN.blit(
                    start_text, (WIDTH/2 - start_text.get_width()/2, HEIGHT/2 + 65))

                # Check for button click
                mouse_pos = pygame.mouse.get_pos()
                mouse_clicked = pygame.mouse.get_pressed()[0]
                if start_button.collidepoint(mouse_pos) and mouse_clicked:
                    multiplayer.request_game_start()

            # Show connected players count
            player_count = font.render(
                f"Connected Players: {len(multiplayer.players)}", True, WHITE)
            SCREEN.blit(player_count, (WIDTH/2 -
                        player_count.get_width()/2, HEIGHT/2 - 50))

        # If game over, allow returning to menu
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
