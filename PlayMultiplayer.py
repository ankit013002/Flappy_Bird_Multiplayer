from Utilities import *
from GameLogic import *


def play_multiplayer_logic():
    game_state = 'play_multiplayer'
    game_active = False
    # 1) Gather events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Handle inputs for your multiplayer mode (e.g. spacebar flaps)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_active:
            bird_movement = -6

        # Possibly handle pipe spawning if this user is the host,
        # or just ignore if the host is someone else.

    # 2) Update your game logic
    move_background()

    if game_active:
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        SCREEN.blit(bird_image, bird_rect)

        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        game_active = check_collision(pipe_list)

        score += 0.01
    else:
        game_state = 'game_over'

    # 3) Update the screen and clock
    pygame.display.update()
    clock.tick(60)

    return game_state, score
