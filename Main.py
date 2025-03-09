from Button import *
from MainScreen import *
from InputBox import *
from LeaderBoard import *
from Settings import *
from Utilities import *
from Multiplayer import *
from GameLogic import *
from GameOver import *
from PlayMultiplayer import *


def main_game_loop():
    global multiplayer  # Ensure multiplayer persists across game states

    score = 0
    pipe_list = []
    game_state = 'start'

    input_box = InputBox(x=((WIDTH - 300) / 2), y=80, w=300, h=40, font=font)
    confirm_button = Button('Confirm', (WIDTH / 2 - 125, HEIGHT / 2 + 100),
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
            game_state, multiplayer = host_logic()

        elif game_state == 'join':
            game_state, multiplayer = join_logic()  # Ensure multiplayer is set

        elif game_state == 'play_multiplayer':
            if multiplayer is None:
                print("[ERROR] Multiplayer instance is not set in main loop!")
                game_state = 'multiplayer menu'  # Prevent crashing
            else:
                game_state, multiplayer = play_multiplayer_logic(multiplayer)

        elif game_state == 'settings':
            game_state = settings_logic(confirm_button)

        pygame.display.update()
        clock.tick(60)


def main():
    pygame.init()
    create_main_screen()
    create_multiplayer_menu()
    create_host_screen()
    create_join_screen()
    main_game_loop()


if __name__ == "__main__":
    main()
