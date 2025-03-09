from Button import *
from Utilities import *
from Network import Multiplayer
from InputBox import *

multiplayer_buttons = []
multiplayer = None
host_running = False
host_ip = ""


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
                        if multiplayer is None:  # Prevent multiple instances
                            game_state = 'host'
                            multiplayer = Multiplayer(is_host=True)
                        else:
                            print("[ERROR] Server is already running!")
                    elif btn.text == 'Join':
                        game_state = 'join'

    multiplayer_menu_screen()
    return game_state


def create_multiplayer_menu():
    """Creates 'Host' and 'Join' buttons."""
    multiplayer_buttons.clear()
    button_font = pygame.font.Font(None, 48)
    button_width = 250
    button_height = 60

    button_spacing = 20
    button_bg_color = WHITE
    button_text_color = (0, 0, 0)

    button_texts = ['Host', 'Join']
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
    draw_centered_text("Multiplayer Menu", 200)

    for button in multiplayer_buttons:
        button.draw(SCREEN)


join_buttons = []
host_buttons = []
ip_input_box = None


def host_logic():
    global multiplayer
    game_state = 'host'

    if multiplayer is None:  # Prevent duplicate server instances
        multiplayer = Multiplayer(is_host=True)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for btn in host_buttons:
                if btn.is_hovered(mouse_pos):
                    if btn.text == "Back":
                        game_state = 'multiplayer menu'
                    elif btn.text == "Start":
                        game_state = 'play_multiplayer'

    host_screen()
    return game_state


def create_host_screen():
    host_buttons.clear()
    button_font = pygame.font.Font(None, 48)

    start_btn = Button("Start", (WIDTH/2 - 125, HEIGHT/2 + 20),
                       (250, 60), button_font, WHITE, BLACK)
    host_buttons.append(start_btn)

    back_btn = Button("Back", (WIDTH/2 - 125, HEIGHT/2 + 100),
                      (250, 60), button_font, WHITE, BLACK)
    host_buttons.append(back_btn)


def host_screen():
    move_background()
    draw_centered_text("Hosting a Game", 200)
    draw_centered_text("Waiting for players...", 50)

    for btn in host_buttons:
        btn.draw(SCREEN)


def join_logic():
    global multiplayer  # Ensure multiplayer is updated globally
    game_state = 'join'

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
                        multiplayer = Multiplayer(
                            is_host=False, host_ip=ip_input_box.text.strip()
                        )  # Assign multiplayer instance
                        game_state = 'play_multiplayer'
                    elif btn.text == "Back":
                        game_state = 'multiplayer menu'

    ip_input_box.update()
    join_screen()
    return game_state


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
    draw_centered_text("Enter Host IP:", 150)
    ip_input_box.draw(SCREEN)

    for btn in join_buttons:
        btn.draw(SCREEN)
