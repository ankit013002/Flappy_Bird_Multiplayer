from Button import *
from Utilities import *
from InputBox import *

buttons = []
player_name_input_box = None
player_name = ''


def start_screen(input_box, pipe_list):
    global player_name_input_box, player_name
    player_name_input_box = input_box
    game_state = 'start'
    game_active = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]:
            input_box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for button in buttons:
                    if button.is_hovered(mouse_pos):
                        match button.text:
                            case 'Play':
                                player_name = input_box.text.strip()
                                if player_name == '':
                                    player_name = 'Player'  # Assign a default name if empty

                                game_state = 'play'
                                game_active = True
                                pipe_list.clear()
                                bird_rect.center = (70, HEIGHT / 2)
                                bird_movement = 0
                                score = 0
                                # Reset input box text
                                input_box.text = ''
                                input_box.txt_surface = input_box.font.render(
                                    input_box.text, True, input_box.color)
                            case 'Multiplayer':
                                game_state = 'multiplayer menu'
                            case 'Host':
                                game_state = 'Host'
                            case 'Join':
                                game_state = 'Join'
                            case 'Leaderboard':
                                game_state = 'leaderboard'
                            case 'Settings':
                                game_state = 'settings'
                            case 'Exit':
                                pygame.quit()
                                sys.exit()
    input_box.update()
    start_screen_layout()

    return game_state, game_active, player_name


def start_screen_layout():
    move_background()

    # Input box
    input_box_width = 300
    input_box_height = 40
    input_box_x = (WIDTH - input_box_width) / 2
    input_box_y = 80

    # Draw the prompt
    prompt_surface = font.render(
        'Enter name to save to leaderboard:', True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH / 2, input_box_y - 30))
    SCREEN.blit(prompt_surface, prompt_rect)

    player_name_input_box.update()
    player_name_input_box.draw(SCREEN)  # Ensure it's redrawn every frame
    # Draw the bird image
    bird_start_rect = bird_image.get_rect(center=(WIDTH / 2, 200))
    SCREEN.blit(bird_image, bird_start_rect)
    # Draw the buttons
    for button in buttons:
        button.draw(SCREEN)


def create_main_screen():
    button_font = pygame.font.Font(None, 48)
    button_width = 250
    button_height = 60

    button_spacing = 20
    button_bg_color = WHITE  # But we will set alpha to make it transparent
    button_text_color = (0, 0, 0)  # Black text

    button_texts = ['Play', 'Multiplayer',
                    'Leaderboard', 'Settings', 'Exit']
    num_buttons = len(button_texts)
    total_height = num_buttons * button_height + \
        (num_buttons - 1) * button_spacing
    start_y = (HEIGHT - total_height) / 2 + 100  # Offset 100 pixels down

    for i, text in enumerate(button_texts):
        x = (WIDTH - button_width) / 2
        y = start_y + i * (button_height + button_spacing)
        button = Button(text, (x, y), (button_width, button_height),
                        button_font, button_bg_color, button_text_color)
        buttons.append(button)
