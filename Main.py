import pygame
import sys
from Adversary import AdversaryBird  # Import the AdversaryBird class
from Config import *
from Button import *
from MainScreen import *
from InputBox import *
from LeaderBoard import *
from Settings import *
from Utilities import *
from Multiplayer import *
from GameLogic import *
from GameOver import *


def main_game_loop():
    global input_box

    # Input box
    score = 0
    pipe_list = []
    host_code = 0
    game_state = 'start'
    connection_code = 0

    connection_code_input_box = InputBox(
        WIDTH / 2 - 150, HEIGHT / 2 - 120, 300, 40, font, str(connection_code))
    input_box = InputBox(x=((WIDTH - 300) / 2), y=80, w=300, h=40, font=font)
    confirm_button = Button('Confirm', (WIDTH / 2 - 125, HEIGHT / 2 + 100),
                            (250, 60), pygame.font.Font(None, 48), WHITE, BLACK)
    connection_button = Button('Connect', (WIDTH / 2 - 125, HEIGHT / 2 + 100),
                               (250, 60), pygame.font.Font(None, 48), WHITE, BLACK)

    while True:
        if game_state == 'start':
            score = 0
            game_state, game_active, player_name = start_screen(
                input_box, pipe_list)

        elif game_state == 'play':
            game_state, score = play_state(pipe_list, score)
            if game_state == 'game_over':
                update_leader_board(player_name, score)

        elif game_state == 'game_over':
            game_state = game_over_screen_logic(score)

        elif game_state == 'leaderboard':
            game_state = leader_board_screen_logic()

        elif game_state == 'multiplayer menu':
            game_state = multiplayer_menu_logic()

        elif game_state == 'host':
            game_state, host_code = host_logic(host_code)
            print(host_code)

        elif game_state == 'join':
            game_state = join_logic(connection_code_input_box, host_code)

        elif game_state == 'play_multiplayer':
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

                if not game_active:
                    game_state = 'game_over'
                    update_leader_board(player_name, score)

                score += 0.01
                display_score(score)
            else:
                game_state = 'game_over'

            # 3) Update the screen and clock
            pygame.display.update()
            clock.tick(60)

        elif game_state == 'settings':
            game_state = settings_logic(confirm_button)

        pygame.display.update()
        clock.tick(60)


def main():

    pygame.init()

    create_main_screen()

    # Create multiplayer menu
    create_multiplayer_menu()
    create_host_screen()
    create_join_screen()

    main_game_loop()


if __name__ == "__main__":
    main()
