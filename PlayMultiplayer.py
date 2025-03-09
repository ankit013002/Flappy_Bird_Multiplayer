from Network import Multiplayer
from Utilities import *
from GameLogic import *

multiplayer = None  # Will be set when game starts


def play_multiplayer_logic():
    global multiplayer, bird_movement  # Declare global multiplayer

    game_state = 'play_multiplayer'
    game_active = True

    if multiplayer is None:  # Check if multiplayer is initialized
        print("[ERROR] Multiplayer instance is not set!")
        return 'multiplayer menu'  # Redirect to multiplayer menu instead of crashing

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and game_active:
            bird_movement = -6  # Jump

    move_background()

    if game_active:
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        # Send player position to server
        multiplayer.client_connect()  # Ensure connection happens only if valid

        # Draw all players (check multiplayer is valid)
        if multiplayer.players:
            for player_id, pos in multiplayer.players.items():
                # Red birds for other players
                pygame.draw.rect(SCREEN, (255, 0, 0), (pos[0], pos[1], 40, 40))

        SCREEN.blit(bird_image, bird_rect)

        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)

        game_active = check_collision(pipe_list)

    pygame.display.update()
    clock.tick(60)

    return game_state  # Ensure it returns a valid state
