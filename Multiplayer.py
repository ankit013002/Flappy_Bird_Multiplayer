from Button import *
from Utilities import *
from Network import Multiplayer
from InputBox import *
from GameLogic import *
from Constants import *
import pygame
import random
import json

multiplayer_buttons = []
multiplayer = None
host_running = False
host_ip = ""
connection_error = False

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


def multiplayer_menu_logic():
    global multiplayer
    game_state = 'multiplayer menu'

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for btn in multiplayer_buttons:
                if btn.is_hovered(mouse_pos):
                    if btn.text == 'Host':
                        game_state = 'host'
                    elif btn.text == 'Join':
                        game_state = 'join'
                    elif btn.text == 'Back':
                        game_state = 'start'

    multiplayer_menu_screen()
    return game_state


def create_multiplayer_menu():
    """Creates 'Host', 'Join', and 'Back' buttons."""
    multiplayer_buttons.clear()
    button_font = pygame.font.Font(None, 48)
    button_width = 250
    button_height = 60

    button_spacing = 20
    button_bg_color = WHITE
    button_text_color = (0, 0, 0)

    button_texts = ['Host', 'Join', 'Back']
    num_buttons = len(button_texts)
    start_y = (HEIGHT - (num_buttons * button_height +
               (num_buttons - 1) * button_spacing)) / 2

    for i, text in enumerate(button_texts):
        x = (WIDTH - button_width) / 2
        y = start_y + i * (button_height + button_spacing)
        button = Button(text, (x, y), (button_width, button_height),
                        button_font, button_bg_color, button_text_color)
        multiplayer_buttons.append(button)


def multiplayer_menu_screen():
    move_background()

    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("Multiplayer Menu", True, WHITE)
    SCREEN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 100))

    instruction_font = pygame.font.Font(None, 36)
    host_text = instruction_font.render(
        "Host a game for others to join", True, WHITE)
    join_text = instruction_font.render(
        "Join someone else's game", True, WHITE)

    SCREEN.blit(host_text, (WIDTH/2 - host_text.get_width()/2, 180))
    SCREEN.blit(join_text, (WIDTH/2 - join_text.get_width()/2, 220))

    for button in multiplayer_buttons:
        button.draw(SCREEN)


join_buttons = []
host_buttons = []
ready_button = None
ip_input_box = None
player_name_input = None


def host_logic():
    global multiplayer
    game_state = 'host'

    if multiplayer is None or not multiplayer.is_host:
        multiplayer = Multiplayer(is_host=True)
        from Multiplayer import generate_initial_pipes
        multiplayer.pipe_list = generate_initial_pipes(pipe_count=50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if multiplayer:
                multiplayer.cleanup()
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for btn in host_buttons:
                if btn.is_hovered(mouse_pos):
                    if btn.text == "Start Game":
                        if multiplayer.request_game_start():
                            game_state = 'play_multiplayer'
                    elif btn.text == "Back":
                        if multiplayer:
                            multiplayer.stop_server()
                            multiplayer = None
                        game_state = 'multiplayer menu'

    host_screen()
    return game_state, multiplayer


def create_host_screen():
    host_buttons.clear()
    button_font = pygame.font.Font(None, 48)

    start_btn = Button("Start Game", (WIDTH/2 - 125, HEIGHT/2 + 100),
                       (250, 60), button_font, WHITE, BLACK)
    host_buttons.append(start_btn)

    back_btn = Button("Back", (WIDTH/2 - 125, HEIGHT/2 + 180),
                      (250, 60), button_font, WHITE, BLACK)
    host_buttons.append(back_btn)


def host_screen():
    move_background()

    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("Host Game", True, WHITE)
    SCREEN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 100))

    ip_text = font.render(
        f"Your IP address: {multiplayer.host_ip}", True, WHITE)
    SCREEN.blit(ip_text, (WIDTH/2 - ip_text.get_width()/2, HEIGHT/2 - 100))

    instructions = font.render(
        "Share this IP with other players to let them join", True, WHITE)
    SCREEN.blit(instructions, (WIDTH/2 -
                instructions.get_width()/2, HEIGHT/2 - 60))

    if multiplayer:
        player_count = font.render(
            f"Players connected: {multiplayer.get_player_count()}", True, WHITE)
        SCREEN.blit(player_count, (WIDTH/2 -
                    player_count.get_width()/2, HEIGHT/2))

    for btn in host_buttons:
        btn.draw(SCREEN)


def generate_initial_pipes(pipe_count=50, x_start=WIDTH+100, x_gap=300):
    """
    Generates 'pipe_count' random pipes ahead of time, each spaced by x_gap in x-direction.
    Returns a list of (x, y, width, height) tuples.
    """
    from Config import pipe_height_options
    pipe_list = []
    gap = 200

    current_x = x_start
    for _ in range(pipe_count):
        random_pipe_pos = random.choice(pipe_height_options)

        bottom_pipe = (current_x, random_pipe_pos, 80, 800)
        top_pipe = (current_x, random_pipe_pos - gap - 800, 80, 800)

        pipe_list.append(bottom_pipe)
        pipe_list.append(top_pipe)

        current_x += x_gap

    return pipe_list


def join_logic():
    global multiplayer, ip_input_box, connection_error
    game_state = 'join'
    connection_error = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        ip_input_box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for btn in join_buttons:
                if btn.is_hovered(mouse_pos):
                    if btn.text == "Connect":
                        ip = ip_input_box.text.strip()
                        if Multiplayer.is_valid_ip(ip):
                            multiplayer = Multiplayer(
                                is_host=False, host_ip=ip)
                            if multiplayer.player_id is not None:
                                multiplayer.set_ready(True)
                                game_state = 'play_multiplayer'
                            else:
                                connection_error = True
                    elif btn.text == "Back":
                        game_state = 'multiplayer menu'

    if multiplayer is not None and multiplayer.game_started:
        game_state = 'play_multiplayer'  # This line is critical!

    ip_input_box.update()
    join_screen()
    return game_state, multiplayer


def create_join_screen():
    global ip_input_box
    join_buttons.clear()
    button_font = pygame.font.Font(None, 48)

    ip_input_box = InputBox(WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 40, font)

    connect_btn = Button("Connect", (WIDTH / 2 - 125, HEIGHT /
                         2 + 100), (250, 60), button_font, WHITE, BLACK)
    join_buttons.append(connect_btn)

    back_btn = Button("Back", (WIDTH / 2 - 125, HEIGHT / 2 + 180),
                      (250, 60), button_font, WHITE, BLACK)
    join_buttons.append(back_btn)


def join_screen():
    move_background()

    title_font = pygame.font.Font(None, 72)
    title_text = title_font.render("Join Game", True, WHITE)
    SCREEN.blit(title_text, (WIDTH/2 - title_text.get_width()/2, 100))

    instructions = font.render("Enter the host's IP address:", True, WHITE)
    SCREEN.blit(instructions, (WIDTH/2 -
                instructions.get_width()/2, HEIGHT/2 - 160))

    ip_input_box.draw(SCREEN)

    for btn in join_buttons:
        btn.draw(SCREEN)

    if connection_error:
        error_text = font.render(
            "Failed to connect to host. Check IP and try again.", True, (255, 0, 0))
        SCREEN.blit(
            error_text, (WIDTH/2 - error_text.get_width()/2, HEIGHT/2 - 40))


def play_multiplayer_logic(multiplayer):
    global bird_movement

    game_state = 'play_multiplayer'
    game_active = True
    pipe_list = []
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

        if event.type == SPAWNPIPE and multiplayer.is_host and multiplayer.game_started:
            new_pipes = create_pipe()
            pipe_message = {
                "type": "pipe_spawn",
                "id": multiplayer.player_id,
                "pipes": [(pipe.x, pipe.y, pipe.width, pipe.height) for pipe in new_pipes]
            }
            if multiplayer.udp_sock:
                multiplayer.udp_sock.sendto(json.dumps(
                    pipe_message).encode(), (multiplayer.host_ip, PORT))

    move_background()

    if multiplayer.game_started and game_active:
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
            game_active = False

        multiplayer.update_position(bird_rect.x, bird_rect.centery, score)

        if multiplayer.pipe_list:
            pipe_list = []
            for pipe_data in multiplayer.pipe_list:
                if len(pipe_data) == 4:
                    x, y, width, height = pipe_data
                    pipe_list.append(pygame.Rect(x, y, width, height))

        if pipe_list:
            pipe_list = move_pipes(pipe_list)
            draw_pipes(pipe_list)

        if check_collision(pipe_list) == False:
            game_active = False

        for player_id, data in multiplayer.players.items():
            if player_id != multiplayer.player_id and "position" in data:
                pos = data["position"]
                color_idx = (player_id - 1) % len(PLAYER_COLORS)
                color = PLAYER_COLORS[color_idx]

                pygame.draw.circle(SCREEN, color, (pos[0], pos[1]), 20)

                player_num = font.render(str(player_id), True, WHITE)
                num_rect = player_num.get_rect(center=(pos[0], pos[1]))
                SCREEN.blit(player_num, num_rect)

        SCREEN.blit(bird_image, bird_rect)

        player_count = font.render(
            f"Players: {len(multiplayer.players)}", True, WHITE)
        SCREEN.blit(player_count, (20, 20))

        if game_active:
            score += 0.01
            display_score(score)

    else:
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


def generate_initial_pipes(pipe_count=30, x_start=WIDTH+100, x_gap=350):
    """
    Generates 'pipe_count' random pipes ahead of time, each spaced by x_gap in x-direction.
    Returns a list of (x, y, width, height) tuples.

    Args:
        pipe_count: Number of pipe pairs to generate
        x_start: Starting x-position for the first pipe
        x_gap: Minimum horizontal gap between pipes

    Returns:
        List of pipe tuples (x, y, width, height)
    """
    from Config import pipe_height_options
    pipe_list = []
    gap = 200  # Vertical gap between top and bottom pipes

    current_x = x_start
    for _ in range(pipe_count):
        # Choose random height from allowed options
        random_pipe_pos = random.choice(pipe_height_options)

        # Add some randomness to the x-gap to prevent predictable patterns
        # But ensure minimum spacing is maintained
        random_spacing = random.randint(0, 100)
        current_x += x_gap + random_spacing

        # Create bottom pipe
        bottom_pipe = (current_x, random_pipe_pos, 80, 800)
        # Create top pipe
        top_pipe = (current_x, random_pipe_pos - gap - 800, 80, 800)

        pipe_list.append(bottom_pipe)
        pipe_list.append(top_pipe)

    return pipe_list
