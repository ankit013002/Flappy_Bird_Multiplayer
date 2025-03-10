from Network import Multiplayer
from Utilities import *
from GameLogic import *
import time
import random
import json
from Constants import *

PLAYER_COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (255, 165, 0),
    (128, 0, 128)
]

last_sync_time = 0
SYNC_INTERVAL = 0.5  # Reduced frequency of updates
PIPE_SPEED = 5
MIN_PIPE_SPACING = 300  # Minimum x-distance between pipes


def play_multiplayer_logic(multiplayer):
    """
    Main multiplayer game loop for both host and client.
    Improved with better pipe synchronization and spacing guarantees.
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

        # Only spawn new pipes if we're the host and if there aren't too many pipes
        if event.type == SPAWNPIPE and multiplayer.is_host and multiplayer.game_started:
            if len(multiplayer.pipe_list) < 100:  # Limit total pipes for performance
                new_pipes = create_pipe()

                # Only add new pipes if they're not too close to existing pipes
                if is_safe_pipe_placement(multiplayer.pipe_list, new_pipes):
                    new_pipe_data = [(p.x, p.y, p.width, p.height)
                                     for p in new_pipes]
                    multiplayer.pipe_list.extend(new_pipe_data)
                else:
                    print(
                        "[HOST] Skipped adding pipes that were too close to existing pipes")

    move_background()

    if multiplayer.game_started and game_active:
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
            game_active = False

        multiplayer.update_position(bird_rect.x, bird_rect.centery, score)

        # Create pipe rects from the pipe data
        pipe_rects = []
        for pipe_data in multiplayer.pipe_list:
            if len(pipe_data) == 4:
                x, y, w, h = pipe_data
                pipe_rects.append(pygame.Rect(x, y, w, h))

        # Move pipes and update the pipe list
        if pipe_rects:
            moved_pipe_rects = [pipe.move(-PIPE_SPEED, 0)
                                for pipe in pipe_rects]

            # Remove pipes that are off-screen
            visible_pipe_rects = [p for p in moved_pipe_rects if p.right > -50]

            # Update the multiplayer pipe list with the moved pipes
            multiplayer.pipe_list = [(p.x, p.y, p.width, p.height)
                                     for p in visible_pipe_rects]

            # Only the host should sync pipe positions periodically
            if multiplayer.is_host and (current_time - last_sync_time) > SYNC_INTERVAL and multiplayer.pipe_list:
                # Send only a small notification that pipes have been updated
                last_sync_time = current_time

            # Draw the pipes
            draw_pipes(visible_pipe_rects)

            # Check collision with pipes
            if not check_collision(visible_pipe_rects):
                game_active = False
                game_state = 'game_over'

        # Draw other players
        for pid, data in multiplayer.players.items():
            if pid != multiplayer.player_id and "position" in data:
                x_pos, y_pos = data["position"]
                color_idx = (int(pid) - 1) % len(PLAYER_COLORS)
                pygame.draw.circle(
                    SCREEN, PLAYER_COLORS[color_idx], (x_pos, y_pos), 20)
                label = font.render(str(pid), True, WHITE)
                SCREEN.blit(label, label.get_rect(center=(x_pos, y_pos)))

        # Draw the player's bird
        SCREEN.blit(bird_image, bird_rect)

        # Display player count
        player_count_surf = font.render(
            f"Players: {len(multiplayer.players)}", True, WHITE)
        SCREEN.blit(player_count_surf, (20, 20))

        # Update score
        score += 0.01
        display_score(score)

    else:
        if not multiplayer.game_started:
            waiting_text = font.render(
                "Waiting for host to start game...", True, WHITE)
            SCREEN.blit(waiting_text, (WIDTH / 2 -
                        waiting_text.get_width() / 2, HEIGHT / 2))

            if multiplayer.is_host:
                start_button = pygame.Rect(
                    WIDTH / 2 - 100, HEIGHT / 2 + 50, 200, 50)
                pygame.draw.rect(SCREEN, GREEN, start_button, border_radius=10)
                start_text = font.render("Start Game", True, BLACK)
                SCREEN.blit(start_text, (WIDTH / 2 -
                            start_text.get_width() / 2, HEIGHT / 2 + 65))

                mouse_pos = pygame.mouse.get_pos()
                mouse_clicked = pygame.mouse.get_pressed()[0]
                if start_button.collidepoint(mouse_pos) and mouse_clicked:
                    if multiplayer.is_host and len(multiplayer.pipe_list) < 100:
                        from Multiplayer import generate_initial_pipes
                        multiplayer.pipe_list = generate_initial_pipes(
                            pipe_count=30, x_gap=350)  # Wider spacing

                    multiplayer.request_game_start()

            player_count = font.render(
                f"Connected Players: {len(multiplayer.players)}", True, WHITE)
            SCREEN.blit(player_count, (WIDTH / 2 -
                        player_count.get_width() / 2, HEIGHT / 2 - 50))

        elif not game_active:
            game_over_text = font.render(
                f"Game Over! Your Score: {int(score)}", True, WHITE)
            SCREEN.blit(game_over_text, (WIDTH / 2 -
                        game_over_text.get_width() / 2, HEIGHT / 2))

            restart_text = font.render(
                "Press ESC to return to menu", True, WHITE)
            SCREEN.blit(restart_text, (WIDTH / 2 -
                        restart_text.get_width() / 2, HEIGHT / 2 + 50))

    return game_state, multiplayer


def is_safe_pipe_placement(existing_pipes, new_pipes):
    """
    Check if the new pipes are placed at a safe distance from existing pipes.

    Args:
        existing_pipes: List of existing pipe tuples (x, y, w, h)
        new_pipes: List of new Pygame Rect objects to be added

    Returns:
        bool: True if the new pipes can be safely added
    """
    if not existing_pipes or not new_pipes:
        return True

    # Get the x-positions of the new pipes
    new_x_positions = set()
    for pipe in new_pipes:
        new_x_positions.add(pipe.x)

    # Check against existing pipes
    for pipe_data in existing_pipes:
        if len(pipe_data) == 4:
            existing_x = pipe_data[0]  # X coordinate
            for new_x in new_x_positions:
                if abs(new_x - existing_x) < MIN_PIPE_SPACING:
                    return False

    return True
