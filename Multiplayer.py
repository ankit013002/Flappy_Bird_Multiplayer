from Button import *
from Utilities import *

multiplayer_buttons = []


def multiplayer_menu_logic():
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
                        # Go to Host screen
                        game_state = 'host'
                    elif btn.text == 'Join':
                        # Go to Join screen
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
    button_bg_color = WHITE  # We'll add transparency in the draw
    button_text_color = (0, 0, 0)

    button_texts = ['Host', 'Join']
    num_buttons = len(button_texts)
    total_height = num_buttons * button_height + \
        (num_buttons - 1) * button_spacing
    start_y = (HEIGHT - total_height) / 2

    for i, text in enumerate(button_texts):
        x = (WIDTH - button_width) / 2
        y = start_y + i * (button_height + button_spacing)
        button = Button(text, (x, y), (button_width, button_height),
                        button_font, button_bg_color, button_text_color)
        multiplayer_buttons.append(button)


def multiplayer_menu_screen():
    """Draws the multiplayer menu with 'Host' and 'Join' buttons."""
    move_background()
    draw_centered_text("Multiplayer Menu", 200)

    for button in multiplayer_buttons:
        button.draw(SCREEN)


# In Multiplayer.py, for the host screen:
host_buttons = []

# Same as your existing code ...
host_buttons = []


def host_logic(host_code):
    game_state = 'host'

    # If no host_code has been generated yet, create one
    if host_code == 0:
        # Generate a 6-digit random code (or whatever format you want)
        # You could also generate from e.g. random.randint(100000, 999999)
        # or do a short string code. Here's an example:
        host_code = random.randint(100000, 999999)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for btn in host_buttons:
                if btn.is_hovered(mouse_pos):
                    if btn.text == "Back":
                        # Clear the host_code if you want to reset each time you leave:
                        host_code = 0
                        game_state = 'multiplayer menu'

                    elif btn.text == "Start":
                        # In real networking code, you’d first ensure that
                        # players are actually connected, etc.
                        # If all set, start the game:
                        game_state = 'play_multiplayer'
    host_screen(host_code)
    return game_state, host_code


def create_host_screen():
    host_buttons.clear()
    button_font = pygame.font.Font(None, 48)
    # Start button
    start_btn = Button("Start", (WIDTH/2 - 125, HEIGHT/2 + 20),
                       (250, 60), button_font, WHITE, BLACK)
    host_buttons.append(start_btn)

    # Back button
    back_btn = Button("Back", (WIDTH/2 - 125, HEIGHT/2 + 100),
                      (250, 60), button_font, WHITE, BLACK)
    host_buttons.append(back_btn)


def host_screen(host_code):
    move_background()

    # Show the “Hosting” label
    draw_centered_text("Hosting a Game", 200)

    # Display the code the Host can share
    draw_centered_text(f"Lobby Code: {host_code}", 100)

    # Placeholder: Show a message for connecting players
    # In real code, you’d check how many players have connected, etc.
    draw_centered_text("Waiting for players...", 50)

    # Draw the “Start” and “Back” buttons
    for btn in host_buttons:
        btn.draw(SCREEN)


join_buttons = []


def join_logic(connection_code_input_box, host_code):
    game_state = 'join'
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Let the user type the code
        connection_code_input_box.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for btn in join_buttons:
                if btn.is_hovered(mouse_pos):
                    if btn.text == 'Connect':
                        # Attempt to connect by comparing typed code to host_code
                        try:
                            typed_code = int(
                                connection_code_input_box.text.strip())
                        except ValueError:
                            typed_code = 0
                        if typed_code == host_code:
                            # success -> in real code, you’d attempt to connect via socket
                            # For now, we can just transition to 'play'
                            game_state = 'play'
                        else:
                            # invalid code -> maybe display an error or keep them here
                            print("Invalid code entered!")

                        # Clear the input field after connecting attempt
                        connection_code_input_box.text = ""
                        connection_code_input_box.txt_surface = connection_code_input_box.font.render(
                            "", True, WHITE)

                    elif btn.text == 'Back':
                        game_state = 'multiplayer menu'

    connection_code_input_box.update()
    join_screen(connection_code_input_box)
    return game_state


def create_join_screen():
    join_buttons.clear()
    button_font = pygame.font.Font(None, 48)
    connection_btn = Button('Connect', (WIDTH / 2 - 125, HEIGHT / 2 + 100),
                            (250, 60), button_font, WHITE, BLACK)
    back_btn = Button('Back', (WIDTH / 2 - 125, HEIGHT / 2 + 180),
                      (250, 60), button_font, WHITE, BLACK)
    join_buttons.append(connection_btn)
    join_buttons.append(back_btn)


def join_screen(connection_code_input_box):
    move_background()

    draw_centered_text('Enter code to connect to:', 150)
    connection_code_input_box.draw(SCREEN)

    # Draw buttons
    for btn in join_buttons:
        btn.draw(SCREEN)
