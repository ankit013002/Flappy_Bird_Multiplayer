from Config import *
from Utilities import *
from InputBox import *


def settings_logic(confirm_button):
    game_state = 'settings'
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if confirm_button.is_hovered(mouse_pos):
                game_state = 'start'
    settings_screen(confirm_button)
    return game_state


def settings_screen(confirm_button):
    move_background()
    confirm_button.draw(SCREEN)
