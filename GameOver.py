from Utilities import *


def game_over_screen_logic(score):
    game_state = 'game_over'
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            game_state = 'start'
    game_over_screen(score)
    return game_state


def game_over_screen(score):
    move_background()
    game_over_surface = font.render(
        f'Game Over. Your Score: {int(score)}', True, WHITE)
    game_over_rect = game_over_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
    SCREEN.blit(game_over_surface, game_over_rect)
    # Prompt to return to main menu
    prompt_surface = font.render(
        'Press SPACE to return to Main Menu', True, WHITE)
    prompt_rect = prompt_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))
    SCREEN.blit(prompt_surface, prompt_rect)
